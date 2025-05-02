"""
ChatGPT Risk Manager module for the Dual Bot trading system.
Provides risk assessment functionality using OpenAI's ChatGPT API via OpenRouter.
"""

import os
import json
import logging
import time
import openai
from typing import Dict, Any, Optional

class ChatGPTRiskManager:
    """Manages risk assessment using ChatGPT API via OpenRouter."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the ChatGPT Risk Manager.
        
        Args:
            config: Configuration dictionary containing ChatGPT settings
        """
        self.logger = logging.getLogger(__name__)
        self.config = config.get('chatgpt', {})
        self.risk_config = self.config.get('risk_manager', {})
        
        # Set up OpenAI client with OpenRouter
        api_key = os.getenv('OPENROUTER_API_KEY') or self.config.get('openrouter_api_key')
        if not api_key:
            self.logger.warning("OpenRouter API key not found. Falling back to direct OpenAI key if available.")
            api_key = os.getenv('OPENAI_API_KEY') or self.config.get('api_key')
            if not api_key:
                raise ValueError("Neither OpenRouter nor OpenAI API key found in environment or config")
            
            # Initialize standard OpenAI client
            self.logger.info("Using direct OpenAI connection")
            self.client = openai.OpenAI(api_key=api_key)
            self.using_openrouter = False
        else:
            # Initialize OpenAI client with OpenRouter configuration
            self.logger.info("Using OpenRouter for OpenAI model access")
            self.client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )
            self.using_openrouter = True
        
        # Load risk manager settings
        self.confidence_threshold = self.risk_config.get('confidence_threshold', 0.7)
        self.max_tokens = self.risk_config.get('max_tokens', 1024)
        self.temperature = self.risk_config.get('temperature', 0.3)
        self.retry_attempts = self.risk_config.get('retry_attempts', 3)
        self.retry_delay_seconds = self.risk_config.get('retry_delay_seconds', 1)
        
        # Set the model name based on whether we're using OpenRouter or direct OpenAI
        self.model = self.config.get('model', 'gpt-4-turbo')
        if self.using_openrouter and not self.model.startswith('openai/'):
            self.model = f"openai/{self.model}"
            self.logger.info(f"Using model via OpenRouter: {self.model}")
        
    def assess_risk(self, trade_recommendation: Dict[str, Any], market_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess the risk of a trade recommendation using ChatGPT.
        
        Args:
            trade_recommendation: Dictionary containing trade recommendation details
            market_context: Dictionary containing current market context
            
        Returns:
            Dictionary containing risk assessment results
        """
        try:
            # Format the prompt
            prompt = self._format_prompt(trade_recommendation, market_context)
            
            # Make API call with retries
            for attempt in range(self.retry_attempts):
                try:
                    # Prepare the API call parameters
                    params = {
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a professional risk analyst for a trading system. Analyze the trade recommendation and provide a structured risk assessment."},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": self.max_tokens,
                        "temperature": self.temperature
                    }
                    
                    # Add OpenRouter-specific parameters if using OpenRouter
                    if self.using_openrouter:
                        params["extra_headers"] = {
                            "HTTP-Referer": "https://ai-trading-bot.com",
                            "X-Title": "AI Trading Bot"
                        }
                    
                    # Use the client to create chat completions
                    response = self.client.chat.completions.create(**params)
                    
                    # Parse the response
                    assessment = self._parse_response(response.choices[0].message.content)
                    
                    # Add metadata
                    assessment['timestamp'] = market_context.get('timestamp')
                    assessment['symbol'] = trade_recommendation.get('symbol')
                    
                    return assessment
                    
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
            self.logger.error(f"Error in risk assessment: {str(e)}")
            return {
                'approved': False,
                'confidence': 0.0,
                'risk_level': 'HIGH',
                'reason': f"Error during risk assessment: {str(e)}",
                'timestamp': market_context.get('timestamp'),
                'symbol': trade_recommendation.get('symbol')
            }
    
    def _format_prompt(self, trade_recommendation: Dict[str, Any], market_context: Dict[str, Any]) -> str:
        """Format the prompt for ChatGPT."""
        return f"""
Please analyze the following trade recommendation and provide a risk assessment:

Trade Recommendation:
{json.dumps(trade_recommendation, indent=2)}

Market Context:
{json.dumps(market_context, indent=2)}

Provide a risk assessment in the following JSON format:
{{
    "approved": boolean,
    "confidence": float (0-1),
    "risk_level": "LOW" | "MEDIUM" | "HIGH",
    "reason": "Detailed explanation of the risk assessment"
}}

Consider the following factors:
1. Market conditions and volatility
2. Technical indicators and signals
3. Options flow and dark pool activity
4. News sentiment and impact
5. Position sizing and risk management
"""
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the ChatGPT response into a structured format."""
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
                
            json_str = response[start_idx:end_idx]
            assessment = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['approved', 'confidence', 'risk_level', 'reason']
            for field in required_fields:
                if field not in assessment:
                    raise ValueError(f"Missing required field: {field}")
                    
            # Validate field types
            if not isinstance(assessment['approved'], bool):
                raise ValueError("'approved' must be a boolean")
            if not isinstance(assessment['confidence'], (int, float)):
                raise ValueError("'confidence' must be a number")
            if assessment['risk_level'] not in ['LOW', 'MEDIUM', 'HIGH']:
                raise ValueError("'risk_level' must be one of: LOW, MEDIUM, HIGH")
            if not isinstance(assessment['reason'], str):
                raise ValueError("'reason' must be a string")
                
            return assessment
            
        except Exception as e:
            self.logger.error(f"Error parsing ChatGPT response: {str(e)}")
            return {
                'approved': False,
                'confidence': 0.0,
                'risk_level': 'HIGH',
                'reason': f"Error parsing risk assessment: {str(e)}"
            } 