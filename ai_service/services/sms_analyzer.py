"""
SMS Scam Detection Service
Uses pre-trained models and rule-based analysis for SMS fraud detection
"""

import asyncio
import re
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    pipeline
)
import torch

logger = logging.getLogger(__name__)

class SMSAnalyzer:
    def __init__(self):
        self.spam_classifier = None
        self.zero_shot_classifier = None
        self.tokenizer = None
        self.model = None
        self.is_initialized = False
        
        # SMS-specific scam patterns
        self.sms_scam_patterns = {
            "urgency": [
                r'\b(urgent|immediately|asap|right now|hurry|deadline|expires?)\b',
                r'\b(act now|don\'t delay|time sensitive|limited time)\b',
                r'\b(expires? in \d+ hours?|deadline today)\b'
            ],
            "authority": [
                r'\b(police|fbi|cia|court|irs|bank|government|official)\b',
                r'\b(arrest|warrant|legal action|investigation)\b',
                r'\b(account suspended|blocked|frozen|closed)\b'
            ],
            "payment": [
                r'\b(transfer|wire|bitcoin|crypto|paypal|venmo|zelle)\b',
                r'\b(payment|pay now|send money|deposit)\b',
                r'\b(\$\d+|\d+ dollars?|amount|fee|charge)\b'
            ],
            "otp_verification": [
                r'\b(otp|verification code|pin|password|login)\b',
                r'\b(confirm|verify|authenticate|security code)\b',
                r'\b(click here|link|website|login now)\b'
            ],
            "threats": [
                r'\b(arrest|jail|prison|warrant|legal consequences)\b',
                r'\b(fine|penalty|lawsuit|court|investigation)\b',
                r'\b(account closed|suspended|blocked|frozen)\b'
            ],
            "personal_info": [
                r'\b(ssn|social security|credit card|bank account)\b',
                r'\b(routing number|account number|personal info)\b',
                r'\b(verify identity|confirm details|update info)\b'
            ]
        }
        
        # Compile regex patterns for better performance
        self.compiled_patterns = {}
        for category, patterns in self.sms_scam_patterns.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    async def initialize(self):
        """Initialize SMS analysis models"""
        try:
            logger.info("Initializing SMS Analyzer...")
            
            # Load pre-trained SMS spam detection model
            model_name = "mariagrandury/roberta-base-finetuned-sms-spam-detection"
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            # Create pipeline for easy inference
            self.spam_classifier = pipeline(
                "text-classification",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Initialize zero-shot classifier as backup
            self.zero_shot_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.is_initialized = True
            logger.info("SMS Analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SMS Analyzer: {str(e)}")
            raise
    
    async def analyze_sms(self, message: str, sender_number: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze SMS message for scam indicators
        """
        start_time = time.time()
        analysis_id = f"sms_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        try:
            # Preprocess SMS
            processed_message = self._preprocess_sms(message)
            
            # Run analysis components
            spam_classification = await self._classify_spam(processed_message)
            pattern_analysis = await self._analyze_patterns(processed_message)
            statistical_analysis = await self._analyze_statistics(processed_message)
            sender_analysis = await self._analyze_sender(sender_number)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(
                spam_classification, pattern_analysis, statistical_analysis, sender_analysis
            )
            
            # Determine risk level
            risk_level, is_scam = self._determine_risk_level(risk_score)
            
            # Generate explanation
            explanation = self._generate_explanation(
                spam_classification, pattern_analysis, statistical_analysis, sender_analysis
            )
            
            # Extract highlighted tokens
            highlighted_tokens = self._extract_highlighted_tokens(processed_message, pattern_analysis)
            
            processing_time = time.time() - start_time
            
            return {
                "analysis_id": analysis_id,
                "channel": "sms",
                "message": message,
                "processed_message": processed_message,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "is_scam": is_scam,
                "confidence": spam_classification["confidence"],
                "triggers": self._extract_triggers(pattern_analysis),
                "explanation": explanation,
                "highlighted_tokens": highlighted_tokens,
                "processing_time": processing_time,
                "timestamp": datetime.utcnow().isoformat(),
                "detailed_analysis": {
                    "spam_classification": spam_classification,
                    "pattern_analysis": pattern_analysis,
                    "statistical_analysis": statistical_analysis,
                    "sender_analysis": sender_analysis
                }
            }
            
        except Exception as e:
            logger.error(f"SMS analysis failed: {str(e)}")
            raise
    
    def _preprocess_sms(self, message: str) -> str:
        """Preprocess SMS message for analysis"""
        # Remove extra whitespace
        message = re.sub(r'\s+', ' ', message.strip())
        
        # Expand contractions
        contractions = {
            "don't": "do not", "won't": "will not", "can't": "cannot",
            "n't": " not", "'re": " are", "'ve": " have", "'ll": " will",
            "you're": "you are", "it's": "it is", "that's": "that is"
        }
        
        for contraction, expansion in contractions.items():
            message = message.replace(contraction, expansion)
        
        # Replace phone numbers with placeholder
        message = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', message)
        
        # Replace email addresses with placeholder
        message = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', message)
        
        # Replace URLs with placeholder
        message = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '[URL]', message)
        
        return message
    
    async def _classify_spam(self, message: str) -> Dict[str, Any]:
        """Classify SMS as spam or ham using pre-trained model"""
        try:
            result = self.spam_classifier(message)
            
            # Convert to our format
            label = result[0]["label"]
            confidence = result[0]["score"]
            
            return {
                "predicted_label": "spam" if label == "LABEL_1" else "ham",
                "confidence": confidence,
                "is_spam": label == "LABEL_1"
            }
            
        except Exception as e:
            logger.error(f"Spam classification failed: {str(e)}")
            # Fallback to zero-shot classification
            return await self._zero_shot_classification(message)
    
    async def _zero_shot_classification(self, message: str) -> Dict[str, Any]:
        """Fallback zero-shot classification"""
        try:
            labels = ["spam", "scam", "fraud", "legitimate"]
            result = self.zero_shot_classifier(message, candidate_labels=labels)
            
            return {
                "predicted_label": result["labels"][0],
                "confidence": result["scores"][0],
                "is_spam": result["labels"][0] in ["spam", "scam", "fraud"]
            }
            
        except Exception as e:
            logger.error(f"Zero-shot classification failed: {str(e)}")
            return {
                "predicted_label": "unknown",
                "confidence": 0.0,
                "is_spam": False
            }
    
    async def _analyze_patterns(self, message: str) -> Dict[str, Any]:
        """Analyze message for scam patterns"""
        pattern_scores = {}
        found_patterns = {}
        
        for category, patterns in self.compiled_patterns.items():
            found_patterns[category] = []
            score = 0.0
            
            for pattern in patterns:
                matches = pattern.findall(message)
                if matches:
                    found_patterns[category].extend(matches)
                    score += len(matches) * 0.2  # Each match adds 0.2 to score
            
            pattern_scores[category] = min(score, 1.0)  # Cap at 1.0
        
        # Calculate overall pattern score
        total_pattern_score = sum(pattern_scores.values()) / len(pattern_scores)
        
        return {
            "pattern_scores": pattern_scores,
            "found_patterns": found_patterns,
            "total_pattern_score": total_pattern_score,
            "high_risk_categories": [cat for cat, score in pattern_scores.items() if score > 0.5]
        }
    
    async def _analyze_statistics(self, message: str) -> Dict[str, Any]:
        """Analyze statistical features of the message"""
        # Message length analysis
        length = len(message)
        word_count = len(message.split())
        
        # Character analysis
        uppercase_ratio = sum(1 for c in message if c.isupper()) / len(message) if message else 0
        digit_ratio = sum(1 for c in message if c.isdigit()) / len(message) if message else 0
        special_char_ratio = sum(1 for c in message if not c.isalnum() and not c.isspace()) / len(message) if message else 0
        
        # Suspicious patterns
        excessive_caps = uppercase_ratio > 0.3
        excessive_digits = digit_ratio > 0.2
        excessive_special = special_char_ratio > 0.1
        very_short = length < 20
        very_long = length > 200
        
        # Calculate statistical risk score
        risk_factors = [excessive_caps, excessive_digits, excessive_special, very_short, very_long]
        statistical_score = sum(risk_factors) / len(risk_factors)
        
        return {
            "length": length,
            "word_count": word_count,
            "uppercase_ratio": uppercase_ratio,
            "digit_ratio": digit_ratio,
            "special_char_ratio": special_char_ratio,
            "excessive_caps": excessive_caps,
            "excessive_digits": excessive_digits,
            "excessive_special": excessive_special,
            "very_short": very_short,
            "very_long": very_long,
            "statistical_score": statistical_score
        }
    
    async def _analyze_sender(self, sender_number: Optional[str]) -> Dict[str, Any]:
        """Analyze sender number for suspicious patterns"""
        if not sender_number:
            return {"score": 0.0, "reputation": "unknown", "reasons": []}
        
        score = 0.0
        reasons = []
        
        # Check for suspicious number patterns
        if re.match(r'^\d{10}$', sender_number):  # 10-digit number
            score += 0.1
            reasons.append("Standard 10-digit number")
        elif re.match(r'^\d{11}$', sender_number):  # 11-digit number
            score += 0.2
            reasons.append("11-digit number (suspicious)")
        elif re.match(r'^\d{5,9}$', sender_number):  # Short number
            score += 0.3
            reasons.append("Short number (suspicious)")
        
        # Check for repeated digits
        if re.search(r'(\d)\1{3,}', sender_number):  # 4+ repeated digits
            score += 0.4
            reasons.append("Repeated digits pattern")
        
        # Check for sequential patterns
        if re.search(r'1234|2345|3456|4567|5678|6789', sender_number):
            score += 0.3
            reasons.append("Sequential digit pattern")
        
        return {
            "score": min(score, 1.0),
            "reputation": "suspicious" if score > 0.3 else "legitimate" if score < 0.1 else "neutral",
            "reasons": reasons
        }
    
    def _calculate_risk_score(self, spam_classification: Dict, pattern_analysis: Dict, 
                            statistical_analysis: Dict, sender_analysis: Dict) -> float:
        """Calculate overall risk score"""
        # Weighted combination
        weights = {
            "spam_classification": 0.4,  # Most important
            "pattern_analysis": 0.3,
            "statistical_analysis": 0.2,
            "sender_analysis": 0.1
        }
        
        # Spam classification score
        spam_score = spam_classification["confidence"] if spam_classification["is_spam"] else 0.0
        
        # Pattern analysis score
        pattern_score = pattern_analysis["total_pattern_score"]
        
        # Statistical analysis score
        statistical_score = statistical_analysis["statistical_score"]
        
        # Sender analysis score
        sender_score = sender_analysis["score"]
        
        # Calculate weighted average
        risk_score = (
            weights["spam_classification"] * spam_score +
            weights["pattern_analysis"] * pattern_score +
            weights["statistical_analysis"] * statistical_score +
            weights["sender_analysis"] * sender_score
        )
        
        return min(risk_score, 1.0)
    
    def _determine_risk_level(self, risk_score: float) -> Tuple[str, bool]:
        """Determine risk level and scam status"""
        if risk_score >= 0.8:
            return "HIGH", True
        elif risk_score >= 0.5:
            return "MEDIUM", False
        else:
            return "LOW", False
    
    def _generate_explanation(self, spam_classification: Dict, pattern_analysis: Dict,
                            statistical_analysis: Dict, sender_analysis: Dict) -> str:
        """Generate human-readable explanation"""
        explanations = []
        
        # Spam classification explanation
        if spam_classification["is_spam"] and spam_classification["confidence"] > 0.7:
            explanations.append(f"AI detected spam with {spam_classification['confidence']:.1%} confidence")
        
        # Pattern analysis explanation
        high_risk_categories = pattern_analysis["high_risk_categories"]
        if high_risk_categories:
            explanations.append(f"High-risk patterns detected: {', '.join(high_risk_categories)}")
        
        # Statistical analysis explanation
        if statistical_analysis["excessive_caps"]:
            explanations.append("Excessive use of capital letters")
        if statistical_analysis["excessive_digits"]:
            explanations.append("Excessive use of numbers")
        if statistical_analysis["very_short"]:
            explanations.append("Unusually short message")
        if statistical_analysis["very_long"]:
            explanations.append("Unusually long message")
        
        # Sender analysis explanation
        if sender_analysis["reasons"]:
            explanations.append(f"Sender issues: {'; '.join(sender_analysis['reasons'])}")
        
        return ". ".join(explanations) if explanations else "No significant scam indicators detected"
    
    def _extract_highlighted_tokens(self, message: str, pattern_analysis: Dict) -> List[Dict[str, Any]]:
        """Extract tokens to highlight in UI"""
        highlighted = []
        
        for category, patterns in pattern_analysis["found_patterns"].items():
            for pattern in patterns:
                if pattern.lower() in message.lower():
                    start = message.lower().find(pattern.lower())
                    highlighted.append({
                        "text": pattern,
                        "start": start,
                        "end": start + len(pattern),
                        "category": category,
                        "risk_level": "high" if category in pattern_analysis["high_risk_categories"] else "medium"
                    })
        
        return highlighted
    
    def _extract_triggers(self, pattern_analysis: Dict) -> List[str]:
        """Extract trigger phrases for UI display"""
        triggers = []
        
        for category, patterns in pattern_analysis["found_patterns"].items():
            if pattern_analysis["pattern_scores"][category] > 0.5:
                triggers.extend(patterns[:3])  # Limit to top 3 per category
        
        return list(set(triggers))  # Remove duplicates
    
    def is_ready(self) -> bool:
        """Check if analyzer is ready"""
        return self.is_initialized
    
    def get_model_info(self) -> str:
        """Get model information"""
        return "mariagrandury/roberta-base-finetuned-sms-spam-detection"
