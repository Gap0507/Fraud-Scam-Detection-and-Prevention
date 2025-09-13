"""
Test suite for Email Analyzer
"""

import pytest
import asyncio
import json
from datetime import datetime
from services.email_analyzer import EmailAnalyzer
from services.email_data_simulator import EmailDataSimulator

class TestEmailAnalyzer:
    """Test cases for Email Analyzer"""
    
    @pytest.fixture
    async def email_analyzer(self):
        """Create Email analyzer instance for testing"""
        analyzer = EmailAnalyzer()
        await analyzer.initialize()
        return analyzer
    
    @pytest.fixture
    def email_data_simulator(self):
        """Create email data simulator instance for testing"""
        return EmailDataSimulator()
    
    @pytest.fixture
    def test_phishing_emails(self):
        """Test phishing emails"""
        return [
            {
                "subject": "URGENT: Your account has been compromised!",
                "body": "Dear Customer,\n\nWe have detected suspicious activity on your account. Please verify your identity immediately by clicking the link below:\n\nhttps://bank-verify.com/secure\n\nIf you do not verify within 24 hours, your account will be suspended.\n\nBest regards,\nSecurity Team"
            },
            {
                "subject": "Microsoft Security Alert - Account Compromised",
                "body": "Microsoft Security Center\n\nWe detected unusual sign-in activity on your Microsoft account. Someone may have accessed your account from an unrecognized device.\n\nLocation: New York, NY\nTime: 2:30 PM\n\nIf this wasn't you, secure your account immediately:\nhttps://microsoft-security.net/login\n\nMicrosoft Security Team"
            },
            {
                "subject": "Congratulations! You've Won $50,000!",
                "body": "Congratulations!\n\nYou have been selected as the winner of our annual lottery! You have won $50,000!\n\nTo claim your prize, please provide your personal information:\nhttps://lottery-claim.tk/winner\n\nThis offer expires in 48 hours. Don't miss out!\n\nLottery Department"
            }
        ]
    
    @pytest.fixture
    def test_legitimate_emails(self):
        """Test legitimate emails"""
        return [
            {
                "subject": "Account Statement Available",
                "body": "Dear Customer,\n\nYour monthly account statement is now available online. You can view it by logging into your account at https://www.bankofamerica.com or by calling us at 1-800-555-0123.\n\nThank you for banking with us.\n\nBank of America Customer Service"
            },
            {
                "subject": "Appointment Reminder - Tomorrow at 2:00 PM",
                "body": "Hello,\n\nThis is a reminder that you have an appointment scheduled for tomorrow at 2:00 PM with Dr. Smith.\n\nPlease arrive 15 minutes early. If you need to reschedule, please call 1-800-555-0456.\n\nThank you,\nCity Medical Center"
            },
            {
                "subject": "Your Package Has Been Delivered",
                "body": "Good news! Your package has been delivered.\n\nTracking Number: 1Z999AA1234567890\nDelivered to: 123 Main St, Anytown, ST 12345\nTime: 3:30 PM\n\nThank you for choosing Amazon!\n\nDelivery Team"
            }
        ]
    
    @pytest.mark.asyncio
    async def test_analyzer_initialization(self, email_analyzer):
        """Test analyzer initialization"""
        assert email_analyzer.is_ready() == True
        assert email_analyzer.zero_shot_classifier is not None
        assert email_analyzer.phishing_classifier is not None
    
    @pytest.mark.asyncio
    async def test_phishing_detection(self, email_analyzer, test_phishing_emails):
        """Test phishing email detection"""
        for email in test_phishing_emails:
            result = await email_analyzer.analyze_email(
                email["subject"], 
                email["body"], 
                "security@bank-verify.com"
            )
            
            # Should detect as phishing
            assert result["is_phishing"] == True
            assert result["risk_level"] in ["MEDIUM", "HIGH"]
            assert result["risk_score"] > 0.3
            assert result["confidence"] > 0.0
            assert len(result["triggers"]) > 0
            assert len(result["explanation"]) > 0
    
    @pytest.mark.asyncio
    async def test_legitimate_detection(self, email_analyzer, test_legitimate_emails):
        """Test legitimate email detection"""
        for email in test_legitimate_emails:
            result = await email_analyzer.analyze_email(
                email["subject"], 
                email["body"], 
                "noreply@bank.com"
            )
            
            # Should detect as legitimate
            assert result["is_phishing"] == False
            assert result["risk_level"] in ["LOW", "MEDIUM"]
            assert result["risk_score"] < 0.8
            assert result["confidence"] > 0.0
    
    @pytest.mark.asyncio
    async def test_preprocessing(self, email_analyzer):
        """Test email preprocessing"""
        test_cases = [
            ("<html><body>Test email</body></html>", "Test email"),
            ("From: test@example.com\nSubject: Test\n\nBody", "Subject: Test\n\nBody"),
            ("Test@example.com", "[EMAIL]"),
            ("Visit https://example.com", "Visit [URL]"),
            ("Call 555-1234", "Call [PHONE]")
        ]
        
        for input_text, expected in test_cases:
            processed = email_analyzer._preprocess_email(input_text)
            assert expected in processed
    
    @pytest.mark.asyncio
    async def test_pattern_analysis(self, email_analyzer):
        """Test pattern analysis"""
        test_subject = "URGENT: Verify your account immediately!"
        test_body = "Click here to verify: https://bank-verify.com"
        
        result = await email_analyzer._analyze_patterns(f"Subject: {test_subject}\n\nBody: {test_body}")
        
        assert "urgency" in result["pattern_scores"]
        assert "phishing_links" in result["pattern_scores"]
        assert result["total_pattern_score"] > 0.3
        assert len(result["high_risk_categories"]) > 0
    
    @pytest.mark.asyncio
    async def test_statistical_analysis(self, email_analyzer):
        """Test statistical analysis"""
        test_cases = [
            ("Normal email", {"excessive_caps": False, "excessive_links": False}),
            ("EXCESSIVE CAPS EMAIL", {"excessive_caps": True, "excessive_links": False}),
            ("Email with https://link1.com and https://link2.com and https://link3.com", 
             {"excessive_links": True, "excessive_caps": False}),
            ("Very short", {"very_short": True, "very_long": False})
        ]
        
        for content, expected in test_cases:
            result = await email_analyzer._analyze_statistics(content)
            for key, value in expected.items():
                assert result[key] == value
    
    @pytest.mark.asyncio
    async def test_sender_analysis(self, email_analyzer):
        """Test sender analysis"""
        test_cases = [
            ("noreply@bank.com", {"reputation": "legitimate"}),
            ("security@bank-verify.tk", {"reputation": "suspicious"}),
            ("support@microsoft.com", {"reputation": "legitimate"}),
            ("alerts@phishing.ml", {"reputation": "suspicious"})
        ]
        
        for email, expected in test_cases:
            result = await email_analyzer._analyze_sender(email)
            assert result["reputation"] == expected["reputation"]
    
    @pytest.mark.asyncio
    async def test_link_analysis(self, email_analyzer):
        """Test link analysis"""
        test_body = "Click here: https://bit.ly/short and https://bank-verify.tk/secure"
        result = await email_analyzer._analyze_links(test_body)
        
        assert result["score"] > 0.0
        assert len(result["suspicious_links"]) > 0
    
    @pytest.mark.asyncio
    async def test_risk_score_calculation(self, email_analyzer):
        """Test risk score calculation"""
        # Test high risk scenario
        phishing_classification = {"is_phishing": True, "confidence": 0.9}
        pattern_analysis = {"total_pattern_score": 0.8}
        statistical_analysis = {"statistical_score": 0.7}
        sender_analysis = {"score": 0.6}
        link_analysis = {"score": 0.5}
        
        risk_score = email_analyzer._calculate_risk_score(
            phishing_classification, pattern_analysis, statistical_analysis, 
            sender_analysis, link_analysis
        )
        
        assert risk_score > 0.7
        assert risk_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_risk_level_determination(self, email_analyzer):
        """Test risk level determination"""
        test_cases = [
            (0.9, ("HIGH", True)),
            (0.7, ("HIGH", True)),
            (0.5, ("MEDIUM", True)),
            (0.3, ("MEDIUM", True)),
            (0.2, ("LOW", False))
        ]
        
        for score, expected in test_cases:
            risk_level, is_phishing = email_analyzer._determine_risk_level(score)
            assert risk_level == expected[0]
            assert is_phishing == expected[1]
    
    @pytest.mark.asyncio
    async def test_highlighted_tokens(self, email_analyzer):
        """Test highlighted token extraction"""
        content = "URGENT: Click here to verify your account!"
        pattern_analysis = {
            "found_patterns": {
                "urgency": ["URGENT"],
                "phishing_links": ["verify"]
            },
            "high_risk_categories": ["urgency"]
        }
        
        highlighted = email_analyzer._extract_highlighted_tokens(content, pattern_analysis)
        
        assert len(highlighted) > 0
        for token in highlighted:
            assert "text" in token
            assert "start" in token
            assert "end" in token
            assert "category" in token
            assert "risk_level" in token
    
    @pytest.mark.asyncio
    async def test_explanation_generation(self, email_analyzer):
        """Test explanation generation"""
        phishing_classification = {"is_phishing": True, "confidence": 0.9}
        pattern_analysis = {
            "high_risk_categories": ["urgency", "phishing_links"],
            "total_pattern_score": 0.8
        }
        statistical_analysis = {"excessive_caps": True, "excessive_links": False}
        sender_analysis = {"reasons": ["Suspicious domain"]}
        link_analysis = {"suspicious_links": [{"url": "test.com", "score": 0.5, "reasons": []}]}
        
        explanation = email_analyzer._generate_explanation(
            phishing_classification, pattern_analysis, statistical_analysis, 
            sender_analysis, link_analysis
        )
        
        assert len(explanation) > 0
        assert "AI detected phishing" in explanation or "High-risk patterns" in explanation
    
    @pytest.mark.asyncio
    async def test_end_to_end_analysis(self, email_analyzer):
        """Test complete end-to-end analysis"""
        subject = "URGENT: Your account has been compromised!"
        body = "Dear Customer,\n\nWe have detected suspicious activity on your account. Please verify your identity immediately by clicking the link below:\n\nhttps://bank-verify.com/secure\n\nIf you do not verify within 24 hours, your account will be suspended.\n\nBest regards,\nSecurity Team"
        sender = "security@bank-verify.com"
        
        result = await email_analyzer.analyze_email(subject, body, sender)
        
        # Check required fields
        assert "analysis_id" in result
        assert "channel" in result
        assert "risk_score" in result
        assert "risk_level" in result
        assert "is_phishing" in result
        assert "confidence" in result
        assert "triggers" in result
        assert "explanation" in result
        assert "highlighted_tokens" in result
        assert "processing_time" in result
        assert "timestamp" in result
        assert "subject" in result
        assert "body" in result
        
        # Check data types
        assert isinstance(result["risk_score"], float)
        assert isinstance(result["is_phishing"], bool)
        assert isinstance(result["triggers"], list)
        assert isinstance(result["highlighted_tokens"], list)
        assert isinstance(result["processing_time"], float)
        
        # Check value ranges
        assert 0.0 <= result["risk_score"] <= 1.0
        assert 0.0 <= result["confidence"] <= 1.0
        assert result["processing_time"] > 0.0
    
    @pytest.mark.asyncio
    async def test_performance(self, email_analyzer):
        """Test performance requirements"""
        subject = "URGENT: Verify your account immediately!"
        body = "Click here to verify: https://bank-verify.com/secure"
        
        start_time = datetime.now()
        result = await email_analyzer.analyze_email(subject, body, "security@bank-verify.com")
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        
        # Should process in less than 3 seconds
        assert processing_time < 3.0
        assert result["processing_time"] < 3.0
    
    @pytest.mark.asyncio
    async def test_batch_analysis(self, email_analyzer, email_data_simulator):
        """Test batch analysis performance"""
        # Generate test data
        test_data = await email_data_simulator.generate_email_data(count=20, phishing_ratio=0.5)
        
        results = []
        start_time = datetime.now()
        
        for item in test_data:
            result = await email_analyzer.analyze_email(
                item["subject"], 
                item["body"], 
                item["sender"]
            )
            results.append(result)
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Should process 20 emails in reasonable time
        assert total_time < 60.0  # 60 seconds for 20 emails
        assert len(results) == 20
        
        # Check accuracy
        correct_predictions = 0
        for i, result in enumerate(results):
            if result["is_phishing"] == test_data[i]["is_phishing"]:
                correct_predictions += 1
        
        accuracy = correct_predictions / len(results)
        assert accuracy > 0.7  # At least 70% accuracy
    
    @pytest.mark.asyncio
    async def test_error_handling(self, email_analyzer):
        """Test error handling"""
        # Test empty subject and body
        result = await email_analyzer.analyze_email("", "", "test@example.com")
        assert result["is_phishing"] == False
        assert result["risk_score"] == 0.0
        
        # Test very long content
        long_subject = "This is a very long subject. " * 50
        long_body = "This is a very long body. " * 1000
        result = await email_analyzer.analyze_email(long_subject, long_body, "test@example.com")
        assert "analysis_id" in result
        
        # Test None sender
        result = await email_analyzer.analyze_email("Test subject", "Test body", None)
        assert "analysis_id" in result

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
