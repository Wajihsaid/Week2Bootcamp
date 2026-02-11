"""
Chat Router - Historical Character Conversations
Compatible with Supabase Edge Functions format
"""

import json
from typing import AsyncIterator
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from loguru import logger

from app.models.schemas import ChatRequest, ChatResponse
from app.config import get_settings

router = APIRouter()


def get_rag_pipeline(request: Request):
    """Get RAG pipeline from app state."""
    from app.main import get_app_state
    app_state = get_app_state()
    rag_pipeline = app_state.get("rag_pipeline")

    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")

    return rag_pipeline


async def stream_sse_response(query: str, character_id: str, rag_pipeline) -> AsyncIterator[str]:
    """Stream response in Server-Sent Events format (compatible with frontend)."""
    try:
        result = await rag_pipeline.answer(
            query=query,
            character_key=character_id,
            top_k=5,
            stream=True
        )

        # Get the async generator
        answer_generator = result['answer']

        # Stream chunks in SSE format
        async for chunk in answer_generator:
            # Format as SSE compatible with OpenAI
            sse_data = {
                "choices": [
                    {
                        "delta": {
                            "content": chunk
                        }
                    }
                ]
            }
            yield f"data: {json.dumps(sse_data)}\n\n"

        # Send done signal
        yield "data: [DONE]\n\n"

    except Exception as e:
        logger.error(f"Streaming error: {e}")
        error_data = {"error": str(e)}
        yield f"data: {json.dumps(error_data)}\n\n"


@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, chat_request: ChatRequest):
    """
    Chat with a historical character using RAG.

    Compatible with Supabase Edge Functions format:
    - Accepts messages array with role/content
    - Supports characterId for persona selection
    - Supports streaming responses
    """
    try:
        rag_pipeline = get_rag_pipeline(request)

        # Extract the last user message
        user_messages = [msg for msg in chat_request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")

        last_message = user_messages[-1].content
        character_id = chat_request.characterId

        logger.info(f"Chat request: character={character_id}, query={last_message[:50]}...")

        # Handle streaming vs non-streaming
        if chat_request.stream:
            # Return streaming response
            return StreamingResponse(
                stream_sse_response(last_message, character_id, rag_pipeline),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        else:
            # Return complete response
            result = await rag_pipeline.answer(
                query=last_message,
                character_key=character_id,
                top_k=5,
                stream=False
            )

            return ChatResponse(
                answer=result['answer'],
                character=result['character'],
                sources=result.get('sources', []),
                entities_detected=result.get('entities_detected', [])
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/characters")
async def list_characters():
    """List all available historical characters."""
    from app.models.characters import HISTORICAL_PERSONAS

    characters = []
    for char_id, persona in HISTORICAL_PERSONAS.items():
        characters.append({
            "id": char_id,
            "name": persona["name"],
            "title": persona["title"],
            "era": persona["era"]
        })

    return {"characters": characters}


@router.get("/characters/{character_id}")
async def get_character(character_id: str):
    """Get details about a specific character."""
    from app.models.characters import HISTORICAL_PERSONAS

    if character_id not in HISTORICAL_PERSONAS:
        raise HTTPException(status_code=404, detail="Character not found")

    persona = HISTORICAL_PERSONAS[character_id]

    return {
        "id": character_id,
        "name": persona["name"],
        "title": persona["title"],
        "era": persona["era"],
        "greeting": f"I am {persona['name']}, {persona['title']}. ({persona['era']})"
    }

