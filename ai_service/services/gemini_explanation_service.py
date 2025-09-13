"""
Gemini Explanation Service
Translates technical analysis results into human-friendly explanations and next steps
"""

import asyncio
import time
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

class GeminiExplanationService:
    def __init__(self):
        self.model = None
        self.is_initialized = False
        self.api_key = None
        
    async def initialize(self):
        """Initialize Gemini model for explanation generation"""
        try:
            logger.info("Initializing Gemini Explanation Service...")
            
            # Get API key from config
            self.api_key = GEMINI_API_KEY
            if not self.api_key or self.api_key == "demo_key":
                logger.warning("GEMINI_API_KEY not found in config")
                self.api_key = "demo_key"
                logger.warning("Using demo key - please set GEMINI_API_KEY for production")
            
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            self.is_initialized = True
            logger.info("Gemini Explanation Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Explanation Service: {str(e)}")
            self.is_initialized = False
    
    async def generate_explanation(self, 
                                 analysis_result: Dict[str, Any], 
                                 original_content: str,
                                 channel: str = "text") -> Dict[str, Any]:
        """
        Generate human-friendly explanation from technical analysis results
        
        Args:
            analysis_result: Technical analysis from Hugging Face models
            original_content: Original message content
            channel: Communication channel (sms, email, chat, voice, video)
        
        Returns:
            Enhanced analysis with Gemini explanations
        """
        if not self.is_initialized:
            logger.warning("Gemini Explanation Service not initialized, returning original result")
            return analysis_result
        
        try:
            # Create the prompt for explanation generation
            prompt = self._create_explanation_prompt(analysis_result, original_content, channel)
            
            # Generate explanation with Gemini
            response = await self._generate_content_async(prompt)
            
            # Parse the response
            gemini_explanation = self._parse_explanation_response(response)
            
            # Enhance the original analysis with Gemini explanations
            enhanced_result = self._enhance_analysis_result(analysis_result, gemini_explanation)
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Gemini explanation generation failed: {str(e)}")
            # Return original result if Gemini fails
            return analysis_result
    
    def _create_explanation_prompt(self, analysis_result: Dict[str, Any], 
                                 original_content: str, channel: str) -> str:
        """Create prompt for Gemini explanation generation"""
        
        # Extract key information from analysis
        risk_score = analysis_result.get('risk_score', 0.0)
        risk_level = analysis_result.get('risk_level', 'LOW')
        is_fraud = analysis_result.get('is_fraud', False)
        triggers = analysis_result.get('triggers', [])
        confidence = analysis_result.get('confidence', 0.0)
        processing_time = analysis_result.get('processing_time', 0.0)
        
        # Get detailed analysis if available
        detailed_analysis = analysis_result.get('detailed_analysis', {})
        
        prompt = f"""
You are an expert fraud detection analyst. I need you to translate technical AI analysis results into clear, human-friendly explanations and actionable next steps.

**ORIGINAL MESSAGE ({channel.upper()}):**
{original_content}

**TECHNICAL ANALYSIS RESULTS:**
- Risk Score: {risk_score:.3f} (0-1 scale)
- Risk Level: {risk_level}
- Fraud Detected: {is_fraud}
- Confidence: {confidence:.3f}
- Processing Time: {processing_time:.3f} seconds
- Trigger Phrases: {', '.join(triggers) if triggers else 'None detected'}

**DETAILED ANALYSIS:**
{json.dumps(detailed_analysis, indent=2) if detailed_analysis else 'No detailed analysis available'}

**YOUR TASK:**
Please provide a comprehensive, human-friendly explanation that includes:

1. **EXECUTIVE SUMMARY** (2-3 sentences): What did we find and what does it mean?

2. **DETAILED EXPLANATION** (3-4 sentences): Why was this flagged as {risk_level} risk? What specific indicators were detected?

3. **TECHNICAL INSIGHTS** (2-3 sentences): What patterns, keywords, or behaviors triggered the detection?

4. **IMMEDIATE ACTIONS** (3-4 bullet points): What should the user do right now?

5. **PREVENTION TIPS** (2-3 bullet points): How can the user avoid similar threats in the future?

6. **CONFIDENCE ASSESSMENT** (1-2 sentences): How certain are we about this analysis?

Please respond in a JSON format with these exact keys:
{{
    "executive_summary": "Brief overview of findings",
    "detailed_explanation": "Why this was flagged and what indicators were found",
    "technical_insights": "Specific patterns and behaviors detected",
    "immediate_actions": ["Action 1", "Action 2", "Action 3"],
    "prevention_tips": ["Tip 1", "Tip 2", "Tip 3"],
    "confidence_assessment": "Assessment of analysis certainty",
    "risk_breakdown": {{
        "primary_concerns": ["Main risk factors"],
        "secondary_concerns": ["Additional risk factors"],
        "mitigating_factors": ["Factors that reduce risk"]
    }},
    "next_steps": {{
        "immediate": "What to do right now",
        "short_term": "What to do in the next few hours",
        "long_term": "What to do to prevent future issues"
    }}
}}

Be specific, actionable, and use language that a non-technical user can understand. Focus on practical advice and clear explanations.
"""
        
        return prompt
    
    async def _generate_content_async(self, prompt: str) -> str:
        """Generate content using Gemini asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(
                    prompt,
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    }
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini content generation failed: {str(e)}")
            raise
    
    def _parse_explanation_response(self, response: str) -> Dict[str, Any]:
        """Parse Gemini response and extract explanation data"""
        try:
            # Try to extract JSON from the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                result = json.loads(json_str)
                
                # Validate and normalize the response
                return {
                    "executive_summary": result.get("executive_summary", "Analysis completed"),
                    "detailed_explanation": result.get("detailed_explanation", "Technical analysis performed"),
                    "technical_insights": result.get("technical_insights", "Patterns detected"),
                    "immediate_actions": result.get("immediate_actions", []),
                    "prevention_tips": result.get("prevention_tips", []),
                    "confidence_assessment": result.get("confidence_assessment", "Analysis completed"),
                    "risk_breakdown": result.get("risk_breakdown", {}),
                    "next_steps": result.get("next_steps", {}),
                    "raw_response": response
                }
            else:
                # Fallback parsing if JSON not found
                return self._fallback_parse(response)
                
        except Exception as e:
            logger.error(f"Failed to parse Gemini explanation response: {str(e)}")
            return self._fallback_parse(response)
    
    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails"""
        return {
            "executive_summary": "AI analysis completed successfully",
            "detailed_explanation": response[:500] + "..." if len(response) > 500 else response,
            "technical_insights": "Pattern analysis performed",
            "immediate_actions": ["Review the analysis results", "Take appropriate action"],
            "prevention_tips": ["Be cautious with suspicious messages", "Verify sender information"],
            "confidence_assessment": "Analysis completed with available data",
            "risk_breakdown": {
                "primary_concerns": ["Analysis completed"],
                "secondary_concerns": [],
                "mitigating_factors": []
            },
            "next_steps": {
                "immediate": "Review analysis results",
                "short_term": "Take recommended actions",
                "long_term": "Implement prevention measures"
            },
            "raw_response": response
        }
    
    def _enhance_analysis_result(self, original_result: Dict[str, Any], 
                               gemini_explanation: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance the original analysis result with Gemini explanations"""
        
        # Create enhanced result
        enhanced_result = original_result.copy()
        
        # Add Gemini explanation layer
        enhanced_result["gemini_explanation"] = {
            "executive_summary": gemini_explanation["executive_summary"],
            "detailed_explanation": gemini_explanation["detailed_explanation"],
            "technical_insights": gemini_explanation["technical_insights"],
            "immediate_actions": gemini_explanation["immediate_actions"],
            "prevention_tips": gemini_explanation["prevention_tips"],
            "confidence_assessment": gemini_explanation["confidence_assessment"],
            "risk_breakdown": gemini_explanation["risk_breakdown"],
            "next_steps": gemini_explanation["next_steps"],
            "generated_at": datetime.utcnow().isoformat(),
            "model_used": "gemini-2.0-flash-exp"
        }
        
        # Update the main explanation to be more human-friendly
        enhanced_result["explanation"] = gemini_explanation["executive_summary"]
        
        # Add human-friendly triggers
        if gemini_explanation["immediate_actions"]:
            enhanced_result["human_friendly_triggers"] = gemini_explanation["immediate_actions"]
        
        # Add next steps
        enhanced_result["next_steps"] = gemini_explanation["next_steps"]
        
        # Add risk breakdown
        enhanced_result["risk_breakdown"] = gemini_explanation["risk_breakdown"]
        
        return enhanced_result
    
    def is_ready(self) -> bool:
        """Check if service is ready"""
        return self.is_initialized
    
    def get_model_info(self) -> str:
        """Get model information"""
        return "Gemini 2.0 Flash Experimental (Explanation Generation)"
