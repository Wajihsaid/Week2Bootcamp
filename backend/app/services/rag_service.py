"""
STAGE 2: RAG Service
Document chunking, embedding generation, FAISS indexing, and retrieval.
"""

import os
import pickle
import pandas as pd
import numpy as np
import faiss
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from sentence_transformers import SentenceTransformer
from loguru import logger

from app.services.nlp_processor import HistoricalTextCleaner, HistoricalEntityExtractor


@dataclass
class HistoricalDocument:
    """A single RAG-ready document chunk with metadata."""
    doc_id: str
    text: str
    raw_text: str
    embedding: Optional[np.ndarray] = None
    metadata: Dict = field(default_factory=dict)


class RAGDocumentProcessor:
    """Process dataset into RAG-ready document chunks."""

    def __init__(self, cleaner: HistoricalTextCleaner):
        self.cleaner = cleaner

    def create_documents(
        self,
        df: pd.DataFrame,
        chunk_size: int = 250,
        chunk_overlap: int = 40
    ) -> List[HistoricalDocument]:
        """Convert DataFrame rows into overlapping, metadata-enriched chunks."""
        documents = []
        doc_counter = 0

        # Detect available columns
        text_cols = [c for c in ['description', 'details', 'summary', 'text', 'rag_document'] if c in df.columns]
        name_col = next((c for c in ['name_of_incident', 'event_name', 'name', 'title'] if c in df.columns), None)
        char_col = next((c for c in ['historical_character', 'character', 'figure', 'person'] if c in df.columns), None)
        year_col = next((c for c in ['year', 'date', 'period', 'year_display'] if c in df.columns), None)

        logger.info(f"Processing {len(df)} rows with columns: text={text_cols}, name={name_col}, char={char_col}, year={year_col}")

        for idx, row in df.iterrows():
            # Build raw text
            parts = []

            event_name = str(row.get(name_col, '')) if name_col else ''
            character = str(row.get(char_col, 'Unknown')) if char_col else 'Unknown'
            year = str(row.get(year_col, 'Unknown')) if year_col else 'Unknown'

            if event_name and event_name != 'nan':
                parts.append(f"Event: {event_name}.")

            for tc in text_cols:
                val = str(row.get(tc, ''))
                if val and val != 'nan':
                    parts.append(val)

            raw_text = ' '.join(parts).strip()
            if not raw_text:
                continue

            # Clean text
            cleaned = self.cleaner.clean_text(raw_text)
            if not cleaned:
                continue

            # Extract context
            context = self.cleaner.extract_historical_context(raw_text)

            # Metadata
            meta = {
                'event_name': event_name if event_name != 'nan' else 'Unknown',
                'character': character if character != 'nan' else 'Unknown',
                'year': year if year != 'nan' else 'Unknown',
                'row_index': idx,
                'time_period': context.get('time_period'),
                'civilization': context.get('civilization'),
                'key_figures': context.get('key_figures', []),
            }

            # Chunk the text
            words = cleaned.split()

            if len(words) <= chunk_size:
                # Single chunk
                doc = HistoricalDocument(
                    doc_id=f"doc_{doc_counter:04d}",
                    text=cleaned,
                    raw_text=raw_text[:500],
                    metadata=meta
                )
                documents.append(doc)
                doc_counter += 1
            else:
                # Multiple overlapping chunks
                start = 0
                chunk_idx = 0
                while start < len(words):
                    end = min(start + chunk_size, len(words))
                    chunk_text = ' '.join(words[start:end])

                    chunk_meta = meta.copy()
                    chunk_meta['chunk_index'] = chunk_idx

                    doc = HistoricalDocument(
                        doc_id=f"doc_{doc_counter:04d}_chunk_{chunk_idx}",
                        text=chunk_text,
                        raw_text=raw_text[:500],
                        metadata=chunk_meta
                    )
                    documents.append(doc)
                    doc_counter += 1
                    chunk_idx += 1

                    start += chunk_size - chunk_overlap
                    if end >= len(words):
                        break

        logger.info(f"Created {len(documents)} document chunks")
        return documents


