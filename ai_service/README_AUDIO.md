# 🔊 Audio Deepfake Detection Integration

This document describes the integration of audio deepfake detection capabilities into the FraudShield AI Service.

## 🎯 Overview

The audio deepfake detection system uses a **CRNNWithAttn** model (ResNet18 + Bi-GRU + Attention) to detect synthetic or artificially generated audio content. This complements the existing SMS, Email, and Chat analysis capabilities.

## 🏗️ Architecture

### Model Details
- **Architecture**: CRNNWithAttn (ResNet18 + Bi-GRU + Attention Pooling)
- **Input**: 2-channel audio, 16kHz sample rate, 4-second segments
- **Processing**: Mel spectrograms (64 mel bins, 780 n_fft, 195 hop_length)
- **Output**: Binary classification (Real/Fake) with confidence score
- **Performance**: 95-97% precision and recall

### Key Components

1. **AudioAnalyzer Service** (`services/audio_analyzer.py`)
   - Handles audio preprocessing and model inference
   - Supports WAV, FLAC, and MP3 formats
   - Processes audio in 4-second segments
   - Returns detailed analysis results

2. **FastAPI Endpoint** (`/analyze/audio`)
   - Accepts audio file uploads
   - Returns structured analysis results
   - Handles file validation and cleanup

3. **Frontend Interface** (`/voice-analysis`)
   - Drag-and-drop audio upload
   - Real-time analysis results
   - Audio preview and metadata display

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd ai_service
pip install -r requirements.txt
```

### 2. Start the Service

```bash
python main.py
```

### 3. Test Audio Analysis

```bash
# Quick test
python quick_audio_test.py

# Full test suite
python test_audio_detection.py
```

### 4. Access Frontend

Navigate to `http://localhost:3000/voice-analysis` to use the web interface.

## 📁 File Structure

```
ai_service/
├── models/
│   └── best_model10.pth          # Pre-trained model weights
├── services/
│   └── audio_analyzer.py         # Audio analysis service
├── test_audio_detection.py       # Comprehensive test suite
├── quick_audio_test.py           # Quick functionality test
└── README_AUDIO.md               # This documentation

fraudshield-frontend/src/
├── app/voice-analysis/
│   └── page.tsx                  # Voice analysis UI
├── services/
│   └── api.ts                    # API integration
└── types/
    └── analysis.ts               # TypeScript types
```

## 🔧 API Usage

### Analyze Audio File

```bash
curl -X POST "http://localhost:8000/analyze/audio" \
  -H "Content-Type: multipart/form-data" \
  -F "audio_file=@your_audio_file.wav"
```

### Response Format

```json
{
  "analysis_id": "audio_20241201_143022_123456",
  "channel": "audio",
  "risk_score": 0.85,
  "risk_level": "HIGH",
  "is_fraud": true,
  "triggers": ["High deepfake probability"],
  "explanation": "Audio appears to be artificially generated (confidence: 0.15)",
  "confidence": 0.15,
  "processing_time": 2.34,
  "timestamp": "2024-12-01T14:30:22.123456",
  "audio_file": "/tmp/audio_file.wav",
  "deepfake_score": 0.85,
  "is_deepfake": true,
  "audio_metadata": {
    "sample_rate": 16000,
    "duration": 4.2,
    "channels": 2,
    "segments_analyzed": 1
  }
}
```

## 🎵 Supported Audio Formats

- **WAV** (recommended)
- **FLAC** (high quality)
- **MP3** (compressed)

### Audio Requirements
- **Sample Rate**: Any (automatically resampled to 16kHz)
- **Channels**: Mono or Stereo (automatically converted to stereo)
- **Duration**: Any length (processed in 4-second segments)
- **File Size**: Maximum 50MB

## 🔍 Analysis Process

1. **File Upload**: Audio file is uploaded via multipart form data
2. **Preprocessing**: 
   - Resample to 16kHz if needed
   - Convert mono to stereo if needed
   - Split into 4-second segments
   - Generate mel spectrograms
