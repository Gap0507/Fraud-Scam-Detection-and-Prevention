"""
Text Analyzer Service for Fraud Detection
Implements zero-shot classification, rule-based heuristics, and explainable AI
"""

import asyncio
import re
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

logger = logging.getLogger(__name__)

class TextAnalyzer:
    def __init__(self):
        self.zero_shot_classifier = None
        self.tokenizer = None
        self.model = None
        self.tfidf_vectorizer = None
        self.scam_keywords = None
        self.urgency_patterns = None
        self.threat_patterns = None
        self.sender_reputation_db = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize AI models and load resources"""
        try:
            logger.info("Initializing Text Analyzer...")
            
            # Initialize zero-shot classifier
            self.zero_shot_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if self._has_gpu() else -1
            )
            
            # Initialize TF-IDF vectorizer for keyword analysis
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 3)
            )
            
            # Load scam detection patterns
            await self._load_scam_patterns()
            
            # Load sender reputation database
            await self._load_sender_reputation()
            
            self.is_initialized = True
            logger.info("Text Analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Text Analyzer: {str(e)}")
            raise
    
    def _has_gpu(self) -> bool:
        """Check if GPU is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    async def _load_scam_patterns(self):
        """Load scam detection patterns and keywords"""
        self.scam_keywords = {
            "arrest": ["arrest", "arrested", "warrant", "police", "fbi", "cia", "court", "jail", "prison"],
            "urgency": ["immediately", "urgent", "asap", "now", "right now", "hurry", "deadline", "expires"],
            "payment": ["payment", "transfer", "wire", "bitcoin", "crypto", "paypal", "venmo", "zelle"],
            "otp": ["otp", "verification code", "pin", "password", "login", "account", "suspended"],
            "threats": ["threat", "threaten", "consequences", "penalty", "fine", "legal action", "lawsuit"],
            "authority": ["government", "irs", "tax", "social security", "medicare", "bank", "official"],
            "personal": ["ssn", "social security", "credit card", "bank account", "routing number"]
        }
        
        # Compile regex patterns for better performance
        self.urgency_patterns = [
            re.compile(r'\b(immediately|urgent|asap|right now|hurry|deadline)\b', re.IGNORECASE),
            re.compile(r'\b(expires?|deadline|limited time)\b', re.IGNORECASE),
            re.compile(r'\b(act now|don\'t delay|time sensitive)\b', re.IGNORECASE)
        ]
        
        self.threat_patterns = [
            re.compile(r'\b(arrest|warrant|police|fbi|court|jail|prison)\b', re.IGNORECASE),
            re.compile(r'\b(legal action|lawsuit|penalty|fine|consequences)\b', re.IGNORECASE),
            re.compile(r'\b(account suspended|blocked|frozen|closed)\b', re.IGNORECASE)
        ]
    
    async def _load_sender_reputation(self):
        """Load sender reputation database"""
        # Simulated reputation database
        self.sender_reputation_db = {
            "suspicious_domains": [
                "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",  # Free email domains
                "tempmail.com", "10minutemail.com", "guerrillamail.com"  # Temporary email
            ],
            "legitimate_domains": [
                "irs.gov", "ssa.gov", "medicare.gov", "bankofamerica.com",
                "wellsfargo.com", "chase.com", "citibank.com"
            ],
            "suspicious_patterns": [
                r'[0-9]{10,}',  # Long number sequences
                r'[a-z0-9]{20,}',  # Random character sequences
                r'[^a-zA-Z0-9@.]',  # Special characters in sender
            ]
        }
    
    async def analyze(self, content: str, channel: str = "text", sender_info: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze text content for fraud indicators
        """
        start_time = time.time()
        analysis_id = f"text_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        try:
            # Preprocess content
            processed_content = self._preprocess_text(content)
            
            # Run analysis components
            zero_shot_result = await self._zero_shot_classification(processed_content)
            rule_based_result = await self._rule_based_analysis(processed_content)
            keyword_analysis = await self._keyword_analysis(processed_content)
            sender_analysis = await self._sender_reputation_analysis(sender_info)
            
            # Combine results
            risk_score = self._calculate_risk_score(
                zero_shot_result, rule_based_result, keyword_analysis, sender_analysis
            )
            
            # Determine risk level and fraud status
            risk_level, is_fraud = self._determine_risk_level(risk_score)
            
            # Generate explanation
            explanation = self._generate_explanation(
                zero_shot_result, rule_based_result, keyword_analysis, sender_analysis
            )
            
            # Extract highlighted tokens
            highlighted_tokens = self._extract_highlighted_tokens(
                processed_content, keyword_analysis, rule_based_result
            )
            
            processing_time = time.time() - start_time
            
            return {
                "analysis_id": analysis_id,
                "channel": channel,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "is_fraud": is_fraud,
                "triggers": self._extract_triggers(keyword_analysis, rule_based_result),
                "explanation": explanation,
                "highlighted_tokens": highlighted_tokens,
                "confidence": zero_shot_result["confidence"],
                "processing_time": processing_time,
                "timestamp": datetime.utcnow().isoformat(),
                "detailed_analysis": {
                    "zero_shot": zero_shot_result,
                    "rule_based": rule_based_result,
                    "keyword_analysis": keyword_analysis,
                    "sender_analysis": sender_analysis
                }
            }
            
        except Exception as e:
            logger.error(f"Text analysis failed: {str(e)}")
            raise
    
    def _preprocess_text(self, content: str) -> str:
        """Preprocess text for analysis"""
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Remove excessive punctuation
        content = re.sub(r'[!]{2,}', '!', content)
        content = re.sub(r'[?]{2,}', '?', content)
        
        # Expand common contractions
        contractions = {
            "don't": "do not", "won't": "will not", "can't": "cannot",
            "n't": " not", "'re": " are", "'ve": " have", "'ll": " will"
        }
        
        for contraction, expansion in contractions.items():
            content = content.replace(contraction, expansion)
        
        return content
    
    async def _zero_shot_classification(self, content: str) -> Dict[str, Any]:
        """Perform zero-shot classification"""
        try:
            labels = ["scam", "phishing", "fraud", "legitimate", "suspicious"]
            
            result = self.zero_shot_classifier(content, candidate_labels=labels)
            
            return {
                "predicted_label": result["labels"][0],
                "confidence": result["scores"][0],
                "all_scores": dict(zip(result["labels"], result["scores"]))
            }
        except Exception as e:
            logger.error(f"Zero-shot classification failed: {str(e)}")
            return {
                "predicted_label": "unknown",
                "confidence": 0.0,
                "all_scores": {}
            }
    
    async def _rule_based_analysis(self, content: str) -> Dict[str, Any]:
        """Perform rule-based analysis"""
        urgency_score = 0
        threat_score = 0
        authority_score = 0
        payment_score = 0
        
        # Check urgency patterns
        for pattern in self.urgency_patterns:
            if pattern.search(content):
                urgency_score += 0.3
        
        # Check threat patterns
        for pattern in self.threat_patterns:
            if pattern.search(content):
                threat_score += 0.4
        
        # Check for authority impersonation
        authority_keywords = self.scam_keywords["authority"]
        for keyword in authority_keywords:
            if keyword.lower() in content.lower():
                authority_score += 0.2
        
        # Check for payment requests
        payment_keywords = self.scam_keywords["payment"]
        for keyword in payment_keywords:
            if keyword.lower() in content.lower():
                payment_score += 0.3
        
        # Check for OTP/verification requests
        otp_keywords = self.scam_keywords["otp"]
        for keyword in otp_keywords:
            if keyword.lower() in content.lower():
                payment_score += 0.2
        
        return {
            "urgency_score": min(urgency_score, 1.0),
            "threat_score": min(threat_score, 1.0),
            "authority_score": min(authority_score, 1.0),
            "payment_score": min(payment_score, 1.0),
            "total_score": (urgency_score + threat_score + authority_score + payment_score) / 4
        }
    
    async def _keyword_analysis(self, content: str) -> Dict[str, Any]:
        """Analyze keywords and phrases"""
        content_lower = content.lower()
        found_keywords = {}
        keyword_scores = {}
        
        for category, keywords in self.scam_keywords.items():
            found_keywords[category] = []
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    found_keywords[category].append(keyword)
            
            # Calculate category score
            if found_keywords[category]:
                keyword_scores[category] = min(len(found_keywords[category]) * 0.2, 1.0)
            else:
                keyword_scores[category] = 0.0
        
        return {
            "found_keywords": found_keywords,
            "keyword_scores": keyword_scores,
            "total_keyword_score": sum(keyword_scores.values()) / len(keyword_scores)
        }
    
    async def _sender_reputation_analysis(self, sender_info: Optional[str]) -> Dict[str, Any]:
        """Analyze sender reputation"""
        if not sender_info:
            return {"score": 0.0, "reputation": "unknown", "reasons": []}
        
        score = 0.0
        reasons = []
        
        # Check domain reputation
        if "@" in sender_info:
            domain = sender_info.split("@")[1].lower()
            
            if domain in self.sender_reputation_db["suspicious_domains"]:
                score += 0.3
                reasons.append(f"Suspicious domain: {domain}")
            elif domain in self.sender_reputation_db["legitimate_domains"]:
                score -= 0.2
                reasons.append(f"Legitimate domain: {domain}")
        
        # Check for suspicious patterns
        for pattern in self.sender_reputation_db["suspicious_patterns"]:
            if re.search(pattern, sender_info):
                score += 0.2
                reasons.append(f"Suspicious pattern in sender: {pattern}")
        
        return {
            "score": min(score, 1.0),
            "reputation": "suspicious" if score > 0.3 else "legitimate" if score < -0.1 else "neutral",
            "reasons": reasons
        }
    
    def _calculate_risk_score(self, zero_shot_result: Dict, rule_based_result: Dict, 
                            keyword_analysis: Dict, sender_analysis: Dict) -> float:
        """Calculate overall risk score"""
        # Weighted combination of different analysis results
        weights = {
            "zero_shot": 0.3,
            "rule_based": 0.3,
            "keyword": 0.2,
            "sender": 0.2
        }
        
        # Zero-shot score (convert to 0-1 scale)
        zero_shot_score = 0.0
        if zero_shot_result["predicted_label"] in ["scam", "phishing", "fraud"]:
            zero_shot_score = zero_shot_result["confidence"]
        elif zero_shot_result["predicted_label"] == "suspicious":
            zero_shot_score = zero_shot_result["confidence"] * 0.7
        
        # Rule-based score
        rule_based_score = rule_based_result["total_score"]
        
        # Keyword score
        keyword_score = keyword_analysis["total_keyword_score"]
        
        # Sender score
        sender_score = sender_analysis["score"]
        
        # Calculate weighted average
        risk_score = (
            weights["zero_shot"] * zero_shot_score +
            weights["rule_based"] * rule_based_score +
            weights["keyword"] * keyword_score +
            weights["sender"] * sender_score
        )
        
        return min(risk_score, 1.0)
    
    def _determine_risk_level(self, risk_score: float) -> Tuple[str, bool]:
        """Determine risk level and fraud status"""
        if risk_score >= 0.8:
            return "HIGH", True
        elif risk_score >= 0.5:
            return "MEDIUM", False
        else:
            return "LOW", False
    
    def _generate_explanation(self, zero_shot_result: Dict, rule_based_result: Dict,
                            keyword_analysis: Dict, sender_analysis: Dict) -> str:
        """Generate human-readable explanation"""
        explanations = []
        
        # Zero-shot explanation
        if zero_shot_result["confidence"] > 0.7:
            explanations.append(
                f"AI classification: {zero_shot_result['predicted_label']} "
                f"(confidence: {zero_shot_result['confidence']:.2f})"
            )
        
        # Rule-based explanations
        if rule_based_result["urgency_score"] > 0.5:
            explanations.append("High urgency language detected")
        if rule_based_result["threat_score"] > 0.5:
            explanations.append("Threatening language detected")
        if rule_based_result["authority_score"] > 0.5:
            explanations.append("Authority impersonation detected")
        if rule_based_result["payment_score"] > 0.5:
            explanations.append("Payment request detected")
        
        # Keyword explanations
        high_risk_categories = [cat for cat, score in keyword_analysis["keyword_scores"].items() 
                               if score > 0.5]
        if high_risk_categories:
            explanations.append(f"High-risk keywords found: {', '.join(high_risk_categories)}")
        
        # Sender explanations
        if sender_analysis["reasons"]:
            explanations.append(f"Sender issues: {'; '.join(sender_analysis['reasons'])}")
        
        return ". ".join(explanations) if explanations else "No significant fraud indicators detected"
    
    def _extract_highlighted_tokens(self, content: str, keyword_analysis: Dict, 
                                  rule_based_result: Dict) -> List[Dict[str, Any]]:
        """Extract tokens to highlight in UI"""
        highlighted = []
        
        # Highlight found keywords
        for category, keywords in keyword_analysis["found_keywords"].items():
            for keyword in keywords:
                if keyword.lower() in content.lower():
                    start = content.lower().find(keyword.lower())
                    highlighted.append({
                        "text": keyword,
                        "start": start,
                        "end": start + len(keyword),
                        "category": category,
                        "risk_level": "high" if keyword_analysis["keyword_scores"][category] > 0.5 else "medium"
                    })
        
        return highlighted
    
    def _extract_triggers(self, keyword_analysis: Dict, rule_based_result: Dict) -> List[str]:
        """Extract trigger phrases for UI display"""
        triggers = []
        
        # Add high-risk keywords
        for category, keywords in keyword_analysis["found_keywords"].items():
            if keyword_analysis["keyword_scores"][category] > 0.5:
                triggers.extend(keywords[:3])  # Limit to top 3 per category
        
        # Add rule-based triggers
        if rule_based_result["urgency_score"] > 0.5:
            triggers.append("Urgency language")
        if rule_based_result["threat_score"] > 0.5:
            triggers.append("Threatening language")
        if rule_based_result["authority_score"] > 0.5:
            triggers.append("Authority impersonation")
        if rule_based_result["payment_score"] > 0.5:
            triggers.append("Payment request")
        
        return list(set(triggers))  # Remove duplicates
    
    def is_ready(self) -> bool:
        """Check if analyzer is ready"""
        return self.is_initialized
    
    def get_model_info(self) -> str:
        """Get model information"""
        return "facebook/bart-large-mnli (Zero-shot Classification)"
