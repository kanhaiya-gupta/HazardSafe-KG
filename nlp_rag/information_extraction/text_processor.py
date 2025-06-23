"""
Text Processor Module

Provides text preprocessing, analysis, and enhancement capabilities
for hazardous substance documents.
"""

import re
import spacy
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
import json
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ProcessedText:
    """Represents processed text with metadata."""
    original_text: str
    cleaned_text: str
    sentences: List[str]
    tokens: List[str]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TextProcessor:
    """Processes and analyzes text documents."""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize the text processor."""
        try:
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model for text processing: {model_name}")
        except OSError:
            logger.warning(f"Model {model_name} not found. Installing...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", model_name])
            self.nlp = spacy.load(model_name)
        
        # Define text cleaning patterns
        self.cleaning_patterns = {
            'remove_extra_whitespace': r'\s+',
            'remove_special_chars': r'[^\w\s\.\,\;\:\!\?\-\(\)]',
            'normalize_quotes': r'["""'']',
            'normalize_dashes': r'[–—]',
            'remove_line_breaks': r'\n+'
        }
        
        # Define section headers for document structure
        self.section_headers = [
            'hazards', 'safety', 'properties', 'composition', 'storage',
            'handling', 'disposal', 'first aid', 'emergency', 'precautions',
            'risks', 'effects', 'exposure', 'toxicology', 'environmental'
        ]
    
    def preprocess_text(self, text: str) -> ProcessedText:
        """Preprocess text for NLP analysis."""
        # Clean text
        cleaned_text = self._clean_text(text)
        
        # Process with spaCy
        doc = self.nlp(cleaned_text)
        
        # Extract sentences
        sentences = [sent.text.strip() for sent in doc.sents]
        
        # Extract tokens
        tokens = [token.text for token in doc if not token.is_space]
        
        # Create processed text object
        processed = ProcessedText(
            original_text=text,
            cleaned_text=cleaned_text,
            sentences=sentences,
            tokens=tokens,
            metadata={
                'num_sentences': len(sentences),
                'num_tokens': len(tokens),
                'avg_sentence_length': len(tokens) / len(sentences) if sentences else 0
            }
        )
        
        return processed
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        cleaned = text
        
        # Apply cleaning patterns
        for pattern_name, pattern in self.cleaning_patterns.items():
            if pattern_name == 'remove_extra_whitespace':
                cleaned = re.sub(pattern, ' ', cleaned)
            elif pattern_name == 'remove_special_chars':
                cleaned = re.sub(pattern, ' ', cleaned)
            elif pattern_name == 'normalize_quotes':
                cleaned = re.sub(pattern, '"', cleaned)
            elif pattern_name == 'normalize_dashes':
                cleaned = re.sub(pattern, '-', cleaned)
            elif pattern_name == 'remove_line_breaks':
                cleaned = re.sub(pattern, ' ', cleaned)
        
        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()
        
        return cleaned
    
    def extract_document_structure(self, text: str) -> Dict[str, Any]:
        """Extract document structure and sections."""
        structure = {
            'sections': {},
            'section_order': [],
            'metadata': {}
        }
        
        lines = text.split('\n')
        current_section = 'general'
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            section_found = False
            for header in self.section_headers:
                if header.lower() in line.lower():
                    # Save previous section
                    if current_content:
                        structure['sections'][current_section] = '\n'.join(current_content)
                        structure['section_order'].append(current_section)
                    
                    # Start new section
                    current_section = header.lower()
                    current_content = []
                    section_found = True
                    break
            
            if not section_found:
                current_content.append(line)
        
        # Save last section
        if current_content:
            structure['sections'][current_section] = '\n'.join(current_content)
            structure['section_order'].append(current_section)
        
        # Add metadata
        structure['metadata'] = {
            'num_sections': len(structure['sections']),
            'section_names': list(structure['sections'].keys()),
            'total_length': len(text)
        }
        
        return structure
    
    def analyze_text_complexity(self, text: str) -> Dict[str, Any]:
        """Analyze text complexity and readability."""
        doc = self.nlp(text)
        
        # Calculate basic statistics
        num_sentences = len(list(doc.sents))
        num_tokens = len([token for token in doc if not token.is_space])
        num_words = len([token for token in doc if token.is_alpha])
        num_unique_words = len(set([token.text.lower() for token in doc if token.is_alpha]))
        
        # Calculate average word length
        word_lengths = [len(token.text) for token in doc if token.is_alpha]
        avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0
        
        # Calculate average sentence length
        avg_sentence_length = num_words / num_sentences if num_sentences > 0 else 0
        
        # Calculate lexical diversity (type-token ratio)
        lexical_diversity = num_unique_words / num_words if num_words > 0 else 0
        
        # Calculate Flesch Reading Ease (simplified)
        # Formula: 206.835 - (1.015 × avg_sentence_length) - (84.6 × avg_syllables_per_word)
        # For simplicity, we'll estimate syllables per word
        syllables = sum(self._count_syllables(token.text) for token in doc if token.is_alpha)
        avg_syllables_per_word = syllables / num_words if num_words > 0 else 0
        
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        flesch_score = max(0, min(100, flesch_score))  # Clamp between 0 and 100
        
        complexity_analysis = {
            'basic_stats': {
                'num_sentences': num_sentences,
                'num_tokens': num_tokens,
                'num_words': num_words,
                'num_unique_words': num_unique_words
            },
            'averages': {
                'avg_word_length': round(avg_word_length, 2),
                'avg_sentence_length': round(avg_sentence_length, 2),
                'avg_syllables_per_word': round(avg_syllables_per_word, 2)
            },
            'readability': {
                'lexical_diversity': round(lexical_diversity, 3),
                'flesch_reading_ease': round(flesch_score, 1),
                'readability_level': self._get_readability_level(flesch_score)
            }
        }
        
        return complexity_analysis
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified approach)."""
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        on_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not on_vowel:
                count += 1
            on_vowel = is_vowel
        
        # Handle edge cases
        if word.endswith('e'):
            count -= 1
        if count == 0:
            count = 1
        
        return count
    
    def _get_readability_level(self, flesch_score: float) -> str:
        """Get readability level based on Flesch score."""
        if flesch_score >= 90:
            return "Very Easy"
        elif flesch_score >= 80:
            return "Easy"
        elif flesch_score >= 70:
            return "Fairly Easy"
        elif flesch_score >= 60:
            return "Standard"
        elif flesch_score >= 50:
            return "Fairly Difficult"
        elif flesch_score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def extract_key_phrases(self, text: str, num_phrases: int = 10) -> List[Dict[str, Any]]:
        """Extract key phrases from text using NLP techniques."""
        doc = self.nlp(text)
        phrases = []
        
        # Extract noun phrases
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) >= 2:  # At least 2 words
                phrases.append({
                    'text': chunk.text,
                    'type': 'noun_phrase',
                    'root': chunk.root.text,
                    'length': len(chunk.text.split())
                })
        
        # Extract verb phrases
        for token in doc:
            if token.pos_ == 'VERB' and token.dep_ in ['ROOT', 'ccomp', 'xcomp']:
                # Get verb phrase
                verb_phrase = self._get_verb_phrase(token)
                if verb_phrase and len(verb_phrase.split()) >= 2:
                    phrases.append({
                        'text': verb_phrase,
                        'type': 'verb_phrase',
                        'root': token.text,
                        'length': len(verb_phrase.split())
                    })
        
        # Sort by length and importance
        phrases.sort(key=lambda x: (x['length'], x['type'] == 'noun_phrase'), reverse=True)
        
        # Return top phrases
        return phrases[:num_phrases]
    
    def _get_verb_phrase(self, verb_token) -> str:
        """Get the complete verb phrase for a verb token."""
        phrase_tokens = [verb_token]
        
        # Add direct objects
        for child in verb_token.children:
            if child.dep_ in ['dobj', 'pobj']:
                phrase_tokens.append(child)
        
        # Add prepositional phrases
        for child in verb_token.children:
            if child.dep_ == 'prep':
                phrase_tokens.append(child)
                for grandchild in child.children:
                    phrase_tokens.append(grandchild)
        
        # Sort tokens by position
        phrase_tokens.sort(key=lambda x: x.i)
        
        return ' '.join([token.text for token in phrase_tokens])
    
    def extract_technical_terms(self, text: str) -> List[Dict[str, Any]]:
        """Extract technical terms and jargon from text."""
        doc = self.nlp(text)
        technical_terms = []
        
        # Define technical term patterns
        technical_patterns = [
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # Multi-word capitalized terms
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b[a-z]+\-[a-z]+\b',  # Hyphenated terms
            r'\b\d+[A-Za-z]+\b',  # Terms with numbers
        ]
        
        # Extract using patterns
        for pattern in technical_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                term = match.group()
                technical_terms.append({
                    'term': term,
                    'pattern': pattern,
                    'position': match.span(),
                    'frequency': text.count(term)
                })
        
        # Extract using spaCy POS patterns
        for token in doc:
            # Look for technical noun phrases
            if (token.pos_ == 'NOUN' and 
                token.is_title and 
                len(token.text) > 3):
                technical_terms.append({
                    'term': token.text,
                    'pattern': 'title_case_noun',
                    'position': (token.idx, token.idx + len(token.text)),
                    'frequency': text.count(token.text)
                })
        
        # Remove duplicates and sort by frequency
        unique_terms = {}
        for term in technical_terms:
            term_text = term['term']
            if term_text not in unique_terms or term['frequency'] > unique_terms[term_text]['frequency']:
                unique_terms[term_text] = term
        
        return sorted(unique_terms.values(), key=lambda x: x['frequency'], reverse=True)
    
    def create_text_summary(self, text: str) -> Dict[str, Any]:
        """Create a comprehensive summary of text analysis."""
        # Preprocess text
        processed = self.preprocess_text(text)
        
        # Analyze complexity
        complexity = self.analyze_text_complexity(text)
        
        # Extract structure
        structure = self.extract_document_structure(text)
        
        # Extract key phrases
        key_phrases = self.extract_key_phrases(text)
        
        # Extract technical terms
        technical_terms = self.extract_technical_terms(text)
        
        summary = {
            'text_info': {
                'original_length': len(text),
                'cleaned_length': len(processed.cleaned_text),
                'num_sentences': processed.metadata['num_sentences'],
                'num_tokens': processed.metadata['num_tokens']
            },
            'complexity_analysis': complexity,
            'document_structure': structure,
            'key_phrases': key_phrases[:5],  # Top 5 phrases
            'technical_terms': technical_terms[:10],  # Top 10 terms
            'processing_metadata': {
                'processing_time': 'N/A',  # Could be added if timing is needed
                'spacy_model': 'en_core_web_sm'
            }
        }
        
        return summary
    
    def export_analysis(self, analysis: Dict[str, Any], filepath: str) -> None:
        """Export text analysis to JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(analysis, f, indent=2)
            logger.info(f"Text analysis exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export text analysis: {e}")
    
    def batch_process_texts(self, texts: List[str]) -> List[ProcessedText]:
        """Process multiple texts in batch."""
        processed_texts = []
        
        for i, text in enumerate(texts):
            try:
                processed = self.preprocess_text(text)
                processed.metadata['batch_index'] = i
                processed_texts.append(processed)
                logger.info(f"Processed text {i+1}/{len(texts)}")
            except Exception as e:
                logger.error(f"Failed to process text {i+1}: {e}")
                # Create empty processed text for failed processing
                processed = ProcessedText(
                    original_text=text,
                    cleaned_text="",
                    sentences=[],
                    tokens=[],
                    metadata={'error': str(e), 'batch_index': i}
                )
                processed_texts.append(processed)
        
        return processed_texts 