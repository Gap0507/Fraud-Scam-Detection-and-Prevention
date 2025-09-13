# Gemini 2.5 Pro Integration

This document explains how to set up and use the Gemini 2.5 Pro integration for deepfake detection.

## Setup

1. **Get Gemini API Key**
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Create a new project or use an existing one
   - Generate an API key for Gemini 2.5 Pro

2. **Set Environment Variable**
   ```bash
   export GEMINI_API_KEY=your_api_key_here
   ```
   
   Or create a `.env` file in the `ai_service` directory:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

3. **Install Dependencies**
   ```bash
   pip install google-generativeai==0.3.2
   ```

## Features

### Audio Analysis
- **Endpoint**: `POST /analyze/audio/gemini`
- **Input**: Audio file (WAV, FLAC, MP3)
- **Output**: Deepfake detection with confidence score and explanation

### Video Analysis
- **Endpoint**: `POST /analyze/video/gemini`
- **Input**: Video file (MP4, AVI, MOV, WebM)
- **Output**: Deepfake detection with detailed analysis

### Model Comparison
- **Endpoint**: `POST /analyze/compare`
- **Input**: Audio file
- **Output**: Side-by-side comparison of custom model vs Gemini

## API Response Format

```json
{
  "analysis_id": "gemini_audio_20241201_123456_789",
  "channel": "voice",
  "deepfake_score": 0.85,
  "is_deepfake": true,
  "confidence": 0.92,
  "risk_level": "HIGH",
  "risk_score": 0.85,
  "is_fraud": true,
  "triggers": ["Synthetic voice patterns", "Unnatural speech rhythm"],
  "explanation": "Audio appears to be artificially generated with high confidence",
  "processing_time": 2.34,
  "timestamp": "2024-12-01T12:34:56.789Z",
  "audio_metadata": {
    "file_size": 1024000,
    "file_type": ".wav",
    "analysis_method": "gemini_2_5_pro"
  },
  "gemini_analysis": {
    "raw_response": "...",
    "model_used": "gemini-2.0-flash-exp",
    "analysis_type": "deepfake_detection"
  }
}
```

## Frontend Integration

The frontend includes a new "Voice Channels" page that provides:

1. **Audio Analysis Tab**: Upload audio files for analysis
2. **Video Analysis Tab**: Upload video files for analysis  
3. **Compare Models Tab**: Side-by-side comparison of both AI models

### Key Features
- Drag and drop file upload
- Real-time audio playback
- Live transcription
- Side-by-side model comparison
- Detailed analysis results with confidence scores

## Performance Comparison

| Model | Processing Time | Accuracy | Use Case |
|-------|----------------|----------|----------|
| Custom CRNN | ~1-2s | High | Real-time analysis |
| Gemini 2.5 Pro | ~2-5s | Very High | Detailed analysis |

## Troubleshooting

### Common Issues

1. **API Key Not Set**
   - Error: "Gemini analyzer not initialized"
   - Solution: Set GEMINI_API_KEY environment variable

2. **File Size Too Large**
   - Error: "File size must be less than 50MB"
   - Solution: Compress or split large files

3. **Unsupported File Format**
   - Error: "Please select a valid audio/video file"
   - Solution: Use supported formats (WAV, FLAC, MP3, MP4, AVI, MOV, WebM)

### Debug Mode

Enable debug logging to see detailed analysis:
```python
import logging
logging.getLogger('ai_service.services.gemini_analyzer').setLevel(logging.DEBUG)
```

## Security Notes

- API keys are sensitive and should be stored securely
- File uploads are temporarily stored and automatically cleaned up
- All analysis is performed locally after file upload
- No data is permanently stored on the server

## Future Enhancements

- Batch processing for multiple files
- Real-time streaming analysis
- Custom model training with Gemini insights
- Advanced video analysis with frame-by-frame detection
