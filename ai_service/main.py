"""
FraudShield AI Service - Multi-Channel Digital Fraud Detection
Main FastAPI application with AI endpoints for text, voice, and video analysis
"""

from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime
import re

from services.text_analyzer import TextAnalyzer
from services.sms_analyzer import SMSAnalyzer
from services.email_analyzer import EmailAnalyzer
from services.chat_analyzer import ChatAnalyzer
from services.data_simulator import DataSimulator
from services.email_data_simulator import EmailDataSimulator
from models.schemas import (
    TextAnalysisRequest, TextAnalysisResponse,
    EmailAnalysisRequest, EmailAnalysisResponse,
    FraudDetectionResponse, AnalysisResult
)
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FraudShield AI Service",
    description="Multi-Channel Digital Fraud Detection and Prevention API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI services
text_analyzer = TextAnalyzer()
sms_analyzer = SMSAnalyzer()
email_analyzer = EmailAnalyzer()
chat_analyzer = ChatAnalyzer()
data_simulator = DataSimulator()
email_data_simulator = EmailDataSimulator()

@app.on_event("startup")
async def startup_event():
    """Initialize AI models on startup"""
    logger.info("Initializing AI models...")
    try:
        await text_analyzer.initialize()
        logger.info("Text analyzer initialized")
    except Exception as e:
        logger.error(f"Text analyzer initialization failed: {e}")
    
    try:
        await sms_analyzer.initialize()
        logger.info("SMS analyzer initialized")
    except Exception as e:
        logger.error(f"SMS analyzer initialization failed: {e}")
    
    try:
        await email_analyzer.initialize()
        logger.info("Email analyzer initialized")
    except Exception as e:
        logger.error(f"Email analyzer initialization failed: {e}")
    
    try:
        await chat_analyzer.initialize()
        logger.info("Chat analyzer initialized")
    except Exception as e:
        logger.error(f"Chat analyzer initialization failed: {e}")
    
    logger.info("AI models initialization completed")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "FraudShield AI Service is running", "timestamp": datetime.utcnow()}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "text_analyzer": text_analyzer.is_ready(),
            "sms_analyzer": sms_analyzer.is_ready(),
            "email_analyzer": email_analyzer.is_ready(),
            "chat_analyzer": chat_analyzer.is_ready()
        },
        "timestamp": datetime.utcnow()
    }

