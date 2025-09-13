"""
Chat Scam Detection Service
Uses pre-trained models and conversation analysis for chat fraud detection
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

class ChatAnalyzer:
    def __init__(self):
        self.scam_classifier = None
        self.zero_shot_classifier = None
        self.sentiment_classifier = None
        self.tokenizer = None
        self.model = None
        self.is_initialized = False
        
        # Chat-specific scam patterns
        self.chat_scam_patterns = {
            "romance_scam": [
                r'\b(baby|honey|sweetheart|darling|love)\b',
                r'\b(marry|marriage|wedding|together forever)\b',
                r'\b(send money|wire transfer|western union|moneygram)\b',
                r'\b(emergency|urgent|help me|need money)\b',
                r'\b(visa|travel|come visit|meet you)\b'
            ],
            "investment_scam": [
                r'\b(investment|trading|crypto|bitcoin|forex|ethereum)\b',
                r'\b(guaranteed|risk-free|high returns|profit|earn money)\b',
                r'\b(limited time|exclusive|insider|secret|opportunity)\b',
                r'\b(send money|deposit|initial investment|wire transfer)\b',
                r'\b(roi|return on investment|multiply your money|make money)\b',
                r'\b(300%|500%|1000%|guaranteed returns|easy money)\b',
                r'\b(act now|don\'t miss|exclusive offer|limited time)\b',
                r'\b(300% returns|5000|millions|once-in-a-lifetime)\b',
                r'\b(show you how|make millions|don\'t miss out)\b'
            ],
            "tech_support_scam": [
                r'\b(computer|virus|malware|hacked|compromised)\b',
                r'\b(remote access|teamviewer|anydesk|help you)\b',
                r'\b(payment|credit card|subscription|renewal)\b',
                r'\b(microsoft|apple|google|windows|mac)\b',
                r'\b(urgent|immediately|act now|security)\b'
            ],
            "gift_card_scam": [
                r'\b(gift card|itunes|amazon|google play|steam)\b',
                r'\b(send code|scratch off|back of card)\b',
                r'\b(urgent|emergency|help|need money)\b',
                r'\b(verify|confirm|activate|redeem)\b',
                r'\b(don\'t tell anyone|keep secret|private)\b'
            ],
            "fake_job_scam": [
                r'\b(job|work from home|remote|freelance)\b',
                r'\b(high pay|easy money|no experience)\b',
                r'\b(send money|processing fee|training cost)\b',
                r'\b(urgent|start immediately|limited positions)\b',
                r'\b(personal info|bank account|ssn|id)\b'
            ],
            "crypto_scam": [
                r'\b(cryptocurrency|bitcoin|ethereum|wallet)\b',
                r'\b(mining|trading|investment|profit)\b',
                r'\b(send crypto|wallet address|private key)\b',
                r'\b(guaranteed|risk-free|exclusive opportunity)\b',
                r'\b(limited time|act now|don\'t miss out)\b'
            ],
            "urgency_pressure": [
                r'\b(urgent|immediately|right now|hurry)\b',
                r'\b(limited time|expires soon|act fast)\b',
                r'\b(don\'t tell anyone|keep secret|confidential)\b',
                r'\b(trust me|believe me|i promise)\b',
                r'\b(emergency|crisis|help me now)\b'
            ],
            "personal_info_request": [
                r'\b(ssn|social security|credit card|bank account)\b',
                r'\b(password|pin|login|username)\b',
                r'\b(date of birth|address|phone number)\b',
                r'\b(verify identity|confirm details|update info)\b',
                r'\b(send photo|selfie|id picture)\b'
            ]
        }
        
        # Compile regex patterns for better performance
        self.compiled_patterns = {}
        for category, patterns in self.chat_scam_patterns.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    async def initialize(self):
        """Initialize Chat analysis models"""
        try:
            logger.info("Initializing Chat Analyzer...")
            
            # Load primary chat scam detection model - same as SMS for consistency
            try:
                model_name = "mariagrandury/roberta-base-finetuned-sms-spam-detection"
                
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
                
                # Create pipeline for easy inference
                self.scam_classifier = pipeline(
                    "text-classification",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=0 if torch.cuda.is_available() else -1
                )
            except Exception as e:
                logger.warning(f"Could not load primary model: {e}")
                self.scam_classifier = None
            
            # Initialize zero-shot classifier as primary method
            self.zero_shot_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Initialize sentiment classifier for conversation analysis
            try:
                self.sentiment_classifier = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    device=0 if torch.cuda.is_available() else -1
                )
            except Exception as e:
                logger.warning(f"Could not load sentiment model: {e}")
                self.sentiment_classifier = None
            
            self.is_initialized = True
            logger.info("Chat Analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Chat Analyzer: {str(e)}")
            raise
    
    async def analyze_chat(self, messages: List[str], sender_info: Optional[str] = None, 
                          conversation_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze chat conversation for scam indicators
        Args:
            messages: List of messages in the conversation
            sender_info: Sender username or identifier
            conversation_context: Additional context about the conversation
        """
        start_time = time.time()
        analysis_id = f"chat_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        try:
            # Combine all messages for analysis
            full_conversation = " ".join(messages)
            
            # Preprocess conversation
            processed_conversation = self._preprocess_chat(full_conversation)
            
            # Run analysis components
            scam_classification = await self._classify_scam(processed_conversation)
            pattern_analysis = await self._analyze_patterns(processed_conversation)
            conversation_analysis = await self._analyze_conversation(messages)
            sender_analysis = await self._analyze_sender(sender_info)
            sentiment_analysis = await self._analyze_sentiment(messages)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(
                scam_classification, pattern_analysis, conversation_analysis, 
                sender_analysis, sentiment_analysis
            )
            
            # Determine risk level
            risk_level, is_scam = self._determine_risk_level(risk_score)
            
            # Generate explanation
            explanation = self._generate_explanation(
                scam_classification, pattern_analysis, conversation_analysis, 
                sender_analysis, sentiment_analysis
            )
            
            # Extract highlighted tokens
            highlighted_tokens = self._extract_highlighted_tokens(processed_conversation, pattern_analysis)
            
            processing_time = time.time() - start_time
            
            return {
                "analysis_id": analysis_id,
                "channel": "chat",
                "messages": messages,
                "processed_conversation": processed_conversation,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "is_scam": is_scam,
                "confidence": scam_classification["confidence"],
                "triggers": self._extract_triggers(pattern_analysis),
                "explanation": explanation,
                "highlighted_tokens": highlighted_tokens,
                "processing_time": processing_time,
                "timestamp": datetime.utcnow().isoformat(),
                "detailed_analysis": {
                    "scam_classification": scam_classification,
                    "pattern_analysis": pattern_analysis,
                    "conversation_analysis": conversation_analysis,
                    "sender_analysis": sender_analysis,
                    "sentiment_analysis": sentiment_analysis
                }
            }
            
        except Exception as e:
            logger.error(f"Chat analysis failed: {str(e)}")
            raise
    
    def _preprocess_chat(self, conversation: str) -> str:
        """Preprocess chat conversation for analysis"""
        # Remove extra whitespace
        conversation = re.sub(r'\s+', ' ', conversation.strip())
        
        # Remove common chat artifacts
        conversation = re.sub(r'\[.*?\]', '', conversation)  # Remove [timestamp] or [user]
        conversation = re.sub(r'<.*?>', '', conversation)   # Remove <tags>
        
        # Expand contractions
        contractions = {
            "don't": "do not", "won't": "will not", "can't": "cannot",
            "n't": " not", "'re": " are", "'ve": " have", "'ll": " will",
            "you're": "you are", "it's": "it is", "that's": "that is",
            "i'm": "i am", "we're": "we are", "they're": "they are"
        }
        
        for contraction, expansion in contractions.items():
            conversation = conversation.replace(contraction, expansion)
        
        # Replace URLs with placeholder
        conversation = re.sub(r'https?://[^\s]+', '[URL]', conversation)
        
        # Replace phone numbers with placeholder
        conversation = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', conversation)
        
        # Replace email addresses with placeholder
        conversation = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', conversation)
        
        return conversation
    
    async def _classify_scam(self, conversation: str) -> Dict[str, Any]:
        """Classify chat conversation as scam using SMS spam detection model"""
        try:
            # Use SMS spam classifier as primary method (same as SMS analyzer)
            if self.scam_classifier is not None:
                result = self.scam_classifier(conversation)
                
                # Convert to our format
                label = result[0]["label"]
                confidence = result[0]["score"]
                
                return {
                    "predicted_label": "spam" if label == "LABEL_1" else "ham",
                    "confidence": confidence,
                    "is_scam": label == "LABEL_1"
                }
            else:
                # Fallback to zero-shot classification
                return await self._zero_shot_classification(conversation)
            
        except Exception as e:
            logger.error(f"Scam classification failed: {str(e)}")
            # Fallback to zero-shot classification
            return await self._zero_shot_classification(conversation)
    
    async def _zero_shot_classification(self, conversation: str) -> Dict[str, Any]:
        """Fallback zero-shot classification"""
        try:
            labels = ["scam", "fraud", "legitimate"]
            result = self.zero_shot_classifier(conversation, candidate_labels=labels)
            
            predicted_label = result["labels"][0]
            confidence = result["scores"][0]
            is_scam = predicted_label in ["scam", "fraud"]
            
            print(f"DEBUG: Chat zero-shot fallback - Label: {predicted_label}, Confidence: {confidence:.3f}, Is Scam: {is_scam}")
            
            return {
                "predicted_label": predicted_label,
                "confidence": confidence,
                "is_scam": is_scam
            }
            
        except Exception as e:
            logger.error(f"Zero-shot classification failed: {str(e)}")
            return {
                "predicted_label": "unknown",
                "confidence": 0.0,
                "is_scam": False
            }
    
    async def _analyze_patterns(self, conversation: str) -> Dict[str, Any]:
        """Analyze conversation for scam patterns"""
        pattern_scores = {}
        found_patterns = {}
        
        # Enhanced pattern scoring for better detection - more aggressive
        for category, patterns in self.compiled_patterns.items():
            found_patterns[category] = []
            score = 0.0
            
            for pattern in patterns:
                matches = pattern.findall(conversation)
                if matches:
                    found_patterns[category].extend(matches)
                    # Much higher weight for matches
                    base_weight = 0.5 if len(matches) > 1 else 0.4
                    score += len(matches) * base_weight
            
            # Boost score for high-risk categories - more aggressive
            if category in ["investment_scam", "romance_scam", "crypto_scam", "fake_job_scam"]:
                score = min(score * 2.0, 1.0)  # 100% boost for high-risk categories
            
            pattern_scores[category] = min(score, 1.0)  # Cap at 1.0
        
        # Calculate overall pattern score - weighted by high-risk categories
        high_risk_categories = ["investment_scam", "romance_scam", "crypto_scam", "fake_job_scam", "tech_support_scam", "gift_card_scam"]
        
        # Give more weight to high-risk categories
        weighted_score = 0.0
        total_weight = 0.0
        
        for category, score in pattern_scores.items():
            if category in high_risk_categories:
                weight = 2.0  # Double weight for high-risk
            else:
                weight = 1.0  # Normal weight for others
            
            weighted_score += score * weight
            total_weight += weight
        
        total_pattern_score = weighted_score / total_weight if total_weight > 0 else 0.0
        
        return {
            "pattern_scores": pattern_scores,
            "found_patterns": found_patterns,
            "total_pattern_score": total_pattern_score,
            "high_risk_categories": [cat for cat, score in pattern_scores.items() if score > 0.5]
        }
    
    async def _analyze_conversation(self, messages: List[str]) -> Dict[str, Any]:
        """Analyze conversation characteristics"""
        if not messages:
            return {"score": 0.0, "characteristics": {}}
        
        # Basic conversation metrics
        total_messages = len(messages)
        avg_message_length = sum(len(msg) for msg in messages) / total_messages
        total_length = sum(len(msg) for msg in messages)
        
        # Analyze message patterns
        short_messages = sum(1 for msg in messages if len(msg) < 20)
        long_messages = sum(1 for msg in messages if len(msg) > 100)
        
        # Check for rapid messaging (potential scam indicator)
        rapid_messaging = 0
        if len(messages) > 1:
            # This would need timestamps in real implementation
            # For now, we'll use message count as proxy
            rapid_messaging = 1 if total_messages > 10 else 0
        
        # Check for repetitive content
        unique_messages = len(set(messages))
        repetition_ratio = 1 - (unique_messages / total_messages) if total_messages > 0 else 0
        
        # Calculate conversation risk score - more precise like SMS
        risk_factors = []
        if short_messages / total_messages > 0.8:  # Very high short message ratio
            risk_factors.append(0.4)
        if rapid_messaging:
            risk_factors.append(0.6)  # High weight for rapid messaging
        if repetition_ratio > 0.5:  # Very high repetition (bot-like)
            risk_factors.append(0.7)
        if total_messages > 20:  # Very long conversation (potential scam)
            risk_factors.append(0.3)
        
        conversation_score = sum(risk_factors) / len(risk_factors) if risk_factors else 0.0
        
        return {
            "score": conversation_score,
            "characteristics": {
                "total_messages": total_messages,
                "avg_message_length": avg_message_length,
                "total_length": total_length,
                "short_messages": short_messages,
                "long_messages": long_messages,
                "rapid_messaging": rapid_messaging,
                "repetition_ratio": repetition_ratio
            }
        }
    
    async def _analyze_sender(self, sender_info: Optional[str]) -> Dict[str, Any]:
        """Analyze sender for suspicious patterns"""
        if not sender_info:
            return {"score": 0.0, "reputation": "unknown", "reasons": []}
        
        score = 0.0
        reasons = []
        
        # Check for suspicious username patterns
        if re.search(r'[0-9]{5,}', sender_info):  # Many numbers
            score += 0.3
            reasons.append("Username contains many numbers")
        
        if re.search(r'[^a-zA-Z0-9_]', sender_info):  # Special characters
            score += 0.2
            reasons.append("Username contains special characters")
        
        if len(sender_info) < 3:  # Very short username
            score += 0.4
            reasons.append("Very short username")
        
        if len(sender_info) > 20:  # Very long username
            score += 0.2
            reasons.append("Very long username")
        
        # Check for common scam username patterns
        scam_patterns = ['admin', 'support', 'official', 'security', 'help']
        if any(pattern in sender_info.lower() for pattern in scam_patterns):
            score += 0.3
            reasons.append("Username contains suspicious keywords")
        
        return {
            "score": min(score, 1.0),
            "reputation": "suspicious" if score > 0.3 else "legitimate" if score < 0.1 else "neutral",
            "reasons": reasons
        }
    
    async def _analyze_sentiment(self, messages: List[str]) -> Dict[str, Any]:
        """Analyze sentiment of the conversation"""
        if not self.sentiment_classifier or not messages:
            return {"score": 0.0, "sentiment": "neutral", "reasons": []}
        
        try:
            # Analyze sentiment of each message
            sentiments = []
            for message in messages[:10]:  # Limit to first 10 messages for performance
                if len(message.strip()) > 10:  # Only analyze meaningful messages
                    result = self.sentiment_classifier(message)
                    sentiments.append(result[0])
            
            if not sentiments:
                return {"score": 0.0, "sentiment": "neutral", "reasons": []}
            
            # Calculate average sentiment
            positive_count = sum(1 for s in sentiments if s['label'] == 'LABEL_2')
            negative_count = sum(1 for s in sentiments if s['label'] == 'LABEL_0')
            neutral_count = sum(1 for s in sentiments if s['label'] == 'LABEL_1')
            
            total = len(sentiments)
            positive_ratio = positive_count / total
            negative_ratio = negative_count / total
            neutral_ratio = neutral_count / total
            
            # Scam conversations often have extreme sentiment (very positive or very negative)
            sentiment_score = 0.0
            reasons = []
            
            if negative_ratio > 0.7:  # Very negative
                sentiment_score = 0.4
                reasons.append("Highly negative sentiment")
            elif positive_ratio > 0.8:  # Overly positive (potential love bombing)
                sentiment_score = 0.3
                reasons.append("Overly positive sentiment (potential love bombing)")
            elif neutral_ratio > 0.9:  # Very neutral (potential bot)
                sentiment_score = 0.2
                reasons.append("Very neutral sentiment (potential bot)")
            
            return {
                "score": sentiment_score,
                "sentiment": "negative" if negative_ratio > 0.5 else "positive" if positive_ratio > 0.5 else "neutral",
                "reasons": reasons,
                "positive_ratio": positive_ratio,
                "negative_ratio": negative_ratio,
                "neutral_ratio": neutral_ratio
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return {"score": 0.0, "sentiment": "neutral", "reasons": []}
    
    def _calculate_risk_score(self, scam_classification: Dict, pattern_analysis: Dict, 
                            conversation_analysis: Dict, sender_analysis: Dict, 
                            sentiment_analysis: Dict) -> float:
        """Calculate overall risk score - optimized like SMS"""
        # Weighted combination - more aggressive for chat detection
        weights = {
            "scam_classification": 0.3,    # Reduced - patterns are more important for chat
            "pattern_analysis": 0.5,       # Most important - patterns are key for chat
            "conversation_analysis": 0.15, # Important for chat
            "sender_analysis": 0.05,       # Less important
            "sentiment_analysis": 0.0      # Disabled for now - focus on core detection
        }
        
        # Scam classification score - use confidence if scam detected, otherwise 0 (like SMS)
        if scam_classification["is_scam"]:
            scam_score = scam_classification["confidence"]
        else:
            scam_score = 0.0
        
        # Pattern analysis score
        pattern_score = pattern_analysis["total_pattern_score"]
        
        # Conversation analysis score
        conversation_score = conversation_analysis["score"]
        
        # Sender analysis score
        sender_score = sender_analysis["score"]
        
        # Sentiment analysis score (disabled for precision)
        sentiment_score = 0.0
        
        print(f"DEBUG: Chat risk calculation - Scam: {scam_score:.3f} (is_scam: {scam_classification['is_scam']}), Pattern: {pattern_score:.3f}, Conversation: {conversation_score:.3f}, Sender: {sender_score:.3f}")
        
        # Calculate weighted average
        risk_score = (
            weights["scam_classification"] * scam_score +
            weights["pattern_analysis"] * pattern_score +
            weights["conversation_analysis"] * conversation_score +
            weights["sender_analysis"] * sender_score +
            weights["sentiment_analysis"] * sentiment_score
        )
        
        # Apply bonus for multiple high-risk patterns (like SMS but more aggressive)
        high_risk_indicators = 0
        if scam_score > 0.6: high_risk_indicators += 1
        if pattern_score > 0.3: high_risk_indicators += 1
        if conversation_score > 0.3: high_risk_indicators += 1
        if sender_score > 0.4: high_risk_indicators += 1
        
        # More aggressive bonus for chat
        if high_risk_indicators >= 1:  # Lower threshold than SMS
            bonus_factor = 1.0 + (0.3 * high_risk_indicators)  # 30% bonus per indicator
            risk_score = risk_score * bonus_factor
        
        print(f"DEBUG: Final chat risk score: {risk_score:.3f}")
        return min(risk_score, 1.0)
    
    def _determine_risk_level(self, risk_score: float) -> Tuple[str, bool]:
        """Determine risk level and scam status - more sensitive for chat"""
        if risk_score >= 0.3:  # Lowered from 0.4 - more sensitive
            return "HIGH", True
        elif risk_score >= 0.15:  # Lowered from 0.2 - more sensitive
            return "MEDIUM", True
        else:
            return "LOW", False
    
    def _generate_explanation(self, scam_classification: Dict, pattern_analysis: Dict,
                            conversation_analysis: Dict, sender_analysis: Dict, 
                            sentiment_analysis: Dict) -> str:
        """Generate human-readable explanation"""
        explanations = []
        
        # Scam classification explanation
        if scam_classification["is_scam"] and scam_classification["confidence"] > 0.7:
            explanations.append(f"AI detected {scam_classification['predicted_label']} with {scam_classification['confidence']:.1%} confidence")
        
        # Pattern analysis explanation
        high_risk_categories = pattern_analysis["high_risk_categories"]
        if high_risk_categories:
            explanations.append(f"High-risk patterns detected: {', '.join(high_risk_categories)}")
        
        # Conversation analysis explanation
        if conversation_analysis["characteristics"]["rapid_messaging"]:
            explanations.append("Rapid messaging pattern detected")
        if conversation_analysis["characteristics"]["repetition_ratio"] > 0.3:
            explanations.append("High message repetition detected")
        
        # Sender analysis explanation
        if sender_analysis["reasons"]:
            explanations.append(f"Sender issues: {'; '.join(sender_analysis['reasons'])}")
        
        # Sentiment analysis explanation
        if sentiment_analysis["reasons"]:
            explanations.append(f"Sentiment analysis: {'; '.join(sentiment_analysis['reasons'])}")
        
        return ". ".join(explanations) if explanations else "No significant scam indicators detected"
    
    def _extract_highlighted_tokens(self, conversation: str, pattern_analysis: Dict) -> List[Dict[str, Any]]:
        """Extract tokens to highlight in UI"""
        highlighted = []
        
        for category, patterns in pattern_analysis["found_patterns"].items():
            for pattern in patterns:
                if pattern.lower() in conversation.lower():
                    start = conversation.lower().find(pattern.lower())
                    highlighted.append({
                        "text": pattern,
                        "start": start,
                        "end": start + len(pattern),
                        "category": category,
                        "risk_level": "high" if category in pattern_analysis["high_risk_categories"] else "medium"
                    })
        
        return highlighted
    
    def _extract_triggers(self, pattern_analysis: Dict) -> List[str]:
        """Extract trigger phrases for UI display - same threshold as SMS"""
        triggers = []
        
        for category, patterns in pattern_analysis["found_patterns"].items():
            if pattern_analysis["pattern_scores"][category] > 0.3:  # Lower threshold for chat
                triggers.extend(patterns[:3])  # Limit to top 3 per category
        
        return list(set(triggers))  # Remove duplicates
    
    def is_ready(self) -> bool:
        """Check if analyzer is ready"""
        return self.is_initialized
    
    def get_model_info(self) -> str:
        """Get model information"""
        return "mariagrandury/roberta-base-finetuned-sms-spam-detection (Primary) + facebook/bart-large-mnli (Fallback)"