3. **Model Inference**: 
   - Process each segment through CRNNWithAttn model
   - Calculate confidence scores
4. **Post-processing**:
   - Average confidence across segments
   - Determine risk level and fraud status
   - Generate explanation and triggers
5. **Response**: Return structured analysis results

## 🧪 Testing

### Test Files
The system includes test audio files:
- `fraud-audio-detection-main/data/Elevanlabs_Fake.wav` - Synthetic audio
- `fraud-audio-detection-main/data/real_audio.flac` - Authentic audio

### Running Tests

```bash
# Quick functionality test
python quick_audio_test.py

# Comprehensive test suite
python test_audio_detection.py

# Test specific functionality
python -c "
import asyncio
from services.audio_analyzer import AudioAnalyzer

async def test():
    analyzer = AudioAnalyzer()
    await analyzer.initialize()
    print(f'Ready: {analyzer.is_ready()}')

asyncio.run(test())
"
```

## 🎛️ Configuration

### Model Parameters
```python
# Audio processing settings
sample_rate = 16000
max_duration = 4  # seconds
n_mels = 64
n_fft = 780
hop_length = 195

# Detection thresholds
deepfake_threshold = 0.4  # Below this = deepfake
high_risk_threshold = 0.2
medium_risk_threshold = 0.4
```

### Performance Tuning
- **GPU Support**: Automatically uses CUDA if available
- **Batch Processing**: Processes multiple segments in parallel
- **Memory Management**: Temporary files are cleaned up automatically

## 🚨 Error Handling

### Common Issues

1. **Model Not Found**
   ```
   FileNotFoundError: Model file not found: models/best_model10.pth
   ```
   **Solution**: Ensure the model file is copied to the correct location

2. **Unsupported Audio Format**
   ```
   HTTPException: Please select a valid audio file (WAV, FLAC, or MP3)
   ```
   **Solution**: Convert audio to supported format

3. **File Too Large**
   ```
   HTTPException: File size must be less than 50MB
   ```
   **Solution**: Compress or split the audio file

4. **CUDA Out of Memory**
   ```
   RuntimeError: CUDA out of memory
   ```
   **Solution**: Use CPU mode or reduce batch size

## 🔒 Security Considerations

- **File Validation**: Only audio files are accepted
- **Size Limits**: 50MB maximum file size
- **Temporary Files**: Automatically cleaned up after processing
- **Input Sanitization**: All file paths are validated

## 📊 Performance Metrics

### Typical Performance
- **Processing Time**: 1-3 seconds per 4-second audio segment
- **Memory Usage**: ~2GB GPU memory (with CUDA)
- **Accuracy**: 95-97% precision and recall
- **Throughput**: ~20-30 files per minute

### Optimization Tips
- Use GPU acceleration when available
- Process multiple files in parallel
- Use compressed audio formats for faster uploads
- Implement caching for repeated analyses

## 🛠️ Troubleshooting

### Service Won't Start
1. Check if all dependencies are installed
2. Verify model file exists
3. Check port availability (8000)

### Analysis Fails
1. Verify audio file format
2. Check file size limits
3. Review error logs

### Frontend Issues
1. Ensure backend is running
2. Check CORS settings
3. Verify API endpoints

## 📈 Future Enhancements

- [ ] Real-time audio streaming analysis
- [ ] Batch processing capabilities
- [ ] Advanced audio preprocessing
- [ ] Model fine-tuning interface
- [ ] Integration with voice synthesis detection
- [ ] Multi-language support
- [ ] Audio quality assessment

## 🤝 Contributing

When contributing to the audio analysis system:

1. Follow the existing code patterns
2. Add comprehensive tests
3. Update documentation
4. Ensure backward compatibility
5. Test with various audio formats

## 📞 Support

For issues or questions regarding audio deepfake detection:

1. Check the troubleshooting section
2. Review error logs
3. Test with provided sample files
4. Create an issue with detailed information

---

**Note**: This audio deepfake detection system is designed to complement the existing FraudShield capabilities and should be used as part of a comprehensive fraud detection strategy.
