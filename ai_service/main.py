"""
FraudShield AI Service - Multi-Channel Digital Fraud Detection
Main FastAPI application with AI endpoints for text, voice, and video analysis
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

from services.text_analyzer import TextAnalyzer
from services.voice_analyzer import VoiceAnalyzer
from services.video_analyzer import VideoAnalyzer
from services.data_simulator import DataSimulator
from models.schemas import (
    TextAnalysisRequest, TextAnalysisResponse,
    VoiceAnalysisRequest, VoiceAnalysisResponse,
    VideoAnalysisRequest, VideoAnalysisResponse,
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
voice_analyzer = VoiceAnalyzer()
video_analyzer = VideoAnalyzer()
data_simulator = DataSimulator()

@app.on_event("startup")
async def startup_event():
    """Initialize AI models on startup"""
    logger.info("Initializing AI models...")
    await asyncio.gather(
        text_analyzer.initialize(),
        voice_analyzer.initialize(),
        video_analyzer.initialize()
    )
    logger.info("AI models initialized successfully")

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
            "voice_analyzer": voice_analyzer.is_ready(),
            "video_analyzer": video_analyzer.is_ready()
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

@app.post("/analyze/voice", response_model=VoiceAnalysisResponse)
async def analyze_voice(
    audio_file: UploadFile = File(...),
    caller_id: Optional[str] = Form(None),
    call_duration: Optional[float] = Form(None)
):
    """
    Analyze voice content for fraud indicators
    Supports call recordings, voicemail, and voice messages
    """
    try:
        logger.info(f"Analyzing voice file: {audio_file.filename}")
        
        # Save uploaded file temporarily
        audio_content = await audio_file.read()
        
        result = await voice_analyzer.analyze(
            audio_content=audio_content,
            filename=audio_file.filename,
            caller_id=caller_id,
            call_duration=call_duration
        )
        
        return VoiceAnalysisResponse(
            analysis_id=result["analysis_id"],
            channel="voice",
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            is_fraud=result["is_fraud"],
            transcript=result["transcript"],
            spoof_score=result["spoof_score"],
            voice_quality=result["voice_quality"],
            triggers=result["triggers"],
            explanation=result["explanation"],
            confidence=result["confidence"],
            processing_time=result["processing_time"],
            timestamp=result["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Voice analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice analysis failed: {str(e)}")

@app.post("/analyze/video", response_model=VideoAnalysisResponse)
async def analyze_video(
    video_file: UploadFile = File(...),
    caller_id: Optional[str] = Form(None)
):
    """
    Analyze video content for deepfake and fraud indicators
    Supports video calls, recorded videos, and live streams
    """
    try:
        logger.info(f"Analyzing video file: {video_file.filename}")
        
        # Save uploaded file temporarily
        video_content = await video_file.read()
        
        result = await video_analyzer.analyze(
            video_content=video_content,
            filename=video_file.filename,
            caller_id=caller_id
        )
        
        return VideoAnalysisResponse(
            analysis_id=result["analysis_id"],
            channel="video",
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            is_fraud=result["is_fraud"],
            deepfake_score=result["deepfake_score"],
            face_analysis=result["face_analysis"],
            lip_sync_score=result["lip_sync_score"],
            blink_analysis=result["blink_analysis"],
            triggers=result["triggers"],
            explanation=result["explanation"],
            confidence=result["confidence"],
            processing_time=result["processing_time"],
            timestamp=result["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Video analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Video analysis failed: {str(e)}")

@app.post("/analyze/multi-channel", response_model=FraudDetectionResponse)
async def analyze_multi_channel(
    text_content: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    video_file: Optional[UploadFile] = File(None),
    channel: str = Form("multi"),
    sender_info: Optional[str] = Form(None)
):
    """
    Analyze multiple channels simultaneously for comprehensive fraud detection
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
        
        # Analyze audio if provided
        if audio_file:
            audio_content = await audio_file.read()
            voice_result = await voice_analyzer.analyze(
                audio_content=audio_content,
                filename=audio_file.filename,
                caller_id=sender_info
            )
            results.append(voice_result)
            overall_risk_score += voice_result["risk_score"]
            channel_count += 1
        
        # Analyze video if provided
        if video_file:
            video_content = await video_file.read()
            video_result = await video_analyzer.analyze(
                video_content=video_content,
                filename=video_file.filename,
                caller_id=sender_info
            )
            results.append(video_result)
            overall_risk_score += video_result["risk_score"]
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
    channel: str = "all"
):
    """
    Generate simulated communication data for testing
    """
    try:
        logger.info(f"Generating {count} simulated {channel} communications")
        
        data = await data_simulator.generate_data(
            count=count,
            channel=channel
        )
        
        return {
            "message": f"Generated {len(data)} simulated communications",
            "data": data,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Data simulation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data simulation failed: {str(e)}")

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
        "voice_analyzer": {
            "ready": voice_analyzer.is_ready(),
            "model_name": voice_analyzer.get_model_info()
        },
        "video_analyzer": {
            "ready": video_analyzer.is_ready(),
            "model_name": video_analyzer.get_model_info()
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
