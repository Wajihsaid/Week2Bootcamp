"""
STAGE 1: NLP Processing Service
Historical text cleaning, normalization, and entity extraction.
"""

import re
import pandas as pd
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np


class HistoricalTextCleaner:
    """Cleans and normalizes historical text with domain-specific rules."""

    def __init__(self):
        # Date normalization patterns
        self.date_patterns = [
            (r'\b(\d+)\s*(BC|BCE|B\.C\.|B\.C\.E\.)\b', r'\1 BCE'),
            (r'\b(\d+)\s*(AD|CE|A\.D\.|C\.E\.)\b', r'\1 CE'),
            (r'\bcirca\s*(\d+)\s*(?:BCE?|CE)?\b', r'circa \1'),
            (r'\b(\d+)\s*-\s*(\d+)\s*(?:century|centuries)\s*(BCE?)?\b', self._format_century_range),
            (r'\b(\d+)(?:st|nd|rd|th)\s+century\s*(BCE?)?\b', self._century_to_years),
            (r'\b(\d+)\s*/\s*(\d+)\s*(?:BCE?|CE)?\b', r'\1-\2'),
        ]

        # Historical name variants → Canonical
        self.historical_names = {
            'hannibal barca': ['hannibal', 'barca', 'hannibal of carthage'],
            'hamilcar barca': ['hamilcar', 'hamilcar the great'],
            'queen dido': ['dido', 'elissa', 'princess elissa', 'dido of carthage'],
            'ibn khaldun': ['abd al-rahman ibn khaldun', 'khaldun'],
            'uqba ibn nafi': ['uqba', 'okba'],
            'kahina': ['dihya', 'al-kahina'],
            'farhat hached': ['farhat', 'hached'],
        }

        # Historical domain terms
        self.historical_terms = {
            'punic', 'carthaginian', 'roman', 'byzantine', 'vandal', 'arab',
            'ottoman', 'hafsid', 'fatimid', 'aghlabid', 'almohad', 'almoravid',
            'berber', 'numidian', 'phoenician', 'islamic', 'crusader',
        }

    def _format_century_range(self, match):
        start, end, era = match.groups()
        era_str = f" {era}" if era else ""
        return f"{start}-{end} century{era_str}"

    def _century_to_years(self, match):
        century, era = match.groups()
        century_num = int(century)
        start_year = (century_num - 1) * 100 + 1
        end_year = century_num * 100
        era_str = f" {era}" if era else " CE"
        return f"{start_year}-{end_year}{era_str}"

    def normalize_dates(self, text: str) -> str:
        """Standardize all date formats in the text."""
        for pattern, replacement in self.date_patterns:
            if callable(replacement):
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            else:
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def normalize_names(self, text: str) -> str:
        """Resolve name variants to canonical forms."""
        text_lower = text.lower()
        for canonical, variants in self.historical_names.items():
            for variant in sorted(variants, key=len, reverse=True):
                if variant.lower() in text_lower:
                    pattern = re.compile(re.escape(variant), re.IGNORECASE)
                    text = pattern.sub(canonical, text)
                    text_lower = text.lower()
        return text

    def clean_text(self, text: str) -> str:
        """Full cleaning pipeline for historical text."""
        if pd.isna(text) or not text:
            return ""

        text = str(text).strip()
        text = self.normalize_dates(text)
        text = self.normalize_names(text)
        text = text.lower()
        text = re.sub(r'[^\w\s\-]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_historical_context(self, text: str) -> Dict[str, Any]:
        """Extract structured historical metadata from text."""
        if not text:
            return {'time_period': None, 'civilization': None, 'key_figures': []}

        context = {
            'time_period': None,
            'civilization': None,
            'key_figures': []
        }

        text_lower = text.lower() if text else ""

        # Time Period Detection
        period_patterns = {
            'prehistoric': r'\b(prehistoric|stone age|neolithic|paleolithic)\b',
            'ancient': r'\b(ancient|classical|antiquity|bce|bc)\b',
            'late antiquity': r'\b(late antiquity|fall of rome|vandal|byzantine)\b',
            'medieval': r'\b(medieval|middle ages|dark ages|hafsid|aghlabid)\b',
            'early modern': r'\b(renaissance|reformation|early modern|ottoman)\b',
            'colonial': r'\b(colonial|protectorate|french rule)\b',
            'modern': r'\b(modern|contemporary|independence|republic)\b'
        }

        for period, pattern in period_patterns.items():
            if re.search(pattern, text_lower):
                context['time_period'] = period
                break

        # Civilization Detection
        civ_patterns = {
            'phoenician': r'\b(phoenician|tyre|sidon)\b',
            'carthaginian': r'\b(carthaginian|punic|carthage)\b',
            'numidian': r'\b(numidian|numidia|berber|amazigh)\b',
            'roman': r'\b(roman|rome|republic|empire|latin)\b',
            'vandal': r'\b(vandal|gaiseric|genseric)\b',
            'byzantine': r'\b(byzantine|eastern roman|constantinople)\b',
            'arab-islamic': r'\b(islamic|muslim|arab|umayyad|abbasid|fatimid)\b',
            'ottoman': r'\b(ottoman|turk|sultan|bey)\b',
            'french colonial': r'\b(french|colonial|protectorate)\b',
            'tunisian': r'\b(tunisian|tunisia|bourguiba|independence)\b'
        }

        for civ, pattern in civ_patterns.items():
            if re.search(pattern, text_lower):
                context['civilization'] = civ
                break

        # Key Figure Detection
        for canonical in self.historical_names:
            if canonical.lower() in text_lower:
                context['key_figures'].append(canonical)

        return context


class HistoricalEntityExtractor:
    """Extract historical entities and create embeddings using BERT."""

    def __init__(self, tokenizer, model, device='cpu'):
        self.tokenizer = tokenizer
        self.model = model
        self.device = device

        # Entity Type Lexicons
        self.entity_lexicons = {
            'PERSON': {
                'hannibal', 'scipio', 'caesar', 'bourguiba', 'dido', 'elissa',
                'king', 'queen', 'emperor', 'sultan', 'pharaoh', 'caliph',
                'ruler', 'leader', 'general', 'commander', 'consul', 'senator',
            },
            'LOCATION': {
                'carthage', 'rome', 'tunis', 'alps', 'zama', 'mediterranean',
                'africa', 'europe', 'asia', 'kairouan', 'mahdia', 'sousse',
                'city', 'empire', 'kingdom', 'province', 'river', 'sea',
            },
            'DATE': {
                'bc', 'bce', 'ad', 'ce', 'century', 'year', 'period', 'era',
                'age', 'ancient', 'medieval', 'modern', 'decade',
            },
            'EVENT': {
                'battle', 'war', 'siege', 'treaty', 'revolution', 'conquest',
                'invasion', 'campaign', 'revolt', 'uprising', 'rebellion',
            },
            'CIVILIZATION': {
                'punic', 'carthaginian', 'roman', 'byzantine', 'vandal',
                'phoenician', 'numidian', 'berber', 'arab', 'islamic',
            }
        }

    def extract_entities(self, text: str, max_length: int = 512) -> List[Dict]:
        """Extract named entities using BERT token analysis."""
        if not text or not text.strip():
            return []

        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            truncation=True,
            padding=True,
            max_length=max_length
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        token_embeddings = outputs.last_hidden_state[0]
        tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])

        entities = []
        current_word = []
        current_indices = []

        special_tokens = {'[CLS]', '[SEP]', '[PAD]', '[UNK]', '<s>', '</s>', '<pad>', '<unk>'}

        for i, token in enumerate(tokens):
            if token in special_tokens:
                if current_word:
                    self._finalize_entity(current_word, current_indices, token_embeddings, entities)
                    current_word = []
                    current_indices = []
                continue

            if token.startswith('##') or token.startswith('Ġ'):
                clean_token = token.lstrip('#').lstrip('Ġ')
                current_word.append(clean_token)
                current_indices.append(i)
            else:
                if current_word:
                    self._finalize_entity(current_word, current_indices, token_embeddings, entities)
                current_word = [token]
                current_indices = [i]

        if current_word:
            self._finalize_entity(current_word, current_indices, token_embeddings, entities)

        # Filter stopwords
        stopwords = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'of', 'and', 'or', 'but', 'is', 'was', 'were'}
        filtered = [ent for ent in entities if len(ent['text']) > 1 and ent['text'].lower() not in stopwords]

        return filtered

    def _finalize_entity(self, word_parts, indices, embeddings, entities_list):
        """Combine subword tokens into a complete entity."""
        word = ''.join(word_parts)
        word = re.sub(r'[^\w\s\-]', '', word).strip()

        if word:
            emb = torch.stack([embeddings[i] for i in indices]).mean(dim=0)
            entity_type = self._classify_entity(word)

            entities_list.append({
                'text': word,
                'type': entity_type,
                'embedding': emb.cpu().numpy()
            })

    def _classify_entity(self, token: str) -> str:
        """Classify entity type using lexicon matching."""
        token_lower = token.lower()

        for entity_type, lexicon in self.entity_lexicons.items():
            if any(term in token_lower for term in lexicon):
                return entity_type

        if token[0].isupper():
            return 'PROPER_NOUN'

        return 'OTHER'

    def create_embedding(self, text: str, method: str = 'mean') -> np.ndarray:
        """Create document-level embedding using Historical BERT."""
        if not text or not text.strip():
            return np.zeros(self.model.config.hidden_size)

        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            truncation=True,
            padding=True,
            max_length=512
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        hidden_states = outputs.last_hidden_state[0]
        attention_mask = inputs['attention_mask'][0].unsqueeze(-1).float()

        if method == 'cls':
            embedding = hidden_states[0]
        elif method == 'mean':
            masked = hidden_states * attention_mask
            embedding = masked.sum(dim=0) / attention_mask.sum(dim=0).clamp(min=1)
        elif method == 'max':
            masked = hidden_states.clone()
            masked[attention_mask.squeeze(-1) == 0] = -1e9
            embedding = masked.max(dim=0)[0]
        else:
            embedding = hidden_states[0]

        return embedding.cpu().numpy()

