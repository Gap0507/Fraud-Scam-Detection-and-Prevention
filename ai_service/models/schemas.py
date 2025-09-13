"""
Pydantic schemas for FraudShield AI Service
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

class ChannelType(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    CHAT = "chat"
    VOICE = "voice"
    VIDEO = "video"
    MULTI = "multi"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class AnalysisRequest(BaseModel):
    """Base analysis request"""
    content: str = Field(..., description="Content to analyze")
    channel: ChannelType = Field(..., description="Communication channel")
    sender_info: Optional[str] = Field(None, description="Sender information")

class TextAnalysisRequest(AnalysisRequest):
    """Text analysis request"""
    content: str = Field(..., description="Text content to analyze", min_length=1, max_length=10000)
    channel: ChannelType = Field(ChannelType.SMS, description="Text channel type")
    sender_info: Optional[str] = Field(None, description="Sender phone number or email")

class EmailAnalysisRequest(BaseModel):
    """Email analysis request"""
    subject: str = Field(..., description="Email subject", min_length=1, max_length=500)
    body: str = Field(..., description="Email body content", min_length=1, max_length=50000)
    sender_email: Optional[str] = Field(None, description="Sender email address")
    channel: ChannelType = Field(ChannelType.EMAIL, description="Communication channel")

class HighlightedToken(BaseModel):
    """Highlighted token for UI display"""
    text: str = Field(..., description="Token text")
    start: int = Field(..., description="Start position")
    end: int = Field(..., description="End position")
    category: str = Field(..., description="Token category")
    risk_level: str = Field(..., description="Risk level (high/medium/low)")

class AnalysisResult(BaseModel):
    """Base analysis result"""
    analysis_id: str = Field(..., description="Unique analysis ID")
    channel: ChannelType = Field(..., description="Communication channel")
    risk_score: float = Field(..., description="Risk score (0.0 to 1.0)", ge=0.0, le=1.0)
    risk_level: RiskLevel = Field(..., description="Risk level")
    is_fraud: bool = Field(..., description="Whether content is identified as fraud")
    triggers: List[str] = Field(..., description="Trigger phrases that caused the alert")
    explanation: str = Field(..., description="Human-readable explanation")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)", ge=0.0, le=1.0)
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: str = Field(..., description="Analysis timestamp")

class EmailAnalysisResponse(AnalysisResult):
    """Email analysis response"""
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body content")
    highlighted_tokens: List[HighlightedToken] = Field(..., description="Tokens to highlight in UI")
    suspicious_links: List[Dict[str, Any]] = Field(default=[], description="Suspicious links found")
    detailed_analysis: Optional[Dict[str, Any]] = Field(None, description="Detailed analysis breakdown")

class AudioAnalysisRequest(BaseModel):
    """Audio analysis request"""
    audio_file: str = Field(..., description="Audio file path or base64 encoded audio")
    caller_id: Optional[str] = Field(None, description="Caller ID or phone number")
    call_duration: Optional[float] = Field(None, description="Call duration in seconds")

class VoiceAnalysisRequest(BaseModel):
    """Voice analysis request"""
    audio_file: str = Field(..., description="Audio file path or content")
    caller_id: Optional[str] = Field(None, description="Caller ID or phone number")
    call_duration: Optional[float] = Field(None, description="Call duration in seconds")

class VideoAnalysisRequest(BaseModel):
    """Video analysis request"""
    video_file: str = Field(..., description="Video file path or content")
    caller_id: Optional[str] = Field(None, description="Caller ID or phone number")

class TextAnalysisResponse(AnalysisResult):
    """Text analysis response"""
    highlighted_tokens: List[HighlightedToken] = Field(..., description="Tokens to highlight in UI")
    detailed_analysis: Optional[Dict[str, Any]] = Field(None, description="Detailed analysis breakdown")

class AudioAnalysisResponse(AnalysisResult):
    """Audio analysis response"""
    audio_file: str = Field(..., description="Audio file path")
    deepfake_score: float = Field(..., description="Deepfake detection score (0.0 to 1.0)", ge=0.0, le=1.0)
    is_deepfake: bool = Field(..., description="Whether audio is detected as deepfake")
    audio_metadata: Dict[str, Any] = Field(..., description="Audio file metadata")
    detailed_analysis: Optional[Dict[str, Any]] = Field(None, description="Detailed analysis breakdown")

class VoiceAnalysisResponse(AnalysisResult):
    """Voice analysis response"""
    transcript: str = Field(..., description="Speech-to-text transcript")
    spoof_score: float = Field(..., description="Voice spoofing score (0.0 to 1.0)", ge=0.0, le=1.0)
    voice_quality: str = Field(..., description="Voice quality assessment")
    detailed_analysis: Optional[Dict[str, Any]] = Field(None, description="Detailed analysis breakdown")

class VideoAnalysisResponse(AnalysisResult):
    """Video analysis response"""
    deepfake_score: float = Field(..., description="Deepfake detection score (0.0 to 1.0)", ge=0.0, le=1.0)
    face_analysis: Dict[str, Any] = Field(..., description="Face analysis results")
    lip_sync_score: float = Field(..., description="Lip sync score (0.0 to 1.0)", ge=0.0, le=1.0)
    blink_analysis: Dict[str, Any] = Field(..., description="Blink analysis results")
    detailed_analysis: Optional[Dict[str, Any]] = Field(None, description="Detailed analysis breakdown")

class FraudDetectionResponse(AnalysisResult):
    """Multi-channel fraud detection response"""
    overall_risk_score: float = Field(..., description="Overall risk score across all channels")
    channel_results: List[AnalysisResult] = Field(..., description="Results from each channel")

class SMSMessage(BaseModel):
    """SMS message structure"""
    message: str = Field(..., description="SMS message content")
    sender: str = Field(..., description="Sender phone number")
    timestamp: str = Field(..., description="Message timestamp")
    is_scam: bool = Field(..., description="Whether message is a scam")
    scam_type: Optional[str] = Field(None, description="Type of scam if applicable")
    channel: str = Field("sms", description="Communication channel")

class EmailMessage(BaseModel):
    """Email message structure"""
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body content")
    sender: str = Field(..., description="Sender email address")
    timestamp: str = Field(..., description="Message timestamp")
    is_phishing: bool = Field(..., description="Whether email is phishing")
    phishing_type: Optional[str] = Field(None, description="Type of phishing if applicable")
    channel: str = Field("email", description="Communication channel")

class DatasetStatistics(BaseModel):
    """Dataset statistics"""
    total_count: int = Field(..., description="Total number of messages")
    scam_count: int = Field(..., description="Number of scam messages")
    legitimate_count: int = Field(..., description="Number of legitimate messages")
    scam_ratio: float = Field(..., description="Ratio of scam messages")

class ModelInfo(BaseModel):
    """Model information"""
    name: str = Field(..., description="Model name")
    version: str = Field(..., description="Model version")
    accuracy: Optional[float] = Field(None, description="Model accuracy")
    precision: Optional[float] = Field(None, description="Model precision")
    recall: Optional[float] = Field(None, description="Model recall")
    f1_score: Optional[float] = Field(None, description="Model F1 score")

class HealthCheck(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Health check timestamp")
    services: Dict[str, bool] = Field(..., description="Service statuses")

class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    timestamp: str = Field(..., description="Error timestamp")

class BatchAnalysisRequest(BaseModel):
    """Batch analysis request"""
    messages: List[TextAnalysisRequest] = Field(..., description="List of messages to analyze")
    batch_id: Optional[str] = Field(None, description="Batch identifier")

class BatchAnalysisResponse(BaseModel):
    """Batch analysis response"""
    batch_id: str = Field(..., description="Batch identifier")
    results: List[TextAnalysisResponse] = Field(..., description="Analysis results")
    total_count: int = Field(..., description="Total number of messages analyzed")
    scam_count: int = Field(..., description="Number of scam messages detected")
    processing_time: float = Field(..., description="Total processing time in seconds")
    timestamp: str = Field(..., description="Analysis timestamp")

class EvaluationMetrics(BaseModel):
    """Model evaluation metrics"""
    accuracy: float = Field(..., description="Overall accuracy")
    precision: float = Field(..., description="Precision score")
    recall: float = Field(..., description="Recall score")
    f1_score: float = Field(..., description="F1 score")
    false_positive_rate: float = Field(..., description="False positive rate")
    false_negative_rate: float = Field(..., description="False negative rate")
    confusion_matrix: List[List[int]] = Field(..., description="Confusion matrix")
    classification_report: Dict[str, Any] = Field(..., description="Detailed classification report")

class TestResult(BaseModel):
    """Test result for a single message"""
    message: str = Field(..., description="Test message")
    expected_label: bool = Field(..., description="Expected label (True for scam)")
    predicted_label: bool = Field(..., description="Predicted label")
    confidence: float = Field(..., description="Prediction confidence")
    is_correct: bool = Field(..., description="Whether prediction is correct")
    risk_score: float = Field(..., description="Risk score")
    triggers: List[str] = Field(..., description="Trigger phrases")

class ModelEvaluation(BaseModel):
    """Complete model evaluation"""
    model_name: str = Field(..., description="Model name")
    dataset_name: str = Field(..., description="Dataset name")
    test_results: List[TestResult] = Field(..., description="Individual test results")
    metrics: EvaluationMetrics = Field(..., description="Evaluation metrics")
    evaluation_timestamp: str = Field(..., description="Evaluation timestamp")
    total_test_time: float = Field(..., description="Total evaluation time in seconds")
