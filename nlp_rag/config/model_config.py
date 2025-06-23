"""
Model Configuration Management for NLP & RAG System

This module manages configuration for various models used in the system:
- LLM models (OpenAI, Anthropic, local models)
- Embedding models (OpenAI, sentence-transformers, etc.)
- Retriever models (BM25, Dense retrievers)
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ModelProvider(Enum):
    """Supported model providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"

class EmbeddingModel(Enum):
    """Supported embedding models."""
    OPENAI_ADA002 = "text-embedding-ada-002"
    OPENAI_3_SMALL = "text-embedding-3-small"
    OPENAI_3_LARGE = "text-embedding-3-large"
    SENTENCE_TRANSFORMERS = "sentence-transformers"
    BGE_SMALL = "BAAI/bge-small-en-v1.5"
    BGE_LARGE = "BAAI/bge-large-en-v1.5"

class LLMModel(Enum):
    """Supported LLM models."""
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"

@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    name: str
    provider: ModelProvider
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_params: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.model_params is None:
            self.model_params = {}

@dataclass
class EmbeddingConfig(ModelConfig):
    """Configuration for embedding models."""
    dimension: int = 1536
    max_tokens: int = 8191
    batch_size: int = 100

@dataclass
class LLMConfig(ModelConfig):
    """Configuration for LLM models."""
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

class ModelConfigManager:
    """Manages model configurations for the NLP & RAG system."""
    
    def __init__(self):
        self.embedding_configs = {}
        self.llm_configs = {}
        self._load_default_configs()
    
    def _load_default_configs(self):
        """Load default model configurations."""
        
        # Default embedding configurations
        self.embedding_configs = {
            "openai_ada002": EmbeddingConfig(
                name="text-embedding-ada-002",
                provider=ModelProvider.OPENAI,
                api_key=os.getenv("OPENAI_API_KEY"),
                dimension=1536,
                max_tokens=8191
            ),
            "openai_3_small": EmbeddingConfig(
                name="text-embedding-3-small",
                provider=ModelProvider.OPENAI,
                api_key=os.getenv("OPENAI_API_KEY"),
                dimension=1536,
                max_tokens=8191
            ),
            "openai_3_large": EmbeddingConfig(
                name="text-embedding-3-large",
                provider=ModelProvider.OPENAI,
                api_key=os.getenv("OPENAI_API_KEY"),
                dimension=3072,
                max_tokens=8191
            ),
            "bge_small": EmbeddingConfig(
                name="BAAI/bge-small-en-v1.5",
                provider=ModelProvider.HUGGINGFACE,
                dimension=384,
                max_tokens=512
            ),
            "bge_large": EmbeddingConfig(
                name="BAAI/bge-large-en-v1.5",
                provider=ModelProvider.HUGGINGFACE,
                dimension=1024,
                max_tokens=512
            )
        }
        
        # Default LLM configurations
        self.llm_configs = {
            "gpt_4": LLMConfig(
                name="gpt-4",
                provider=ModelProvider.OPENAI,
                api_key=os.getenv("OPENAI_API_KEY"),
                max_tokens=4096,
                temperature=0.7
            ),
            "gpt_4_turbo": LLMConfig(
                name="gpt-4-turbo-preview",
                provider=ModelProvider.OPENAI,
                api_key=os.getenv("OPENAI_API_KEY"),
                max_tokens=4096,
                temperature=0.7
            ),
            "gpt_3_5_turbo": LLMConfig(
                name="gpt-3.5-turbo",
                provider=ModelProvider.OPENAI,
                api_key=os.getenv("OPENAI_API_KEY"),
                max_tokens=4096,
                temperature=0.7
            ),
            "claude_3_opus": LLMConfig(
                name="claude-3-opus-20240229",
                provider=ModelProvider.ANTHROPIC,
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                max_tokens=4096,
                temperature=0.7
            ),
            "claude_3_sonnet": LLMConfig(
                name="claude-3-sonnet-20240229",
                provider=ModelProvider.ANTHROPIC,
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                max_tokens=4096,
                temperature=0.7
            ),
            "claude_3_haiku": LLMConfig(
                name="claude-3-haiku-20240307",
                provider=ModelProvider.ANTHROPIC,
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                max_tokens=4096,
                temperature=0.7
            )
        }
    
    def get_embedding_config(self, model_name: str) -> Optional[EmbeddingConfig]:
        """Get embedding configuration by name."""
        return self.embedding_configs.get(model_name)
    
    def get_llm_config(self, model_name: str) -> Optional[LLMConfig]:
        """Get LLM configuration by name."""
        return self.llm_configs.get(model_name)
    
    def add_embedding_config(self, name: str, config: EmbeddingConfig):
        """Add a new embedding configuration."""
        self.embedding_configs[name] = config
    
    def add_llm_config(self, name: str, config: LLMConfig):
        """Add a new LLM configuration."""
        self.llm_configs[name] = config
    
    def list_embedding_models(self) -> Dict[str, EmbeddingConfig]:
        """List all available embedding models."""
        return self.embedding_configs.copy()
    
    def list_llm_models(self) -> Dict[str, LLMConfig]:
        """List all available LLM models."""
        return self.llm_configs.copy()
    
    def validate_config(self, config: ModelConfig) -> bool:
        """Validate a model configuration."""
        if not config.name:
            return False
        
        if config.provider in [ModelProvider.OPENAI, ModelProvider.ANTHROPIC]:
            if not config.api_key:
                return False
        
        return True

# Global configuration manager instance
config_manager = ModelConfigManager() 