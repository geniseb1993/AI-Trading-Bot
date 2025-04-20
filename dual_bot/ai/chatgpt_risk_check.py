"""
ChatGPT Risk Manager module for the Dual Bot trading system.
Provides risk assessment functionality using OpenAI's ChatGPT API.
"""

import os
import json
import logging
import openai
from typing import Dict, Any, Optional

class ChatGPTRiskManager:
    """Manages risk assessment using ChatGPT API."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the ChatGPT Risk Manager.
        
        Args:
            config: Configuration dictionary containing ChatGPT settings
        """
        self.logger = logging.getLogger(__name__)
        self.config = config.get('chatgpt', {})
        self.risk_config = self.config.get('risk_manager', {})
        
        # Set up OpenAI client
        api_key = os.getenv('OPENAI_API_KEY') or self.config.get('api_key')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment or config")
        
        openai.api_key = api_key
        
        # Load risk manager settings
        self.confidence_threshold = self.risk_config.get('confidence_threshold', 0.7)
        self.max_tokens = self.risk_config.get('max_tokens', 1024)
        self.temperature = self.risk_config.get('temperature', 0.3)
        self.retry_attempts = self.risk_config.get('retry_attempts', 3)
        self.retry_delay_seconds = self.risk_config.get('retry_delay_seconds', 1)
        
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
                    response = openai.ChatCompletion.create(
                        model=self.config.get('model', 'gpt-4-turbo-preview'),
                        messages=[
                            {"role": "system", "content": "You are a professional risk analyst for a trading system. Analyze the trade recommendation and provide a structured risk assessment."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=self.max_tokens,
                        temperature=self.temperature
                    )
                    
                    # Parse the response
                    assessment = self._parse_response(response.choices[0].message.content)
                    
                    # Add metadata
                    assessment['timestamp'] = market_context.get('timestamp')
                    assessment['symbol'] = trade_recommendation.get('symbol')
                    
                    return assessment
                    
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