@app.post("/analyze/text", response_model=TextAnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """
    Analyze text content for fraud indicators
    Supports SMS, email, and chat transcripts
    """
    try:
        logger.info(f"Analyzing text: {request.content[:100]}...")
        
        # Always use SMS analyzer for SMS messages
        if request.channel == "sms":
            if not sms_analyzer.is_ready():
                raise HTTPException(status_code=503, detail="SMS analyzer not ready")
            
            result = await sms_analyzer.analyze_sms(
                message=request.content,
                sender_number=request.sender_info
            )
            # Convert SMS result to text analysis format
            result = {
                "analysis_id": result["analysis_id"],
                "channel": "sms",
                "risk_score": result["risk_score"],
                "risk_level": result["risk_level"],
                "is_fraud": result["is_scam"],
                "triggers": result["triggers"],
                "explanation": result["explanation"],
                "highlighted_tokens": result["highlighted_tokens"],
                "confidence": result["confidence"],
                "processing_time": result["processing_time"],
                "timestamp": result["timestamp"]
            }
        else:
            result = await text_analyzer.analyze(
                content=request.content,
                channel=request.channel,
                sender_info=request.sender_info
            )
        
        return TextAnalysisResponse(
            analysis_id=result["analysis_id"],
            channel=result["channel"],
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            is_fraud=result["is_fraud"],
            triggers=result["triggers"],
            explanation=result["explanation"],
            highlighted_tokens=result["highlighted_tokens"],
            confidence=result["confidence"],
            processing_time=result["processing_time"],
            timestamp=result["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Text analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")

@app.post("/analyze/email", response_model=EmailAnalysisResponse)
async def analyze_email(request: EmailAnalysisRequest):
    """
    Analyze email content for phishing indicators
    """
    try:
        logger.info(f"Analyzing email: {request.subject[:50]}...")
        
        if not email_analyzer.is_ready():
            raise HTTPException(status_code=503, detail="Email analyzer not ready")
        
        result = await email_analyzer.analyze_email(
            subject=request.subject,
            body=request.body,
            sender_email=request.sender_email
        )
        
        return EmailAnalysisResponse(
            analysis_id=result["analysis_id"],
            channel=result["channel"],
            subject=result["subject"],
            body=result["body"],
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            is_fraud=result["is_phishing"],
            triggers=result["triggers"],
            explanation=result["explanation"],
            highlighted_tokens=result["highlighted_tokens"],
            suspicious_links=result["detailed_analysis"]["link_analysis"]["suspicious_links"],
            confidence=result["confidence"],
            processing_time=result["processing_time"],
            timestamp=result["timestamp"],
            detailed_analysis=result["detailed_analysis"]
        )
        
    except Exception as e:
        logger.error(f"Email analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Email analysis failed: {str(e)}")

@app.post("/analyze/chat", response_model=TextAnalysisResponse)
async def analyze_chat(request: TextAnalysisRequest):
    """
    Analyze chat conversation for scam indicators
    """
    try:
        logger.info(f"Analyzing chat: {request.content[:100]}...")
        
        if not chat_analyzer.is_ready():
            raise HTTPException(status_code=503, detail="Chat analyzer not ready")
        
        # For chat analysis, we expect the content to be a JSON string of messages
        import json
        try:
            messages = json.loads(request.content)
            if not isinstance(messages, list):
                messages = [request.content]  # Fallback to single message
        except:
            messages = [request.content]  # Fallback to single message
        
        result = await chat_analyzer.analyze_chat(
            messages=messages,
            sender_info=request.sender_info
        )
        
        return TextAnalysisResponse(
            analysis_id=result["analysis_id"],
            channel="chat",
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            is_fraud=result["is_scam"],
            triggers=result["triggers"],
            explanation=result["explanation"],
            highlighted_tokens=result["highlighted_tokens"],
            confidence=result["confidence"],
            processing_time=result["processing_time"],
            timestamp=result["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Chat analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat analysis failed: {str(e)}")

# Voice and video analysis endpoints will be added when those services are implemented

@app.post("/analyze/multi-channel", response_model=FraudDetectionResponse)
async def analyze_multi_channel(
    text_content: Optional[str] = Form(None),
    channel: str = Form("multi"),
    sender_info: Optional[str] = Form(None)
):
    """
    Analyze text content for comprehensive fraud detection
    (Voice and video analysis will be added when those services are implemented)
    """
    try:
        logger.info("Starting multi-channel analysis")
        
        results = []
        overall_risk_score = 0.0
        channel_count = 0
        
        # Analyze text if provided
        if text_content:
            text_result = await text_analyzer.analyze(
                content=text_content,
                channel="text",
                sender_info=sender_info
            )
            results.append(text_result)
            overall_risk_score += text_result["risk_score"]
            channel_count += 1
        
        # Calculate overall risk score
        if channel_count > 0:
            overall_risk_score = overall_risk_score / channel_count
        
        # Determine overall risk level
        if overall_risk_score >= 0.8:
            risk_level = "HIGH"
            is_fraud = True
        elif overall_risk_score >= 0.5:
            risk_level = "MEDIUM"
            is_fraud = False
        else:
            risk_level = "LOW"
            is_fraud = False
        
        return FraudDetectionResponse(
            analysis_id=f"multi_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            channel="multi",
            overall_risk_score=overall_risk_score,
            risk_level=risk_level,
            is_fraud=is_fraud,
            channel_results=results,
            explanation=f"Multi-channel analysis completed. {channel_count} channels analyzed.",
            confidence=min([r["confidence"] for r in results]) if results else 0.0,
            processing_time=sum([r["processing_time"] for r in results]) if results else 0.0,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Multi-channel analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Multi-channel analysis failed: {str(e)}")

@app.get("/simulate/data")
async def simulate_communication_data(
    count: int = 10,
    channel: str = "sms"
):
    """
    Generate simulated communication data for testing
    """
    try:
        logger.info(f"Generating {count} simulated {channel} communications")
        
        if channel == "sms" or channel == "all":
            data = await data_simulator.generate_sms_data(
                count=count,
                scam_ratio=0.5
            )
        elif channel == "email" or channel == "all":
            data = await email_data_simulator.generate_email_data(
                count=count,
                phishing_ratio=0.5
            )
        else:
            data = []
        
        return {
            "message": f"Generated {len(data)} simulated communications",
            "data": data,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Data simulation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data simulation failed: {str(e)}")

@app.post("/analyze/unified")
async def analyze_unified(request: dict):
    """
    Unified analysis endpoint that automatically detects content type and analyzes accordingly.
    Just paste any content and it will smartly detect if it's SMS, Email, or Chat.
    """
    try:
        content = request.get("content", "").strip()
        sender_info = request.get("sender_info", "")
        
        if not content:
            raise HTTPException(
                status_code=400,
                detail="Content is required"
            )
        
        # Smart content type detection
        detected_type = detect_content_type(content)
        
        # Analyze based on detected type
        if detected_type == "email":
            # Parse email content
            lines = content.split('\n')
            subject = lines[0] if lines else "No Subject"
            body = '\n'.join(lines[1:]) if len(lines) > 1 else content
            
            analysis = await email_analyzer.analyze_email(
                subject=subject,
                body=body,
                sender_email=sender_info
            )
            analysis["detected_type"] = "email"
            
        elif detected_type == "chat":
            # Parse chat content
            try:
                # Try to parse as JSON array of messages
                import json
                messages = json.loads(content)
                if isinstance(messages, list):
                    chat_messages = messages
                else:
                    chat_messages = [content]
            except:
                # If not JSON, treat as single message
                chat_messages = [content]
            
            analysis = await chat_analyzer.analyze_chat(
                messages=chat_messages,
                sender_info=sender_info
            )
            analysis["detected_type"] = "chat"
            
        else:  # SMS or general text
            analysis = await sms_analyzer.analyze_sms(
                message=content,
                sender_number=sender_info
            )
            analysis["detected_type"] = "sms"
        
        # Add unified response format
        analysis["unified_analysis"] = True
        analysis["detection_confidence"] = get_detection_confidence(content, detected_type)
        
        return analysis
        
    except Exception as e:
        logger.error(f"Unified analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

def detect_content_type(content: str) -> str:
    """
    Smart content type detection based on patterns and structure.
    Returns: 'email', 'chat', or 'sms'
    """
    content_lower = content.lower()
    
    # Email detection patterns
    email_patterns = [
        r'^subject\s*:',  # Subject: line
        r'^from\s*:',     # From: line
               r'^to\s*:',       # To: line
        r'^cc\s*:',       # CC: line
        r'^bcc\s*:',      # BCC: line
        r'^reply-to\s*:', # Reply-To: line
        r'@\w+\.\w+',     # Email addresses
        r'^dear\s+\w+',   # Dear [Name] greeting
        r'^sincerely',    # Email signature
        r'^best regards', # Email signature
        r'^yours truly',  # Email signature
    ]
    
    # Chat detection patterns
    chat_patterns = [
        r'^\s*\[.*?\]\s*',  # [timestamp] or [username]
        r'^\w+:\s*',        # username: message
        r'^\d{1,2}:\d{2}\s*',  # time format
        r'^\d{1,2}/\d{1,2}/\d{4}',  # date format
        r'^\w+\s+\d{1,2}:\d{2}',  # day time format
        r'^\w+\s+\d{1,2}:\d{2}\s+[AP]M',  # day time AM/PM
    ]
    
    # Check for email patterns
    email_score = 0
    for pattern in email_patterns:
        if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            email_score += 1
    
    # Check for chat patterns
    chat_score = 0
    for pattern in chat_patterns:
        if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            chat_score += 1
    
    # Additional heuristics
    lines = content.split('\n')
    
    # Email heuristics
    if any(line.strip().startswith(('Subject:', 'From:', 'To:', 'CC:', 'BCC:')) for line in lines[:5]):
        email_score += 2
    
    # Chat heuristics
    if len(lines) > 1 and any(':' in line and len(line.split(':')[0]) < 20 for line in lines[:3]):
        chat_score += 2
    
    # Length-based detection
    if len(content) > 1000:  # Long content is likely email
        email_score += 1
    elif len(content) < 200:  # Short content is likely SMS
        email_score -= 1
    
    # Decision logic
    if email_score >= 2:
        return "email"
    elif chat_score >= 2:
        return "chat"
    else:
        return "sms"  # Default to SMS for short, simple content

def get_detection_confidence(content: str, detected_type: str) -> float:
    """Calculate confidence score for content type detection"""
    confidence = 0.5  # Base confidence
    
    if detected_type == "email":
        # Check for strong email indicators
        if re.search(r'^subject\s*:', content, re.MULTILINE | re.IGNORECASE):
            confidence += 0.3
        if re.search(r'@\w+\.\w+', content):
            confidence += 0.2
        if len(content) > 500:
            confidence += 0.1
            
    elif detected_type == "chat":
        # Check for strong chat indicators
        if re.search(r'^\w+:\s*', content, re.MULTILINE):
            confidence += 0.3
        if re.search(r'^\s*\[.*?\]\s*', content, re.MULTILINE):
            confidence += 0.2
        if len(content.split('\n')) > 3:
            confidence += 0.1
            
    else:  # SMS
        # SMS is default, so lower confidence
        if len(content) < 200:
            confidence += 0.2
        if not re.search(r'@\w+\.\w+', content):  # No email addresses
            confidence += 0.1
    
    return min(confidence, 1.0)

@app.get("/models/status")
async def get_models_status():
    """
    Get status of all AI models
    """
    return {
        "text_analyzer": {
            "ready": text_analyzer.is_ready(),
            "model_name": text_analyzer.get_model_info()
        },
        "sms_analyzer": {
            "ready": sms_analyzer.is_ready(),
            "model_name": sms_analyzer.get_model_info()
        },
        "email_analyzer": {
            "ready": email_analyzer.is_ready(),
            "model_name": email_analyzer.get_model_info()
        },
        "chat_analyzer": {
            "ready": chat_analyzer.is_ready(),
            "model_name": chat_analyzer.get_model_info()
        },
        "voice_analyzer": {
            "ready": False,
            "model_name": "Not implemented yet"
        },
        "video_analyzer": {
            "ready": False,
            "model_name": "Not implemented yet"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
