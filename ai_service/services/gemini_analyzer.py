"""
Gemini 1.5 Flash Deepfake Detection Service
Uses Google's Gemini 1.5 Flash for audio/video deepfake detection
"""

import asyncio
import time
import logging
import base64
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

class GeminiAnalyzer:
    def __init__(self):
        self.model = None
        self.is_initialized = False
        self.api_key = None
        
    async def initialize(self):
        """Initialize Gemini 1.5 Flash model"""
        try:
            logger.info("Initializing Gemini Analyzer...")
            
            # Get API key from config
            self.api_key = GEMINI_API_KEY
            if not self.api_key or self.api_key == "demo_key":
                logger.warning("GEMINI_API_KEY not found in config")
                # For demo purposes, we'll use a placeholder
                self.api_key = "demo_key"
                logger.warning("Using demo key - please set GEMINI_API_KEY for production")
            
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            self.is_initialized = True
            logger.info("Gemini Analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Analyzer: {str(e)}")
            # Don't raise - allow system to work without Gemini
            self.is_initialized = False
    
    async def analyze_audio(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Analyze audio file for deepfake detection using Gemini 1.5 Flash
        """
        start_time = time.time()
        analysis_id = f"gemini_audio_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        try:
            if not self.is_initialized:
                return self._create_error_response(analysis_id, "Gemini analyzer not initialized")
            
            # Read and encode audio file
            with open(audio_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Create the prompt for deepfake detection
            prompt = self._create_audio_analysis_prompt()
            
            # Prepare the content for Gemini
            content = {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": self._get_mime_type(audio_file_path),
                            "data": audio_base64
                        }
                    }
                ]
            }
            
            # Generate content with Gemini
            response = await self._generate_content_async(content)
            
            # Parse the response
            result = self._parse_gemini_response(response)
            
            processing_time = time.time() - start_time
            
            return {
                "analysis_id": analysis_id,
                "channel": "voice",
                "audio_file": audio_file_path,
                "deepfake_score": result["confidence"],
                "is_deepfake": result["is_deepfake"],
                "confidence": result["confidence"],
                "risk_level": self._determine_risk_level(result["confidence"], result["is_deepfake"]),
                "risk_score": result["confidence"],
                "is_fraud": result["is_deepfake"],
                "triggers": result.get("technical_indicators", []),
                "explanation": result.get("explanation", "No explanation provided"),
                "processing_time": processing_time,
                "timestamp": datetime.utcnow().isoformat(),
                "audio_metadata": {
                    "file_size": len(audio_data),
                    "file_type": self._get_file_extension(audio_file_path),
                    "analysis_method": "gemini_1_5_flash"
                },
                "gemini_analysis": {
                    "raw_response": response,
                    "model_used": "gemini-1.5-flash",
                    "analysis_type": "deepfake_detection"
                }
            }
            
        except Exception as e:
            logger.error(f"Gemini audio analysis failed: {str(e)}")
            return self._create_error_response(analysis_id, f"Analysis failed: {str(e)}")
    
    async def analyze_video(self, video_file_path: str) -> Dict[str, Any]:
        """
        Analyze video file for deepfake detection using Gemini 1.5 Flash
        """
        start_time = time.time()
        analysis_id = f"gemini_video_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        try:
            if not self.is_initialized:
                return self._create_error_response(analysis_id, "Gemini analyzer not initialized")
            
            # Read and encode video file
            with open(video_file_path, 'rb') as video_file:
                video_data = video_file.read()
                video_base64 = base64.b64encode(video_data).decode('utf-8')
            
            # Create the prompt for deepfake detection
            prompt = self._create_video_analysis_prompt()
            
            # Prepare the content for Gemini
            content = {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": self._get_mime_type(video_file_path),
                            "data": video_base64
                        }
                    }
                ]
            }
            
            # Generate content with Gemini
            response = await self._generate_content_async(content)
            
            # Parse the response
            result = self._parse_gemini_response(response)
            
            processing_time = time.time() - start_time
            
            return {
                "analysis_id": analysis_id,
                "channel": "video",
                "video_file": video_file_path,
                "deepfake_score": result["confidence"],
                "is_deepfake": result["is_deepfake"],
                "confidence": result["confidence"],
                "risk_level": self._determine_risk_level(result["confidence"], result["is_deepfake"]),
                "risk_score": result["confidence"],
                "is_fraud": result["is_deepfake"],
                "triggers": result.get("technical_indicators", []),
                "explanation": result.get("explanation", "No explanation provided"),
                "processing_time": processing_time,
                "timestamp": datetime.utcnow().isoformat(),
                "video_metadata": {
                    "file_size": len(video_data),
                    "file_type": self._get_file_extension(video_file_path),
                    "analysis_method": "gemini_1_5_flash"
                },
                "gemini_analysis": {
                    "raw_response": response,
                    "model_used": "gemini-1.5-flash",
                    "analysis_type": "deepfake_detection"
                }
            }
            
        except Exception as e:
            logger.error(f"Gemini video analysis failed: {str(e)}")
            return self._create_error_response(analysis_id, f"Analysis failed: {str(e)}")
    
    def _create_audio_analysis_prompt(self) -> str:
        """Create prompt for audio deepfake analysis"""
        return """
        Analyze this audio file for deepfake/synthetic content detection. Please provide a detailed analysis focusing on:

        1. **Audio Authenticity**: Is this audio likely to be genuine human speech or artificially generated?
        2. **Technical Quality**: Are there any artifacts, inconsistencies, or unnatural patterns?
        3. **Voice Characteristics**: Does the voice sound natural, consistent, and human-like?
        4. **Background Analysis**: Are there any suspicious background elements or processing artifacts?

        Please respond with a JSON object in this exact format:
        {
            "is_deepfake": true/false,
            "confidence": 0.0-1.0,
            "reason": "Detailed explanation of your analysis and findings",
            "technical_indicators": ["list", "of", "technical", "indicators", "found"],
            "voice_quality_score": 0.0-1.0,
            "artificial_indicators": ["list", "of", "artificial", "indicators", "if", "any"]
        }

        Be thorough in your analysis and provide specific technical details about what you observe.
        """
    
    def _create_video_analysis_prompt(self) -> str:
        """Create prompt for video deepfake analysis"""
        return """
        Analyze this video file for deepfake/synthetic content detection. Please provide a detailed analysis focusing on:

        1. **Visual Authenticity**: Is this video likely to be genuine human recording or artificially generated?
        2. **Face Analysis**: Are there any facial inconsistencies, unnatural movements, or processing artifacts?
        3. **Lip Sync**: Does the lip movement match the audio naturally?
        4. **Eye Movement**: Are the eye movements natural and consistent?
        5. **Background Consistency**: Are there any background inconsistencies or artifacts?
        6. **Lighting and Shadows**: Do the lighting and shadows appear natural?

        Please respond with a JSON object in this exact format:
        {
            "is_deepfake": true/false,
            "confidence": 0.0-1.0,
            "reason": "Detailed explanation of your analysis and findings",
            "technical_indicators": ["list", "of", "technical", "indicators", "found"],
            "face_quality_score": 0.0-1.0,
            "lip_sync_score": 0.0-1.0,
            "artificial_indicators": ["list", "of", "artificial", "indicators", "if", "any"]
        }

        Be thorough in your analysis and provide specific technical details about what you observe.
        """
    
    async def _generate_content_async(self, content: Dict) -> str:
        """Generate content using Gemini asynchronously"""
        try:
            # Run the synchronous generate_content in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(
                    content,
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
    
    def _parse_gemini_response(self, response: str) -> Dict[str, Any]:
        """Parse Gemini response and extract analysis results"""
        try:
            import json
            
            # Try to extract JSON from the response
            # Look for JSON object in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                result = json.loads(json_str)
                
                # Validate and normalize the response
                return {
                    "is_deepfake": bool(result.get("is_deepfake", False)),
                    "confidence": float(result.get("confidence", 0.0)),
                    "explanation": str(result.get("reason", result.get("explanation", "No explanation provided"))),
                    "technical_indicators": result.get("technical_indicators", []),
                    "voice_quality_score": float(result.get("voice_quality_score", 0.5)),
                    "face_quality_score": float(result.get("face_quality_score", 0.5)),
                    "lip_sync_score": float(result.get("lip_sync_score", 0.5)),
                    "artificial_indicators": result.get("artificial_indicators", [])
                }
            else:
                # Fallback parsing if JSON not found
                return self._fallback_parse(response)
                
        except Exception as e:
            logger.error(f"Failed to parse Gemini response: {str(e)}")
            return self._fallback_parse(response)
    
    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails"""
        # Simple keyword-based parsing
        response_lower = response.lower()
        
        is_deepfake = any(keyword in response_lower for keyword in [
            'deepfake', 'synthetic', 'artificial', 'generated', 'fake'
        ])
        
        confidence = 0.5  # Default confidence
        if 'high confidence' in response_lower or 'very likely' in response_lower:
            confidence = 0.8
        elif 'low confidence' in response_lower or 'unlikely' in response_lower:
            confidence = 0.3
        
        return {
            "is_deepfake": is_deepfake,
            "confidence": confidence,
            "explanation": response[:500] + "..." if len(response) > 500 else response,
            "technical_indicators": [],
            "voice_quality_score": 0.5,
            "face_quality_score": 0.5,
            "lip_sync_score": 0.5,
            "artificial_indicators": []
        }
    
    def _determine_risk_level(self, confidence: float, is_deepfake: bool) -> str:
        """Determine risk level based on confidence score and deepfake status"""
        if is_deepfake:
            # If it's a deepfake, risk level depends on confidence
            if confidence >= 0.8:
                return "HIGH"
            elif confidence >= 0.5:
                return "MEDIUM"
            else:
                return "LOW"
        else:
            # If it's genuine content, risk level is always LOW regardless of confidence
            return "LOW"
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type based on file extension"""
        ext = self._get_file_extension(file_path).lower()
        mime_types = {
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg',
            '.flac': 'audio/flac',
            '.mp4': 'video/mp4',
            '.avi': 'video/avi',
            '.mov': 'video/quicktime',
            '.webm': 'video/webm'
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def _get_file_extension(self, file_path: str) -> str:
        """Get file extension"""
        return os.path.splitext(file_path)[1]
    
    def _create_error_response(self, analysis_id: str, error_message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "analysis_id": analysis_id,
            "channel": "voice",
            "error": True,
            "error_message": error_message,
            "is_deepfake": False,
            "confidence": 0.0,
            "risk_level": "LOW",
            "risk_score": 0.0,
            "is_fraud": False,
            "triggers": [],
            "explanation": f"Analysis failed: {error_message}",
            "processing_time": 0.0,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def is_ready(self) -> bool:
        """Check if analyzer is ready"""
        return self.is_initialized
    
    def get_model_info(self) -> str:
        """Get model information"""
        return "Gemini 1.5 Flash (Google AI)"
