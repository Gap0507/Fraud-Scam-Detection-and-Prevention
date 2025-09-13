"""
Test suite for SMS Analyzer
"""

import pytest
import asyncio
import json
from datetime import datetime
from services.sms_analyzer import SMSAnalyzer
from services.data_simulator import DataSimulator

class TestSMSAnalyzer:
    """Test cases for SMS Analyzer"""
    
    @pytest.fixture
    async def sms_analyzer(self):
        """Create SMS analyzer instance for testing"""
        analyzer = SMSAnalyzer()
        await analyzer.initialize()
        return analyzer
    
    @pytest.fixture
    def data_simulator(self):
        """Create data simulator instance for testing"""
        return DataSimulator()
    
    @pytest.fixture
    def test_scam_messages(self):
        """Test scam messages"""
        return [
            "URGENT: You have an outstanding warrant. Call 555-0123 immediately or face arrest.",
            "BANK ALERT: Unusual activity detected. Verify account at https://secure-bank.com or account will be closed.",
            "Your OTP is 123456. Do not share with anyone. Valid for 5 minutes.",
            "URGENT: Transfer $1000 to 1234567890 immediately or face consequences.",
            "CONGRATULATIONS! You've won $5000! Call 555-0456 to claim your prize.",
            "IRS ALERT: Tax refund of $2500 pending. Verify at https://irs-gov.com to receive."
        ]
    
    @pytest.fixture
    def test_legitimate_messages(self):
        """Test legitimate messages"""
        return [
            "Your account balance is $1500. Thank you for banking with us.",
            "Reminder: You have an appointment with Dr. Smith on 2024-12-01 at 9:00 AM.",
            "Your package has been delivered to 123 Main St on 2024-12-01.",
            "Your verification code is 789012. This code expires in 10 minutes.",
            "Transaction alert: $50 withdrawn from your account on 2024-12-01.",
            "Your monthly statement is ready. View at https://my-bank.com or call 555-0789."
        ]
    
    @pytest.mark.asyncio
    async def test_analyzer_initialization(self, sms_analyzer):
        """Test analyzer initialization"""
        assert sms_analyzer.is_ready() == True
        assert sms_analyzer.spam_classifier is not None
        assert sms_analyzer.zero_shot_classifier is not None
        assert sms_analyzer.tokenizer is not None
        assert sms_analyzer.model is not None
    
    @pytest.mark.asyncio
    async def test_scam_detection(self, sms_analyzer, test_scam_messages):
        """Test scam message detection"""
        for message in test_scam_messages:
            result = await sms_analyzer.analyze_sms(message, "555-0123")
            
            # Should detect as scam
            assert result["is_scam"] == True
            assert result["risk_level"] in ["MEDIUM", "HIGH"]
            assert result["risk_score"] > 0.5
            assert result["confidence"] > 0.0
            assert len(result["triggers"]) > 0
            assert len(result["explanation"]) > 0
    
    @pytest.mark.asyncio
    async def test_legitimate_detection(self, sms_analyzer, test_legitimate_messages):
        """Test legitimate message detection"""
        for message in test_legitimate_messages:
            result = await sms_analyzer.analyze_sms(message, "555-0789")
            
            # Should detect as legitimate
            assert result["is_scam"] == False
            assert result["risk_level"] in ["LOW", "MEDIUM"]
            assert result["risk_score"] < 0.8
            assert result["confidence"] > 0.0
    
    @pytest.mark.asyncio
    async def test_preprocessing(self, sms_analyzer):
        """Test SMS preprocessing"""
        test_cases = [
            ("Don't call me!", "Do not call me!"),
            ("Call 555-1234 now", "Call [PHONE] now"),
            ("Visit https://example.com", "Visit [URL]"),
            ("Email me at test@example.com", "Email me at [EMAIL]"),
            ("  Multiple   spaces  ", "Multiple spaces")
        ]
        
        for input_text, expected in test_cases:
            processed = sms_analyzer._preprocess_sms(input_text)
            assert processed == expected
    
    @pytest.mark.asyncio
    async def test_pattern_analysis(self, sms_analyzer):
        """Test pattern analysis"""
        test_message = "URGENT: Transfer $1000 immediately or face arrest!"
        result = await sms_analyzer._analyze_patterns(test_message)
        
        assert "urgency" in result["pattern_scores"]
        assert "payment" in result["pattern_scores"]
        assert "threats" in result["pattern_scores"]
        assert result["total_pattern_score"] > 0.5
        assert len(result["high_risk_categories"]) > 0
    
    @pytest.mark.asyncio
    async def test_statistical_analysis(self, sms_analyzer):
        """Test statistical analysis"""
        test_cases = [
            ("Normal message", {"excessive_caps": False, "excessive_digits": False}),
            ("EXCESSIVE CAPS MESSAGE", {"excessive_caps": True, "excessive_digits": False}),
            ("Message with 1234567890", {"excessive_caps": False, "excessive_digits": True}),
            ("Very short", {"very_short": True, "very_long": False}),
            ("This is a very long message that exceeds the normal length and should be flagged as suspicious because it contains too many words and characters which is not typical for SMS messages", {"very_short": False, "very_long": True})
        ]
        
        for message, expected in test_cases:
            result = await sms_analyzer._analyze_statistics(message)
            for key, value in expected.items():
                assert result[key] == value
    
    @pytest.mark.asyncio
    async def test_sender_analysis(self, sms_analyzer):
        """Test sender analysis"""
        test_cases = [
            ("555-0123", {"reputation": "legitimate"}),
            ("1234567890", {"reputation": "legitimate"}),
            ("1111", {"reputation": "suspicious"}),
            ("12345678901", {"reputation": "suspicious"}),
            ("1111222233", {"reputation": "suspicious"})
        ]
        
        for phone, expected in test_cases:
            result = await sms_analyzer._analyze_sender(phone)
            assert result["reputation"] == expected["reputation"]
    
    @pytest.mark.asyncio
    async def test_risk_score_calculation(self, sms_analyzer):
        """Test risk score calculation"""
        # Test high risk scenario
        spam_classification = {"is_spam": True, "confidence": 0.9}
        pattern_analysis = {"total_pattern_score": 0.8}
        statistical_analysis = {"statistical_score": 0.7}
        sender_analysis = {"score": 0.6}
        
        risk_score = sms_analyzer._calculate_risk_score(
            spam_classification, pattern_analysis, statistical_analysis, sender_analysis
        )
        
        assert risk_score > 0.7
        assert risk_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_risk_level_determination(self, sms_analyzer):
        """Test risk level determination"""
        test_cases = [
            (0.9, ("HIGH", True)),
            (0.7, ("HIGH", True)),
            (0.6, ("MEDIUM", False)),
            (0.4, ("MEDIUM", False)),
            (0.3, ("LOW", False))
        ]
        
        for score, expected in test_cases:
            risk_level, is_scam = sms_analyzer._determine_risk_level(score)
            assert risk_level == expected[0]
            assert is_scam == expected[1]
    
    @pytest.mark.asyncio
    async def test_highlighted_tokens(self, sms_analyzer):
        """Test highlighted token extraction"""
        message = "URGENT: Transfer $1000 immediately!"
        pattern_analysis = {
            "found_patterns": {
                "urgency": ["URGENT", "immediately"],
                "payment": ["$1000", "Transfer"]
            },
            "high_risk_categories": ["urgency", "payment"]
        }
        
        highlighted = sms_analyzer._extract_highlighted_tokens(message, pattern_analysis)
        
        assert len(highlighted) > 0
        for token in highlighted:
            assert "text" in token
            assert "start" in token
            assert "end" in token
            assert "category" in token
            assert "risk_level" in token
    
    @pytest.mark.asyncio
    async def test_explanation_generation(self, sms_analyzer):
        """Test explanation generation"""
        spam_classification = {"is_spam": True, "confidence": 0.9}
        pattern_analysis = {
            "high_risk_categories": ["urgency", "payment"],
            "total_pattern_score": 0.8
        }
        statistical_analysis = {"excessive_caps": True, "very_short": False}
        sender_analysis = {"reasons": ["Suspicious pattern"]}
        
        explanation = sms_analyzer._generate_explanation(
            spam_classification, pattern_analysis, statistical_analysis, sender_analysis
        )
        
        assert len(explanation) > 0
        assert "AI detected spam" in explanation or "High-risk patterns" in explanation
    
    @pytest.mark.asyncio
    async def test_end_to_end_analysis(self, sms_analyzer):
        """Test complete end-to-end analysis"""
        message = "URGENT: You have an outstanding warrant. Call 555-0123 immediately or face arrest."
        sender = "555-0123"
        
        result = await sms_analyzer.analyze_sms(message, sender)
        
        # Check required fields
        assert "analysis_id" in result
        assert "channel" in result
        assert "risk_score" in result
        assert "risk_level" in result
        assert "is_scam" in result
        assert "confidence" in result
        assert "triggers" in result
        assert "explanation" in result
        assert "highlighted_tokens" in result
        assert "processing_time" in result
        assert "timestamp" in result
        
        # Check data types
        assert isinstance(result["risk_score"], float)
        assert isinstance(result["is_scam"], bool)
        assert isinstance(result["triggers"], list)
        assert isinstance(result["highlighted_tokens"], list)
        assert isinstance(result["processing_time"], float)
        
        # Check value ranges
        assert 0.0 <= result["risk_score"] <= 1.0
        assert 0.0 <= result["confidence"] <= 1.0
        assert result["processing_time"] > 0.0
    
    @pytest.mark.asyncio
    async def test_performance(self, sms_analyzer):
        """Test performance requirements"""
        message = "URGENT: Transfer $1000 immediately or face arrest!"
        
        start_time = datetime.now()
        result = await sms_analyzer.analyze_sms(message, "555-0123")
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        
        # Should process in less than 2 seconds
        assert processing_time < 2.0
        assert result["processing_time"] < 2.0
    
    @pytest.mark.asyncio
    async def test_batch_analysis(self, sms_analyzer, data_simulator):
        """Test batch analysis performance"""
        # Generate test data
        test_data = await data_simulator.generate_sms_data(count=50, scam_ratio=0.5)
        
        results = []
        start_time = datetime.now()
        
        for item in test_data:
            result = await sms_analyzer.analyze_sms(item["message"], item["sender"])
            results.append(result)
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Should process 50 messages in reasonable time
        assert total_time < 30.0  # 30 seconds for 50 messages
        assert len(results) == 50
        
        # Check accuracy
        correct_predictions = 0
        for i, result in enumerate(results):
            if result["is_scam"] == test_data[i]["is_scam"]:
                correct_predictions += 1
        
        accuracy = correct_predictions / len(results)
        assert accuracy > 0.8  # At least 80% accuracy
    
    @pytest.mark.asyncio
    async def test_error_handling(self, sms_analyzer):
        """Test error handling"""
        # Test empty message
        result = await sms_analyzer.analyze_sms("", "555-0123")
        assert result["is_scam"] == False
        assert result["risk_score"] == 0.0
        
        # Test very long message
        long_message = "This is a very long message. " * 100
        result = await sms_analyzer.analyze_sms(long_message, "555-0123")
        assert "analysis_id" in result
        
        # Test None sender
        result = await sms_analyzer.analyze_sms("Test message", None)
        assert "analysis_id" in result

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
