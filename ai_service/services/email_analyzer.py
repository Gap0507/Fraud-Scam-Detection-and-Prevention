"""
Email Phishing Detection Service
Uses pre-trained models and rule-based analysis for email fraud detection
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

class EmailAnalyzer:
    def __init__(self):
        self.phishing_classifier = None
        self.zero_shot_classifier = None
        self.tokenizer = None
        self.model = None
        self.is_initialized = False
        
        # Performance monitoring
        self.analysis_cache = {}  # Simple cache for repeated analyses
        self.cache_max_size = 100  # Limit cache size
        
        # Email-specific phishing patterns
        self.email_phishing_patterns = {
            "urgency": [
                r'\b(urgent|immediately|asap|right now|hurry|deadline|expires?)\b',
                r'\b(act now|don\'t delay|time sensitive|limited time)\b',
                r'\b(expires? in \d+ hours?|deadline today)\b',
                r'\b(account will be closed|suspended|blocked)\b'
            ],
            "authority": [
                r'\b(police|fbi|cia|court|irs|bank|government|official|microsoft|apple|google)\b',
                r'\b(arrest|warrant|legal action|investigation|security team)\b',
                r'\b(account suspended|blocked|frozen|closed|compromised)\b',
                r'\b(verify|confirm|update|validate)\b(?!.*click|.*link)'  # Exclude when followed by click/link
            ],
            "payment": [
                r'\b(transfer|wire|bitcoin|crypto|paypal|venmo|zelle|gift card)\b',
                r'\b(payment|pay now|send money|deposit|refund)\b',
                r'\b(\$\d+|\d+ dollars?|amount|fee|charge|tax)\b',
                r'\b(credit card|debit card|bank account|routing number)\b'
            ],
            "phishing_links": [
                r'https?://[^\s]+(?:bit\.ly|tinyurl|goo\.gl|t\.co|short\.link)',
                r'https?://[^\s]+(?:click|verify|confirm|update|secure)(?![^\s]*\.(?:com|org|net|edu|gov))',  # Exclude legitimate domains
                r'https?://[^\s]+(?:[a-z0-9-]+\.(?:tk|ml|ga|cf))',
                r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>'
            ],
            "suspicious_domains": [
                r'@[a-z0-9-]+\.(?:tk|ml|ga|cf|cc|info)',
                r'@[a-z0-9-]+\.(?:gq|top|click|download)',
                r'@[a-z0-9-]+\.(?:online|site|website|web)'
            ],
            "threats": [
                r'\b(arrest|jail|prison|warrant|legal consequences|lawsuit)\b',
                r'\b(fine|penalty|investigation|court|police)\b',
                r'\b(account closed|suspended|blocked|frozen|terminated)\b',
                r'\b(immediate action|consequences|penalties)\b'
            ],
            "personal_info": [
                r'\b(ssn|social security|credit card|bank account|routing)\b',
                r'\b(password|pin|login|username|account number)\b',
                r'\b(verify identity|confirm details|update info|personal data)\b',
                r'\b(date of birth|address|phone number|email address)\b'
            ],
            "spoofing": [
                r'\b(microsoft|apple|google|amazon|paypal|ebay|facebook)\b',
                r'\b(irs|fbi|cia|police|government|official)\b',
                r'\b(bank|chase|wells fargo|bank of america|citibank)\b'
            ],
            "lottery_scams": [
                r'\b(congratulations|you\'ve won|you have won|winner)\b',
                r'\b(lottery|jackpot|prize|winnings?|reward)\b',
                r'\b(claim your|collect your|receive your)\b',
                r'\b(international lottery|national lottery|mega lottery)\b',
                r'\b(\$[\d,]+ prize|\$[\d,]+ winnings?|\$[\d,]+ reward)\b',
                r'\b(claim now|act fast|limited time offer)\b'
            ],
            "fake_legitimacy": [
                r'\b(if you did not request|if you did not make|ignore this email)\b',
                r'\b(legitimate|official|authorized|verified)\b',
                r'\b(security team|customer service|support team)\b',
                r'\b(we are committed|we take security|we value your)\b'
            ]
        }
        
        # Compile regex patterns for better performance
        self.compiled_patterns = {}
        for category, patterns in self.email_phishing_patterns.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    async def initialize(self):
        """Initialize Email analysis models"""
        try:
            logger.info("Initializing Email Analyzer...")
            
            # Use a more balanced model for email classification - similar to SMS approach
            try:
                # Try a general text classification model that works well for emails
                self.phishing_classifier = pipeline(
                    "text-classification",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    device=0 if torch.cuda.is_available() else -1
                )
            except Exception as e:
                logger.warning(f"Could not load primary model: {e}")
                # Fallback to zero-shot only
                self.phishing_classifier = None
            
            # Initialize zero-shot classifier as primary method (like SMS)
            self.zero_shot_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.is_initialized = True
            logger.info("Email Analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Email Analyzer: {str(e)}")
            raise
    
    async def analyze_email(self, subject: str, body: str, sender_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze email for phishing indicators with performance optimization
        """
        start_time = time.time()
        analysis_id = f"email_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        try:
            # Create cache key for potential reuse
            cache_key = f"{hash(subject + body + (sender_email or ''))}"
            
            # Check cache first (for hackathon demo - simple approach)
            if cache_key in self.analysis_cache:
                cached_result = self.analysis_cache[cache_key].copy()
                cached_result["analysis_id"] = analysis_id
                cached_result["processing_time"] = time.time() - start_time
                cached_result["timestamp"] = datetime.utcnow().isoformat()
                print(f"DEBUG: Using cached result for email analysis")
                return cached_result
            
            # Combine subject and body for analysis
            full_content = f"Subject: {subject}\n\nBody: {body}"
            
            # Preprocess email
            processed_content = self._preprocess_email(full_content)
            
            # Run analysis components
            phishing_classification = await self._classify_phishing(processed_content)
            pattern_analysis = await self._analyze_patterns(processed_content)
            statistical_analysis = await self._analyze_statistics(processed_content)
            sender_analysis = await self._analyze_sender(sender_email)
            link_analysis = await self._analyze_links(body)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(
                phishing_classification, pattern_analysis, statistical_analysis, 
                sender_analysis, link_analysis
            )
            
            # Determine risk level
            risk_level, is_phishing = self._determine_risk_level(risk_score)
            
            # Generate explanation
            explanation = self._generate_explanation(
                phishing_classification, pattern_analysis, statistical_analysis, 
                sender_analysis, link_analysis
            )
            
            # Extract highlighted tokens
            highlighted_tokens = self._extract_highlighted_tokens(processed_content, pattern_analysis)
            
            processing_time = time.time() - start_time
            
            # Create result
            result = {
                "analysis_id": analysis_id,
                "channel": "email",
                "subject": subject,
                "body": body,
                "processed_content": processed_content,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "is_phishing": is_phishing,
                "confidence": phishing_classification["confidence"],
                "triggers": self._extract_triggers(pattern_analysis),
                "explanation": explanation,
                "highlighted_tokens": highlighted_tokens,
                "processing_time": processing_time,
                "timestamp": datetime.utcnow().isoformat(),
                "detailed_analysis": {
                    "phishing_classification": phishing_classification,
                    "pattern_analysis": pattern_analysis,
                    "statistical_analysis": statistical_analysis,
                    "sender_analysis": sender_analysis,
                    "link_analysis": link_analysis
                }
            }
            
            # Cache result for potential reuse (simple LRU for hackathon)
            if len(self.analysis_cache) >= self.cache_max_size:
                # Remove oldest entry (simple approach)
                oldest_key = next(iter(self.analysis_cache))
                del self.analysis_cache[oldest_key]
            
            self.analysis_cache[cache_key] = result.copy()
            
            return result
            
        except Exception as e:
            logger.error(f"Email analysis failed: {str(e)}")
            raise
    
    def _preprocess_email(self, content: str) -> str:
        """Preprocess email content for analysis with enhanced edge case handling"""
        # Handle empty or very short content
        if not content or len(content.strip()) < 10:
            return "short content"
        
        # Convert to lowercase for consistency
        content = content.lower()
        
        # Remove HTML tags and decode HTML entities
        content = re.sub(r'<[^>]+>', ' ', content)
        content = re.sub(r'&[a-zA-Z0-9#]+;', ' ', content)  # Remove HTML entities
        
        # Remove email headers
        content = re.sub(r'^(from|to|subject|date|message-id):.*$', '', content, flags=re.MULTILINE)
        
        # Remove extra whitespace and normalize
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Handle very long content by keeping most relevant parts
        if len(content) > 5000:
            # Keep first 2000 and last 1000 characters for context
            content = content[:2000] + " ... " + content[-1000:]
        
        # Expand contractions
        contractions = {
            "don't": "do not", "won't": "will not", "can't": "cannot",
            "n't": " not", "'re": " are", "'ve": " have", "'ll": " will",
            "you're": "you are", "it's": "it is", "that's": "that is"
        }
        
        for contraction, expansion in contractions.items():
            content = content.replace(contraction, expansion)
        
        # Replace email addresses with placeholder
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', content)
        
        # Replace URLs with placeholder (improved regex)
        content = re.sub(r'https?://[^\s<>"\']+', '[URL]', content)
        
        # Replace phone numbers with placeholder
        content = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', content)
        
        # Remove excessive punctuation
        content = re.sub(r'[!]{2,}', '!', content)
        content = re.sub(r'[?]{2,}', '?', content)
        
        return content
    
    async def _classify_phishing(self, content: str) -> Dict[str, Any]:
        """Classify email as phishing using zero-shot classification with performance optimization"""
        try:
            # Truncate very long emails to improve performance (keep first 2000 chars)
            # This maintains context while reducing processing time
            truncated_content = content[:2000] if len(content) > 2000 else content
            
            # Use zero-shot classification as primary method (like SMS system)
            # Enhanced labels for better detection
            labels = ["phishing", "spam", "fraud", "suspicious", "lottery_scam", "phishing_email", "legitimate", "business"]
            result = self.zero_shot_classifier(truncated_content, candidate_labels=labels)
            
            predicted_label = result["labels"][0]
            confidence = result["scores"][0]
            is_phishing = predicted_label in ["phishing", "spam", "fraud", "suspicious", "lottery_scam", "phishing_email"]
            
            print(f"DEBUG: Zero-shot classification - Label: {predicted_label}, Confidence: {confidence:.3f}, Is Phishing: {is_phishing}")
            
            return {
                "predicted_label": predicted_label,
                "confidence": confidence,
                "is_phishing": is_phishing
            }
            
        except Exception as e:
            logger.error(f"Zero-shot classification failed: {str(e)}")
            # Fallback to backup classifier if available
            if self.phishing_classifier is not None:
                try:
                    # Use truncated content for fallback as well
                    truncated_content = content[:2000] if len(content) > 2000 else content
                    result = self.phishing_classifier(truncated_content)
                    predicted_label = result[0]["label"]
                    confidence = result[0]["score"]
                    
                    # Improved sentiment-to-phishing mapping
                    # Note: This is a prototype-level fallback - sentiment analysis isn't ideal for phishing detection
                    is_phishing = (predicted_label == "NEGATIVE" and confidence > 0.6) or confidence > 0.8
                    
                    print(f"DEBUG: Fallback classification - Label: {predicted_label}, Confidence: {confidence:.3f}, Is Phishing: {is_phishing}")
                    
                    return {
                        "predicted_label": "phishing" if is_phishing else "legitimate",
                        "confidence": confidence,
                        "is_phishing": is_phishing
                    }
                except Exception as e2:
                    logger.error(f"Fallback classification also failed: {str(e2)}")
            
            return {
                "predicted_label": "unknown",
                "confidence": 0.0,
                "is_phishing": False
            }
    
    async def _analyze_patterns(self, content: str) -> Dict[str, Any]:
        """Analyze email for phishing patterns with enhanced scoring"""
        pattern_scores = {}
        found_patterns = {}
        
        # Define category weights for better scoring
        category_weights = {
            "lottery_scams": 0.5,      # High weight for lottery scams
            "urgency": 0.4,            # High weight for urgency
            "authority": 0.3,          # Medium-high weight for authority
            "payment": 0.4,            # High weight for payment-related
            "phishing_links": 0.6,     # Very high weight for suspicious links
            "suspicious_domains": 0.7, # Very high weight for suspicious domains
            "threats": 0.5,            # High weight for threats
            "personal_info": 0.4,      # High weight for personal info requests
            "spoofing": 0.5,           # High weight for spoofing
            "fake_legitimacy": -0.2    # Negative weight - reduces false positives
        }
        
        for category, patterns in self.compiled_patterns.items():
            found_patterns[category] = []
            score = 0.0
            
            for pattern in patterns:
                matches = pattern.findall(content)
                if matches:
                    found_patterns[category].extend(matches)
                    # Use category-specific scoring
                    base_score = len(matches) * 0.3
                    weight = category_weights.get(category, 0.3)
                    score += base_score * weight
            
            pattern_scores[category] = min(score, 1.0)  # Cap at 1.0
        
        # Calculate weighted pattern score instead of simple average
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for category, score in pattern_scores.items():
            weight = abs(category_weights.get(category, 0.3))  # Use absolute value for weighting
            total_weighted_score += score * weight
            total_weight += weight
        
        total_pattern_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        
        return {
            "pattern_scores": pattern_scores,
            "found_patterns": found_patterns,
            "total_pattern_score": total_pattern_score,
            "high_risk_categories": [cat for cat, score in pattern_scores.items() if score > 0.2]
        }
    
    async def _analyze_statistics(self, content: str) -> Dict[str, Any]:
        """Analyze statistical features of the email"""
        # Content length analysis
        length = len(content)
        word_count = len(content.split())
        
        # Character analysis
        uppercase_ratio = sum(1 for c in content if c.isupper()) / len(content) if content else 0
        digit_ratio = sum(1 for c in content if c.isdigit()) / len(content) if content else 0
        special_char_ratio = sum(1 for c in content if not c.isalnum() and not c.isspace()) / len(content) if content else 0
        
        # Email-specific features
        exclamation_count = content.count('!')
        question_count = content.count('?')
        link_count = len(re.findall(r'http[s]?://[^\s]+', content))
        
        # Suspicious patterns
        excessive_caps = uppercase_ratio > 0.2
        excessive_digits = digit_ratio > 0.15
        excessive_special = special_char_ratio > 0.08
        excessive_exclamations = exclamation_count > 3
        excessive_links = link_count > 2
        very_short = length < 50
        very_long = length > 2000
        
        # Calculate statistical risk score
        risk_factors = [excessive_caps, excessive_digits, excessive_special, 
                       excessive_exclamations, excessive_links, very_short, very_long]
        statistical_score = sum(risk_factors) / len(risk_factors)
        
        return {
            "length": length,
            "word_count": word_count,
            "uppercase_ratio": uppercase_ratio,
            "digit_ratio": digit_ratio,
            "special_char_ratio": special_char_ratio,
            "exclamation_count": exclamation_count,
            "question_count": question_count,
            "link_count": link_count,
            "excessive_caps": excessive_caps,
            "excessive_digits": excessive_digits,
            "excessive_special": excessive_special,
            "excessive_exclamations": excessive_exclamations,
            "excessive_links": excessive_links,
            "very_short": very_short,
            "very_long": very_long,
            "statistical_score": statistical_score
        }
    
    async def _analyze_sender(self, sender_email: Optional[str]) -> Dict[str, Any]:
        """Analyze sender email for suspicious patterns"""
        if not sender_email:
            return {"score": 0.0, "reputation": "unknown", "reasons": []}
        
        score = 0.0
        reasons = []
        
        # Check for suspicious domains
        if '@' in sender_email:
            domain = sender_email.split('@')[1].lower()
            
            # Check for suspicious TLDs
            suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.cc', '.info', '.gq', '.top']
            if any(domain.endswith(tld) for tld in suspicious_tlds):
                score += 0.4
                reasons.append(f"Suspicious TLD: {domain}")
            
            # Check for free email providers
            free_providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com']
            if domain in free_providers:
                score += 0.1
                reasons.append(f"Free email provider: {domain}")
            
            # Check for legitimate domains
            legitimate_domains = ['microsoft.com', 'apple.com', 'google.com', 'amazon.com', 
                                'paypal.com', 'ebay.com', 'facebook.com', 'irs.gov']
            if domain in legitimate_domains:
                score -= 0.2
                reasons.append(f"Legitimate domain: {domain}")
        
        # Check for suspicious patterns in email
        if re.search(r'[0-9]{10,}', sender_email):  # Long number sequences
            score += 0.3
            reasons.append("Long number sequence in email")
        
        if re.search(r'[^a-zA-Z0-9@.]', sender_email):  # Special characters
            score += 0.2
            reasons.append("Special characters in email")
        
        return {
            "score": min(score, 1.0),
            "reputation": "suspicious" if score > 0.3 else "legitimate" if score < -0.1 else "neutral",
            "reasons": reasons
        }
    
    async def _analyze_links(self, body: str) -> Dict[str, Any]:
        """Analyze links in email body for phishing indicators"""
        # Extract all URLs
        urls = re.findall(r'http[s]?://[^\s]+', body)
        
        if not urls:
            return {"score": 0.0, "suspicious_links": [], "reasons": []}
        
        score = 0.0
        suspicious_links = []
        reasons = []
        
        for url in urls:
            link_score = 0.0
            link_reasons = []
            
            # Check for URL shorteners
            shorteners = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'short.link', 'is.gd']
            if any(shortener in url.lower() for shortener in shorteners):
                link_score += 0.4
                link_reasons.append("URL shortener detected")
            
            # Check for suspicious domains
            suspicious_domains = ['.tk', '.ml', '.ga', '.cf', '.cc', '.info']
            if any(domain in url.lower() for domain in suspicious_domains):
                link_score += 0.5
                link_reasons.append("Suspicious domain")
            
            # Check for phishing keywords in URL
            phishing_keywords = ['click', 'verify', 'confirm', 'update', 'secure', 'login']
            if any(keyword in url.lower() for keyword in phishing_keywords):
                link_score += 0.3
                link_reasons.append("Phishing keywords in URL")
            
            if link_score > 0.2:
                suspicious_links.append({
                    "url": url,
                    "score": link_score,
                    "reasons": link_reasons
                })
                score += link_score
        
        # Normalize score
        score = min(score / len(urls), 1.0)
        
        return {
            "score": score,
            "suspicious_links": suspicious_links,
            "reasons": reasons
        }
    
    def _calculate_risk_score(self, phishing_classification: Dict, pattern_analysis: Dict, 
                            statistical_analysis: Dict, sender_analysis: Dict, link_analysis: Dict) -> float:
        """Calculate overall risk score with enhanced logic"""
        # Enhanced weighted combination with dynamic adjustments
        base_weights = {
            "phishing_classification": 0.35,  # Slightly reduced
            "pattern_analysis": 0.35,         # Increased for better pattern detection
            "statistical_analysis": 0.1,      # Keep low
            "sender_analysis": 0.1,           # Keep low
            "link_analysis": 0.1              # Keep low
        }
        
        # Phishing classification score with confidence boost
        if phishing_classification["is_phishing"]:
            phishing_score = phishing_classification["confidence"]
            # Boost confidence for high-confidence predictions
            if phishing_score > 0.8:
                phishing_score = min(phishing_score * 1.1, 1.0)
        else:
            phishing_score = 0.0
        
        # Pattern analysis score
        pattern_score = pattern_analysis["total_pattern_score"]
        
        # Statistical analysis score
        statistical_score = statistical_analysis["statistical_score"]
        
        # Sender analysis score
        sender_score = sender_analysis["score"]
        
        # Link analysis score
        link_score = link_analysis["score"]
        
        # Apply dynamic weight adjustments based on content
        weights = base_weights.copy()
        
        # If high pattern score, increase pattern weight
        if pattern_score > 0.3:
            weights["pattern_analysis"] = 0.45
            weights["phishing_classification"] = 0.3
        
        # If suspicious links, increase link weight
        if link_score > 0.5:
            weights["link_analysis"] = 0.2
            weights["phishing_classification"] = 0.3
        
        # If suspicious sender, increase sender weight
        if sender_score > 0.5:
            weights["sender_analysis"] = 0.2
            weights["phishing_classification"] = 0.3
        
        # Calculate weighted average
        risk_score = (
            weights["phishing_classification"] * phishing_score +
            weights["pattern_analysis"] * pattern_score +
            weights["statistical_analysis"] * statistical_score +
            weights["sender_analysis"] * sender_score +
            weights["link_analysis"] * link_score
        )
        
        # Apply bonus for multiple high-risk indicators (with proper normalization)
        high_risk_indicators = 0
        if phishing_score > 0.7: high_risk_indicators += 1
        if pattern_score > 0.4: high_risk_indicators += 1
        if link_score > 0.6: high_risk_indicators += 1
        if sender_score > 0.6: high_risk_indicators += 1
        
        # Apply bonus with proper normalization to prevent overflow
        if high_risk_indicators >= 2:
            bonus_factor = 1.0 + (0.15 * (high_risk_indicators - 1))  # Graduated bonus
            risk_score = risk_score * bonus_factor
        
        # Reduce false positives for legitimate business emails
        if (phishing_classification["predicted_label"] in ["legitimate", "business"] and 
            phishing_classification["confidence"] > 0.6 and
            pattern_score < 0.3 and
            link_score < 0.3):
            risk_score = risk_score * 0.5  # Reduce risk score by 50% for legitimate business emails
        
        # Ensure score is properly normalized between 0 and 1
        risk_score = max(0.0, min(risk_score, 1.0))
        
        # Debug logging
        print(f"DEBUG: Risk calculation - Phishing: {phishing_score:.3f}, Pattern: {pattern_score:.3f}, Statistical: {statistical_score:.3f}, Sender: {sender_score:.3f}, Link: {link_score:.3f}")
        print(f"DEBUG: Final risk score: {risk_score:.3f}")
        
        return risk_score
    
    def _determine_risk_level(self, risk_score: float) -> Tuple[str, bool]:
        """Determine risk level and phishing status with optimized thresholds"""
        # Optimized thresholds for better accuracy
        if risk_score >= 0.25:  # Lowered for better phishing detection
            return "HIGH", True
        elif risk_score >= 0.12:  # Lowered for better medium-risk detection
            return "MEDIUM", True
        else:
            return "LOW", False
    
    def _generate_explanation(self, phishing_classification: Dict, pattern_analysis: Dict,
                            statistical_analysis: Dict, sender_analysis: Dict, link_analysis: Dict) -> str:
        """Generate human-readable explanation"""
        explanations = []
        
        # Phishing classification explanation
        if phishing_classification["is_phishing"] and phishing_classification["confidence"] > 0.7:
            explanations.append(f"AI detected phishing with {phishing_classification['confidence']:.1%} confidence")
        
        # Pattern analysis explanation
        high_risk_categories = pattern_analysis["high_risk_categories"]
        if high_risk_categories:
            explanations.append(f"High-risk patterns detected: {', '.join(high_risk_categories)}")
        
        # Statistical analysis explanation
        if statistical_analysis["excessive_caps"]:
            explanations.append("Excessive use of capital letters")
        if statistical_analysis["excessive_links"]:
            explanations.append("Excessive number of links")
        if statistical_analysis["excessive_exclamations"]:
            explanations.append("Excessive use of exclamation marks")
        
        # Sender analysis explanation
        if sender_analysis["reasons"]:
            explanations.append(f"Sender issues: {'; '.join(sender_analysis['reasons'])}")
        
        # Link analysis explanation
        if link_analysis["suspicious_links"]:
            explanations.append(f"Suspicious links detected: {len(link_analysis['suspicious_links'])}")
        
        return ". ".join(explanations) if explanations else "No significant phishing indicators detected"
    
    def _extract_highlighted_tokens(self, content: str, pattern_analysis: Dict) -> List[Dict[str, Any]]:
        """Extract tokens to highlight in UI"""
        highlighted = []
        
        for category, patterns in pattern_analysis["found_patterns"].items():
            for pattern in patterns:
                if pattern.lower() in content.lower():
                    start = content.lower().find(pattern.lower())
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
            if pattern_analysis["pattern_scores"][category] > 0.2:  # Lowered threshold
                triggers.extend(patterns[:3])  # Limit to top 3 per category
        
        return list(set(triggers))  # Remove duplicates
    
    def is_ready(self) -> bool:
        """Check if analyzer is ready"""
        return self.is_initialized
    
    def get_model_info(self) -> str:
        """Get model information"""
        return "facebook/bart-large-mnli (Zero-shot Classification for Email Phishing)"
