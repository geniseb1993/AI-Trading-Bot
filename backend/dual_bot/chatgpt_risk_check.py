"""
ChatGPT risk manager module for assessing trade recommendations and providing risk assessments.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import openai

from dual_bot.config import config, logger

class ChatGPTRiskManager:
    """Risk manager using ChatGPT for trade assessment."""
    
    def __init__(self):
        """Initialize ChatGPT risk manager."""
        self.config = config
        self.api_key = self.config["ai_models"]["chatgpt"]["api_key"]
        self.model = self.config["ai_models"]["chatgpt"]["model"]
        self.max_tokens = self.config["ai_models"]["chatgpt"]["max_tokens"]
        self.temperature = self.config["ai_models"]["chatgpt"]["temperature"]
        
        # Set up OpenAI client
        openai.api_key = self.api_key
    
    def assess_trade(self, recommendation: Dict, market_context: Dict) -> Dict:
        """
        Assess a trade recommendation and provide risk analysis.
        
        Args:
            recommendation: Trade recommendation from DeepSeek
            market_context: Current market conditions and data
            
        Returns:
            Dictionary containing risk assessment and decision
        """
        try:
            # Format the prompt
            prompt = self._format_prompt(recommendation, market_context)
            
            # Get ChatGPT's analysis
            response = self._get_chatgpt_response(prompt)
            
            # Parse the response
            assessment = self._parse_response(response)
            
            # Log the assessment
            logger.info(f"Risk assessment for {recommendation['symbol']}: {json.dumps(assessment, indent=2)}")
            
            return assessment
        except Exception as e:
            logger.error(f"Error in risk assessment: {e}")
            return self._get_fallback_assessment(recommendation)
    
    def _format_prompt(self, recommendation: Dict, market_context: Dict) -> str:
        """
        Format the prompt for ChatGPT.
        
        Args:
            recommendation: Trade recommendation
            market_context: Market context data
            
        Returns:
            Formatted prompt string
        """
        # Extract key information
        symbol = recommendation["symbol"]
        direction = recommendation["direction"]
        confidence = recommendation["confidence"]
        signals = recommendation["signals"]
        trade_type = recommendation["trade_type"]
        
        # Format signals information
        signals_text = ""
        for signal in signals:
            signals_text += f"- {signal['type'].upper()}: {signal['direction']} (confidence: {signal['confidence']:.2f})\n"
            if "details" in signal:
                details = signal["details"]
                if isinstance(details, dict):
                    for key, value in details.items():
                        signals_text += f"  * {key}: {value}\n"
        
        # Format market context
        market_text = "Market Context:\n"
        if "market_hours" in market_context:
            market_text += f"- Trading hours: {market_context['market_hours']}\n"
        if "market_conditions" in market_context:
            market_text += f"- Market conditions: {market_context['market_conditions']}\n"
        if "vix" in market_context:
            market_text += f"- VIX: {market_context['vix']}\n"
        if "sector_performance" in market_context:
            market_text += f"- Sector performance: {market_context['sector_performance']}\n"
        
        # Construct the prompt
        prompt = f"""
Please analyze the following {trade_type} trade recommendation and provide a risk assessment with a YES/NO decision.

Trade Details:
- Symbol: {symbol}
- Direction: {direction}
- Overall Confidence: {confidence:.2f}
- Trade Type: {trade_type}

Signals:
{signals_text}

{market_text}

Please consider:
1. Signal alignment and confirmation
2. Market conditions and timing
3. Risk/reward ratio
4. Potential risks and hedging requirements

Provide your assessment in the following format:
DECISION: [YES/NO]
CONFIDENCE: [0-100]
RISK_LEVEL: [LOW/MEDIUM/HIGH]
SUMMARY: [One-line summary of your reasoning]
RISKS: [Key risks to consider]
HEDGING: [Hedging recommendations if needed]
"""
        
        return prompt
    
    def _get_chatgpt_response(self, prompt: str) -> str:
        """
        Get response from ChatGPT API.
        
        Args:
            prompt: Formatted prompt string
            
        Returns:
            ChatGPT's response string
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional risk manager specializing in options trading."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error getting ChatGPT response: {e}")
            raise
    
    def _parse_response(self, response: str) -> Dict:
        """
        Parse ChatGPT's response into structured format.
        
        Args:
            response: ChatGPT's response string
            
        Returns:
            Dictionary containing parsed assessment
        """
        try:
            lines = response.strip().split("\n")
            assessment = {}
            
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key == "decision":
                        assessment["decision"] = value.upper() == "YES"
                    elif key == "confidence":
                        assessment["confidence"] = float(value.replace("%", "")) / 100
                    elif key == "risk_level":
                        assessment["risk_level"] = value.upper()
                    elif key == "summary":
                        assessment["summary"] = value
                    elif key == "risks":
                        assessment["risks"] = [r.strip() for r in value.split(",")]
                    elif key == "hedging":
                        assessment["hedging"] = value
            
            # Add timestamp
            assessment["timestamp"] = datetime.now().isoformat()
            
            return assessment
        except Exception as e:
            logger.error(f"Error parsing ChatGPT response: {e}")
            raise
    
    def _get_fallback_assessment(self, recommendation: Dict) -> Dict:
        """
        Get fallback risk assessment when ChatGPT fails.
        
        Args:
            recommendation: Trade recommendation
            
        Returns:
            Fallback assessment dictionary
        """
        return {
            "decision": False,
            "confidence": 0.0,
            "risk_level": "HIGH",
            "summary": "Unable to perform risk assessment - using conservative fallback",
            "risks": ["Assessment system failure"],
            "hedging": "Do not proceed with trade",
            "timestamp": datetime.now().isoformat()
        }


# Example usage
if __name__ == "__main__":
    # Sample trade recommendation
    recommendation = {
        "symbol": "QQQ",
        "direction": "bullish",
        "confidence": 0.85,
        "signals": [
            {
                "type": "options_flow",
                "direction": "bullish",
                "confidence": 0.9,
                "details": {
                    "premium": 1500000,
                    "unusual_volume": True,
                    "dte": 0
                }
            }
        ],
        "timestamp": datetime.now().isoformat(),
        "trade_type": "0DTE"
    }
    
    # Sample market context
    market_context = {
        "market_hours": "Regular Trading Hours",
        "market_conditions": "Low Volatility",
        "vix": 15.5,
        "sector_performance": "Technology +1.2%"
    }
    
    # Initialize risk manager
    risk_manager = ChatGPTRiskManager()
    
    # Get risk assessment
    assessment = risk_manager.assess_trade(recommendation, market_context)
    
    # Print results
    print("\nRisk Assessment:")
    print(json.dumps(assessment, indent=2)) 