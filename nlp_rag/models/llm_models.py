"""
LLM Model Implementations for NLP & RAG System

This module provides implementations for various Large Language Models:
- OpenAI GPT models
- Anthropic Claude models
- Local models (optional)
"""

import logging
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
import asyncio

from ..config.model_config import LLMConfig, ModelProvider, config_manager

logger = logging.getLogger(__name__)

class BaseLLM(ABC):
    """Abstract base class for LLM implementations."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the LLM model."""
        pass
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text from a prompt."""
        pass
    
    @abstractmethod
    async def generate_stream(self, prompt: str, **kwargs):
        """Generate text stream from a prompt."""
        pass

class OpenAILLM(BaseLLM):
    """OpenAI LLM implementation."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = None
    
    async def initialize(self) -> bool:
        """Initialize OpenAI client."""
        try:
            import openai
            self.client = openai.AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url
            )
            self.initialized = True
            logger.info(f"OpenAI LLM initialized: {self.config.name}")
            return True
        except ImportError:
            logger.error("OpenAI library not installed")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI LLM: {e}")
            return False
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using OpenAI API."""
        if not self.initialized:
            return {"error": "LLM not initialized"}
        
        try:
            # Merge config with kwargs
            params = {
                "model": self.config.name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "frequency_penalty": self.config.frequency_penalty,
                "presence_penalty": self.config.presence_penalty,
                **kwargs
            }
            
            response = await self.client.chat.completions.create(**params)
            
            return {
                "success": True,
                "text": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason
            }
            
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            return {"error": str(e)}
    
    async def generate_stream(self, prompt: str, **kwargs):
        """Generate streaming text using OpenAI API."""
        if not self.initialized:
            yield {"error": "LLM not initialized"}
            return
        
        try:
            params = {
                "model": self.config.name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "stream": True,
                **kwargs
            }
            
            async for chunk in await self.client.chat.completions.create(**params):
                if chunk.choices[0].delta.content:
                    yield {
                        "success": True,
                        "text": chunk.choices[0].delta.content,
                        "model": chunk.model
                    }
                    
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            yield {"error": str(e)}

class AnthropicLLM(BaseLLM):
    """Anthropic Claude LLM implementation."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = None
    
    async def initialize(self) -> bool:
        """Initialize Anthropic client."""
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(
                api_key=self.config.api_key,
                base_url=self.config.base_url
            )
            self.initialized = True
            logger.info(f"Anthropic LLM initialized: {self.config.name}")
            return True
        except ImportError:
            logger.error("Anthropic library not installed")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic LLM: {e}")
            return False
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using Anthropic API."""
        if not self.initialized:
            return {"error": "LLM not initialized"}
        
        try:
            params = {
                "model": self.config.name,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "messages": [{"role": "user", "content": prompt}],
                **kwargs
            }
            
            response = await self.client.messages.create(**params)
            
            return {
                "success": True,
                "text": response.content[0].text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                },
                "model": response.model,
                "stop_reason": response.stop_reason
            }
            
        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            return {"error": str(e)}
    
    async def generate_stream(self, prompt: str, **kwargs):
        """Generate streaming text using Anthropic API."""
        if not self.initialized:
            yield {"error": "LLM not initialized"}
            return
        
        try:
            params = {
                "model": self.config.name,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True,
                **kwargs
            }
            
            async with self.client.messages.stream(**params) as stream:
                async for chunk in stream:
                    if chunk.type == "content_block_delta":
                        yield {
                            "success": True,
                            "text": chunk.delta.text,
                            "model": chunk.model
                        }
                        
        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            yield {"error": str(e)}

class LLMManager:
    """Manager for LLM models."""
    
    def __init__(self):
        self.models = {}
        self.default_model = None
    
    async def initialize_model(self, model_name: str) -> bool:
        """Initialize a specific LLM model."""
        config = config_manager.get_llm_config(model_name)
        if not config:
            logger.error(f"LLM config not found: {model_name}")
            return False
        
        if config.provider == ModelProvider.OPENAI:
            model = OpenAILLM(config)
        elif config.provider == ModelProvider.ANTHROPIC:
            model = AnthropicLLM(config)
        else:
            logger.error(f"Unsupported LLM provider: {config.provider}")
            return False
        
        success = await model.initialize()
        if success:
            self.models[model_name] = model
            if not self.default_model:
                self.default_model = model_name
            logger.info(f"LLM model initialized: {model_name}")
        
        return success
    
    async def generate(self, prompt: str, model_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate text using specified or default model."""
        model_name = model_name or self.default_model
        if not model_name:
            return {"error": "No default model set"}
        
        model = self.models.get(model_name)
        if not model:
            # Try to initialize the model
            success = await self.initialize_model(model_name)
            if not success:
                return {"error": f"Failed to initialize model: {model_name}"}
            model = self.models[model_name]
        
        return await model.generate(prompt, **kwargs)
    
    async def generate_stream(self, prompt: str, model_name: Optional[str] = None, **kwargs):
        """Generate streaming text using specified or default model."""
        model_name = model_name or self.default_model
        if not model_name:
            yield {"error": "No default model set"}
            return
        
        model = self.models.get(model_name)
        if not model:
            # Try to initialize the model
            success = await self.initialize_model(model_name)
            if not success:
                yield {"error": f"Failed to initialize model: {model_name}"}
                return
            model = self.models[model_name]
        
        async for chunk in model.generate_stream(prompt, **kwargs):
            yield chunk
    
    def set_default_model(self, model_name: str):
        """Set the default LLM model."""
        self.default_model = model_name
    
    def get_available_models(self) -> List[str]:
        """Get list of available model names."""
        return list(self.models.keys())
    
    def get_model_configs(self) -> Dict[str, LLMConfig]:
        """Get all available model configurations."""
        return config_manager.list_llm_models()

# Global LLM manager instance
llm_manager = LLMManager() 