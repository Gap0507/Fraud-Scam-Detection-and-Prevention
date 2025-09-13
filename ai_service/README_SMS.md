# SMS Fraud Detection Service

A lightweight AI-powered service for detecting SMS scams and fraud attempts using machine learning and pattern analysis.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Option 1: Use the installer script
python install_dependencies.py

# Option 2: Manual installation
pip install -r requirements.txt
```

### 2. Start the Service
```bash
python main.py
```

The service will start on `http://localhost:8000`

### 3. Test the Service
```bash
# Run automated tests
python test_sms_detection.py

# Or test manually with curl
curl -X POST "http://localhost:8000/analyze/text" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "URGENT: You have an outstanding warrant. Call 555-0123 immediately!",
    "channel": "sms",
    "sender_info": "555-0123"
  }'
```

## 📊 API Endpoints

### Health Check
```bash
GET /health
```

### Text Analysis
```bash
POST /analyze/text
Content-Type: application/json

{
  "content": "Your SMS message here",
  "channel": "sms",
  "sender_info": "555-0123"
}
```

### Data Simulation
```bash
GET /simulate/data?count=10&channel=sms
```

### Model Status
```bash
GET /models/status
```

## 🔍 How It Works

The SMS fraud detection uses a **multi-layered approach**:

1. **Preprocessing**: Cleans and normalizes text
2. **AI Classification**: Uses pre-trained models for spam detection
3. **Pattern Analysis**: Detects urgency, threats, authority impersonation
4. **Statistical Analysis**: Analyzes message characteristics
5. **Sender Analysis**: Validates phone number patterns
6. **Risk Scoring**: Combines all factors for final decision

## 🎯 Detection Capabilities

**Scam Types Detected:**
- Arrest/Warrant scams
- Bank account suspension
- OTP/Verification code scams
- Payment/Transfer requests
- Prize/Lottery scams
- Tax/IRS scams

**Pattern Detection:**
- Urgency language ("urgent", "immediately")
- Threatening language ("arrest", "legal action")
- Authority impersonation ("police", "FBI", "IRS")
- Payment requests ("transfer", "wire", "bitcoin")

## 📈 Response Format

```json
{
  "analysis_id": "text_20241201_103000_123456",
  "channel": "sms",
  "risk_score": 0.85,
  "risk_level": "HIGH",
  "is_fraud": true,
  "triggers": ["URGENT", "warrant", "arrest"],
  "explanation": "AI detected spam with 0.9 confidence...",
  "highlighted_tokens": [...],
  "confidence": 0.9,
  "processing_time": 0.5,
  "timestamp": "2024-12-01T10:30:00.123456"
}
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
python run_tests.py
```

This will test:
- Basic functionality
- Scam detection accuracy
- Legitimate message handling
- Performance benchmarks
- Error handling

## 🔧 Troubleshooting

**Common Issues:**

1. **Service won't start**: Check if port 8000 is available
2. **Model loading errors**: Ensure all dependencies are installed
3. **Slow performance**: First run downloads models (one-time)
4. **Memory issues**: Close other applications if needed

**Error Messages:**
- `AttributeError: 'MessageFactory' object has no attribute 'GetPrototype'`: This is a known issue with some dependencies, but doesn't affect functionality
- `ModuleNotFoundError`: Run `pip install -r requirements.txt`

## 📝 Dependencies

- **FastAPI**: Web framework
- **Transformers**: AI models
- **PyTorch**: Deep learning
- **scikit-learn**: Machine learning utilities
- **Pydantic**: Data validation
- **NumPy**: Numerical computing

## 🎉 Success!

Your SMS fraud detection service is now ready to protect users from scam messages!
