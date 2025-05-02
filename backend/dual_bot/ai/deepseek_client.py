"""
DeepSeek client module for the Dual Bot trading system.
Provides access to DeepSeek models via OpenRouter.
"""

import os
import json
import logging
import time
import openai
from typing import Dict, Any, List, Optional

class DeepSeekClient:
    """Client for accessing DeepSeek models via OpenRouter."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the DeepSeek client using OpenRouter.
        
        Args:
            config: Configuration dictionary containing DeepSeek settings
        """
        self.logger = logging.getLogger(__name__)
        self.config = config.get('deepseek', {})
        
        # Set up OpenRouter client for DeepSeek
        # Try to get API key from environment first, then config
        api_key = os.getenv('OPENROUTER_API_KEY') or self.config.get('api_key')
        if not api_key:
            # Fall back to direct DeepSeek API key if available
            api_key = os.getenv('DEEPSEEK_API_KEY') or self.config.get('direct_api_key')
            
        if not api_key:
            raise ValueError("OpenRouter API key not found in environment or config")
        
        # Validate API key format for OpenRouter
        if not (api_key.startswith("sk-or") or api_key.startswith("sk-proj")):
            self.logger.warning("Unusual OpenRouter API key format. OpenRouter keys typically start with 'sk-or-' or 'sk-proj-'")
        
        # Initialize the OpenAI client with OpenRouter base URL
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "https://ai-trading-bot.com",  # Your site URL
                "X-Title": "AI Trading Bot"                    # Your site name
            }
        )
        
        # Get model from config or environment
        self.model = os.getenv('DEEPSEEK_MODEL') or self.config.get('model', 'deepseek/deepseek-coder')
        
        # Log the model being used
        self.logger.info(f"DeepSeek client initialized with model: {self.model}")
        
        # Load settings
        self.max_tokens = self.config.get('max_tokens', 2048)
        self.temperature = self.config.get('temperature', 0.7)
        self.retry_attempts = self.config.get('retry_attempts', 3)
        self.retry_delay_seconds = self.config.get('retry_delay_seconds', 2)
        
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text from DeepSeek model.
        
        Args:
            prompt: The user prompt to send to the model
            system_prompt: Optional system prompt for context
            
        Returns:
            Generated text response
        """
        try:
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Debug log
            self.logger.info(f"Making request to DeepSeek via OpenRouter with model: {self.model}")
            
            # Make API call with retries
            for attempt in range(self.retry_attempts):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature
                    )
                    
                    # Log successful call
                    self.logger.info(f"DeepSeek API call successful using model: {response.model}")
                    
                    # Return generated text
                    return response.choices[0].message.content
                    
                except openai.RateLimitError as e:
                    self.logger.warning(f"Rate limit exceeded: {str(e)}")
                    if attempt == self.retry_attempts - 1:
                        raise
                    time.sleep(self.retry_delay_seconds * (attempt + 1))  # Exponential backoff
                
                except openai.APIError as e:
                    self.logger.warning(f"API error: {str(e)}")
                    if attempt == self.retry_attempts - 1:
                        raise
                    time.sleep(self.retry_delay_seconds)
                    
                except Exception as e:
                    if attempt == self.retry_attempts - 1:
                        raise
                    self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    time.sleep(self.retry_delay_seconds)
                    
        except Exception as e:
            self.logger.error(f"Error generating text from DeepSeek: {str(e)}")
            return f"Error: Could not generate text from DeepSeek model. {str(e)}"
    
    def analyze_market(self, market_data: Dict[str, Any], technical_indicators: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market data using DeepSeek model.
        
        Args:
            market_data: Dictionary containing market data
            technical_indicators: Dictionary containing technical indicators
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Format the prompt
            prompt = self._format_market_analysis_prompt(market_data, technical_indicators)
            
            # Generate analysis
            response_text = self.generate(
                prompt=prompt,
                system_prompt="You are an expert market analyst. Analyze the market data and technical indicators to provide trading insights."
            )
            
            # Parse JSON response
            return self._parse_json_response(response_text)
            
        except Exception as e:
            self.logger.error(f"Error analyzing market data: {str(e)}")
            return {
                "error": str(e),
                "recommendation": "hold",
                "confidence": 0.0,
                "reasoning": "Error occurred during analysis"
            }
    
    def _format_market_analysis_prompt(self, market_data: Dict[str, Any], technical_indicators: Dict[str, Any]) -> str:
        """Format the prompt for market analysis."""
        return f"""
Please analyze the following market data and technical indicators:

Market Data:
{json.dumps(market_data, indent=2)}

Technical Indicators:
{json.dumps(technical_indicators, indent=2)}

Provide a trading recommendation in the following JSON format:
{{
    "recommendation": "buy" | "sell" | "hold",
    "confidence": float (0-1),
    "price_target": float (optional),
    "stop_loss": float (optional),
    "timeframe": "short_term" | "medium_term" | "long_term",
    "reasoning": "Detailed explanation of the recommendation"
}}
"""
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from the model."""
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
                
            json_str = response[start_idx:end_idx]
            return json.loads(json_str)
            
        except Exception as e:
            self.logger.error(f"Error parsing model response: {str(e)}")
            return {
                "error": str(e),
                "recommendation": "hold",
                "confidence": 0.0,
                "reasoning": "Failed to parse response"
            } 