class HistoricalRetriever:
    """Retrieve relevant historical documents using FAISS."""

    def __init__(
        self,
        faiss_index,
        documents: List[HistoricalDocument],
        embedder: SentenceTransformer,
        extractor: HistoricalEntityExtractor,
        cleaner: HistoricalTextCleaner,
        bert_rerank_weight: float = 0.3
    ):
        self.index = faiss_index
        self.documents = documents
        self.embedder = embedder
        self.extractor = extractor
        self.cleaner = cleaner
        self.bert_weight = bert_rerank_weight

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        use_reranking: bool = True,
        character_filter: Optional[str] = None,
        min_score: float = 0.0
    ) -> List[Tuple[HistoricalDocument, float]]:
        """Retrieve top-k relevant documents for a query."""
        # Clean the query
        cleaned_query = self.cleaner.clean_text(query)

        # FAISS retrieval (fetch more candidates for re-ranking)
        candidates_k = top_k * 4 if use_reranking else top_k

        query_embedding = self.embedder.encode(
            [cleaned_query],
            normalize_embeddings=True
        ).astype('float32')

        scores, indices = self.index.search(query_embedding, candidates_k)

        candidates = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documents) and score >= min_score:
                doc = self.documents[idx]

                # Apply character filter if specified
                if character_filter:
                    doc_char = doc.metadata.get('character', '').lower()
                    if character_filter.lower() not in doc_char:
                        continue

                candidates.append((doc, float(score)))

        if not candidates:
            return []

        # Re-rank with Historical BERT
        if use_reranking and len(candidates) > 1:
            query_bert_emb = self.extractor.create_embedding(cleaned_query[:500], method='mean')

            reranked = []
            for doc, faiss_score in candidates:
                doc_bert_emb = self.extractor.create_embedding(doc.text[:500], method='mean')

                bert_sim = np.dot(query_bert_emb, doc_bert_emb) / (
                    np.linalg.norm(query_bert_emb) * np.linalg.norm(doc_bert_emb) + 1e-8
                )

                # Combined score
                combined = (1 - self.bert_weight) * faiss_score + self.bert_weight * bert_sim
                reranked.append((doc, float(combined)))

            reranked.sort(key=lambda x: x[1], reverse=True)
            return reranked[:top_k]

        return candidates[:top_k]

    def format_context(
        self,
        results: List[Tuple[HistoricalDocument, float]],
        max_context_length: int = 2000
    ) -> str:
        """Format retrieved documents into a context string for the LLM."""
        if not results:
            return "No relevant historical information found."

        context_parts = []
        total_length = 0

        for i, (doc, score) in enumerate(results, 1):
            meta = doc.metadata

            entry = (
                f"[Source {i} | Relevance: {score:.3f}]\n"
                f"Event: {meta.get('event_name', 'Unknown')}\n"
                f"Historical Figure: {meta.get('character', 'Unknown')}\n"
                f"Year: {meta.get('year', 'Unknown')}\n"
                f"Period: {meta.get('time_period', 'Unknown')}\n"
                f"Civilization: {meta.get('civilization', 'Unknown')}\n"
                f"Content: {doc.text}\n"
            )

            if total_length + len(entry) > max_context_length:
                break

            context_parts.append(entry)
            total_length += len(entry)

        return "\n---\n".join(context_parts)


class RAGSystem:
    """Complete RAG system manager."""

    def __init__(self, config):
        self.config = config
        self.embedder = None
        self.cleaner = None
        self.extractor = None
        self.documents = []
        self.faiss_index = None
        self.retriever = None
        self.is_initialized = False

    def initialize(
        self,
        hist_tokenizer,
        hist_model,
        device: str = 'cpu'
    ):
        """Initialize all RAG components."""
        logger.info("Initializing RAG System...")

        # Initialize components
        logger.info(f"Loading sentence embedder: {self.config.embedding_model}")
        self.embedder = SentenceTransformer(self.config.embedding_model)

        self.cleaner = HistoricalTextCleaner()
        self.extractor = HistoricalEntityExtractor(hist_tokenizer, hist_model, device)

        # Load or create documents
        dataset_path = self.config.dataset_path
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")

        logger.info(f"Loading dataset from {dataset_path}")
        df = pd.read_csv(dataset_path, encoding='utf-8')
        logger.info(f"Loaded {len(df)} rows")

        # Check for cached processed documents
        cache_path = os.path.join(self.config.faiss_index_path, 'documents.pkl')
        os.makedirs(self.config.faiss_index_path, exist_ok=True)

        if os.path.exists(cache_path):
            logger.info("Loading cached documents...")
            with open(cache_path, 'rb') as f:
                self.documents = pickle.load(f)
            logger.info(f"Loaded {len(self.documents)} cached documents")
        else:
            # Create documents
            logger.info("Creating document chunks...")
            processor = RAGDocumentProcessor(self.cleaner)
            self.documents = processor.create_documents(
                df,
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap
            )

            # Generate embeddings
            logger.info("Generating embeddings...")
            all_texts = [doc.text for doc in self.documents]
            embeddings = self.embedder.encode(
                all_texts,
                batch_size=64,
                show_progress_bar=True,
                normalize_embeddings=True
            ).astype('float32')

            for i, doc in enumerate(self.documents):
                doc.embedding = embeddings[i]

            # Cache documents
            logger.info(f"Caching documents to {cache_path}")
            with open(cache_path, 'wb') as f:
                pickle.dump(self.documents, f)

        # Build FAISS index
        logger.info("Building FAISS index...")
        embedding_matrix = np.vstack([doc.embedding for doc in self.documents])
        dimension = embedding_matrix.shape[1]

        self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner Product = Cosine (normalized)
        self.faiss_index.add(embedding_matrix)

        logger.info(f"FAISS index built: {self.faiss_index.ntotal} vectors, dim={dimension}")

        # Create retriever
        self.retriever = HistoricalRetriever(
            faiss_index=self.faiss_index,
            documents=self.documents,
            embedder=self.embedder,
            extractor=self.extractor,
            cleaner=self.cleaner,
            bert_rerank_weight=self.config.bert_rerank_weight
        )

        self.is_initialized = True
        logger.info("RAG System initialized successfully!")

    def get_retriever(self) -> HistoricalRetriever:
        """Get the retriever instance."""
        if not self.is_initialized:
            raise RuntimeError("RAG system not initialized. Call initialize() first.")
        return self.retriever

    def get_document_count(self) -> int:
        """Get total document count."""
        return len(self.documents)

