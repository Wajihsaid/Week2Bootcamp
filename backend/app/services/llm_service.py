"""
STAGE 3: LLM Service
Role-prompted generation with historical character personas.
"""

import json
from typing import Dict, Any, Optional, AsyncIterator
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from loguru import logger
import httpx

from app.models.characters import HISTORICAL_PERSONAS, get_character_info, detect_character_from_query
from app.services.rag_service import HistoricalRetriever


class LLMService:
    """Manages LLM generation with role prompting."""

    def __init__(self, config):
        self.config = config
        self.generator = None
        self.tokenizer = None
        self.model = None
        self.use_external = config.use_external_llm
        self.is_initialized = False

    def initialize(self):
        """Initialize the LLM."""
        if self.use_external:
            logger.info(f"Using external LLM API: {self.config.external_llm_model}")
            self.is_initialized = True
            return

        if not self.config.llm_model:
            logger.warning("No LLM configured. Running in context-only mode.")
            self.is_initialized = True
            return

        logger.info(f"Loading LLM: {self.config.llm_model}")

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.llm_model)

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.llm_model,
                torch_dtype=torch.float16 if self.config.use_gpu else torch.float32,
                device_map="auto" if self.config.use_gpu else None,
                low_cpu_mem_usage=True
            )

            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=512,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.2,
                pad_token_id=self.tokenizer.pad_token_id
            )

            logger.info(f"LLM loaded successfully: {self.config.llm_model}")
            self.is_initialized = True

        except Exception as e:
            logger.error(f"Failed to load LLM: {e}")
            logger.warning("Falling back to context-only mode")
            self.is_initialized = True

    def _build_prompt(self, query: str, context: str, character_key: str) -> str:
        """Build the full prompt with role instructions and retrieved context."""
        persona = get_character_info(character_key)

        prompt = (
            f"### SYSTEM ###\n"
            f"{persona['system_prompt']}\n\n"
            f"### RETRIEVED HISTORICAL CONTEXT ###\n"
            f"The following information has been retrieved from verified historical sources.\n"
            f"Use ONLY this information to answer the question. "
            f"Do not add any facts not present here.\n\n"
            f"{context}\n\n"
            f"### END OF CONTEXT ###\n\n"
            f"### USER QUESTION ###\n"
            f"{query}\n\n"
            f"### RESPONSE (as {persona['name']}) ###\n"
        )
        return prompt

    async def generate_streaming(
        self,
        query: str,
        context: str,
        character_key: str
    ) -> AsyncIterator[str]:
        """Generate streaming response."""
        prompt = self._build_prompt(query, context, character_key)
        persona = get_character_info(character_key)

        if self.use_external:
            # Use external API with streaming
            async for chunk in self._generate_external_streaming(prompt, persona):
                yield chunk
        elif self.generator:
            # Use local model (non-streaming fallback)
            response = await self._generate_local(prompt, persona)
            yield response
        else:
            # Context-only mode
            yield self._fallback_response(persona, context, query)

    async def generate(
        self,
        query: str,
        context: str,
        character_key: str
    ) -> str:
        """Generate non-streaming response."""
        prompt = self._build_prompt(query, context, character_key)
        persona = get_character_info(character_key)

        if self.use_external:
            return await self._generate_external(prompt, persona)
        elif self.generator:
            return await self._generate_local(prompt, persona)
        else:
            return self._fallback_response(persona, context, query)

    async def _generate_external(self, prompt: str, persona: Dict) -> str:
        """Generate using external LLM API (OpenAI-compatible)."""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.config.external_llm_api_url,
                    headers={
                        "Authorization": f"Bearer {self.config.external_llm_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.config.external_llm_model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 512
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    return self._extract_response(answer, persona['name'])
                else:
                    logger.error(f"External API error: {response.status_code}")
                    return f"Error generating response: {response.status_code}"

        except Exception as e:
            logger.error(f"External generation failed: {e}")
            return f"Error: {str(e)}"

    async def _generate_external_streaming(
        self,
        prompt: str,
        persona: Dict
    ) -> AsyncIterator[str]:
        """Generate streaming response using external API."""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    self.config.external_llm_api_url,
                    headers={
                        "Authorization": f"Bearer {self.config.external_llm_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.config.external_llm_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 512,
                        "stream": True
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            yield f"Error: {str(e)}"

    async def _generate_local(self, prompt: str, persona: Dict) -> str:
        """Generate using local LLM."""
        try:
            output = self.generator(
                prompt,
                max_new_tokens=400,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.2
            )

            generated = output[0]['generated_text']
            answer = self._extract_response(generated, persona['name'])
            return answer

        except Exception as e:
            logger.error(f"Local generation failed: {e}")
            return f"Error generating response: {str(e)}"

    def _extract_response(self, generated: str, character_name: str) -> str:
        """Extract the response part from generated text."""
        response_marker = f"### RESPONSE (as {character_name}) ###"
        if response_marker in generated:
            answer = generated.split(response_marker)[-1].strip()
        else:
            answer = generated.strip()

        # Clean up any trailing prompt artifacts
        cleanup_markers = ['### SYSTEM', '### RETRIEVED', '### USER', '### END', '###']
        for marker in cleanup_markers:
            if marker in answer:
                answer = answer[:answer.index(marker)].strip()

        # Remove repeated lines
        lines = answer.split('\n')
        seen = set()
        unique_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and stripped not in seen:
                seen.add(stripped)
                unique_lines.append(line)

        return '\n'.join(unique_lines)

    def _fallback_response(self, persona: Dict, context: str, query: str) -> str:
        """Generate a structured answer when LLM is unavailable."""
        intros = {
            'Hannibal Barca': "I, Hannibal, commander of Carthage's armies, shall tell you what I know.",
            'Hamilcar Barca': "As the father of Hannibal and defender of Carthage, I share these truths.",
            'Elyssa (Dido)': "As the founder of great Carthage, I shall share what the records reveal.",
            'Uqba ibn Nafi': "In the name of Allah, I share what the chronicles tell.",
            'Kahina': "The spirits of my ancestors speak through these records.",
            'Ibn Khaldoun': "As a student of history and civilization, allow me to present what the sources show.",
            'Abu Zakariya Yahya': "As Sultan of Ifriqiya, I recount what the chronicles preserve.",
            'Kheireddine Pacha': "As Admiral of the Ottoman fleet, I tell you what the records say.",
            'Farhat Hached': "As a fighter for Tunisia's freedom, I share these historical facts.",
        }

        name = persona['name']
        intro = intros.get(name, "Based on the historical records available to me:")

        return (
            f"Speaking as {name}, {persona['title']}:\n\n"
            f"{intro}\n\n"
            f"{context}\n\n"
            f"[Note: This is a direct context retrieval. LLM generation was not available for in-character narration.]"
        )


class HistoricalRAGPipeline:
    """Complete RAG pipeline: retrieval + role-prompted generation."""

    def __init__(
        self,
        retriever: HistoricalRetriever,
        llm_service: LLMService,
        config
    ):
        self.retriever = retriever
        self.llm_service = llm_service
        self.config = config

    async def answer(
        self,
        query: str,
        character_key: Optional[str] = None,
        top_k: int = 5,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate a historically-grounded, in-character answer."""
        result = {
            'query': query,
            'character': None,
            'answer': '',
            'sources': [],
            'entities_detected': []
        }

        # Detect or set character
        if character_key is None:
            character_key = detect_character_from_query(query)

        if character_key not in HISTORICAL_PERSONAS:
            character_key = 'ibn-khaldoun'

        persona = get_character_info(character_key)
        result['character'] = persona['name']

        # Retrieve relevant documents
        logger.info(f"Retrieving top-{top_k} documents for query: {query[:50]}...")
        retrieved = self.retriever.retrieve(
            query, top_k=top_k, use_reranking=True
        )

        if not retrieved:
            no_info_responses = {
                'hannibal': "I, Hannibal, have marched across many lands, yet the records of my scouts contain nothing on this matter.",
                'hamilcar': "The records of my time do not speak of this matter.",
                'elyssa': "The gods have not revealed this knowledge to me, and no Phoenician scroll speaks of it.",
                'uqba': "Allah has not granted me knowledge of this matter.",
                'kahina': "The spirits of my ancestors have not shown me this.",
                'ibn-khaldoun': "My extensive studies of history and civilization have not uncovered information on this topic.",
                'abu-zakariya': "The chronicles of my reign do not speak of this matter.",
                'kheireddine': "The winds of the Mediterranean carry no whisper of this to my ears.",
                'farhat-hached': "In all my years of struggle for our nation, this matter did not cross my path.",
            }
            result['answer'] = no_info_responses.get(
                character_key,
                f"As {persona['name']}, I must confess that the historical records available to me contain no information on this matter."
            )
            return result

        # Prepare sources
        result['sources'] = [
            {
                'event': doc.metadata.get('event_name', 'Unknown'),
                'character': doc.metadata.get('character', 'Unknown'),
                'year': doc.metadata.get('year', 'Unknown'),
                'score': float(score),
                'preview': doc.text[:100]
            }
            for doc, score in retrieved
        ]

        # Format context
        context = self.retriever.format_context(
            retrieved, max_context_length=self.config.max_context_length
        )

        # Generate answer
        if stream:
            # Return async generator for streaming
            async def stream_generator():
                async for chunk in self.llm_service.generate_streaming(query, context, character_key):
                    yield chunk

            result['answer'] = stream_generator()
        else:
            result['answer'] = await self.llm_service.generate(query, context, character_key)

        return result

