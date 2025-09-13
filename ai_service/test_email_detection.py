#!/usr/bin/env python3
"""
Quick test script for Email Phishing Detection Service
"""

import requests
import json
import time

def test_email_detection():
    """Test the email detection service"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Email Phishing Detection Service")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service is healthy: {data['status']}")
            print(f"   Text Analyzer: {'Ready' if data['services']['text_analyzer'] else 'Not Ready'}")
            print(f"   SMS Analyzer: {'Ready' if data['services']['sms_analyzer'] else 'Not Ready'}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to service: {str(e)}")
        print("   Make sure to run: python main.py")
        return False
    
    # Test 2: Phishing email detection
    print("\n2️⃣ Testing phishing email detection...")
    phishing_email = {
        "subject": "URGENT: Your account has been compromised!",
        "body": "Dear Customer,\n\nWe have detected suspicious activity on your account. Please verify your identity immediately by clicking the link below:\n\nhttps://bank-verify.com/secure\n\nIf you do not verify within 24 hours, your account will be suspended.\n\nBest regards,\nSecurity Team",
        "sender_email": "security@bank-verify.com"
    }
    
    try:
        response = requests.post(
            f"{base_url}/analyze/email",
            json=phishing_email,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Phishing detected: {data['is_fraud']}")
            print(f"   Risk Score: {data['risk_score']:.3f}")
            print(f"   Risk Level: {data['risk_level']}")
            print(f"   Triggers: {', '.join(data['triggers'][:3])}")
            print(f"   Processing Time: {data['processing_time']:.3f}s")
        else:
            print(f"❌ Phishing detection failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Phishing detection error: {str(e)}")
        return False
    
    # Test 3: Legitimate email detection
    print("\n3️⃣ Testing legitimate email detection...")
    legitimate_email = {
        "subject": "Account Statement Available",
        "body": "Dear Customer,\n\nYour monthly account statement is now available online. You can view it by logging into your account at https://www.bankofamerica.com or by calling us at 1-800-555-0123.\n\nThank you for banking with us.\n\nBank of America Customer Service",
        "sender_email": "noreply@bankofamerica.com"
    }
    
    try:
        response = requests.post(
            f"{base_url}/analyze/email",
            json=legitimate_email,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Legitimate email: {not data['is_fraud']}")
            print(f"   Risk Score: {data['risk_score']:.3f}")
            print(f"   Risk Level: {data['risk_level']}")
            print(f"   Processing Time: {data['processing_time']:.3f}s")
        else:
            print(f"❌ Legitimate detection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Legitimate detection error: {str(e)}")
        return False
    
    # Test 4: Data simulation
    print("\n4️⃣ Testing email data simulation...")
    try:
        response = requests.get(f"{base_url}/simulate/data?count=5&channel=email", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Generated {len(data['data'])} test emails")
            phishing_count = sum(1 for item in data['data'] if item['is_phishing'])
            print(f"   Phishing emails: {phishing_count}")
            print(f"   Legitimate emails: {len(data['data']) - phishing_count}")
        else:
            print(f"❌ Data simulation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Data simulation error: {str(e)}")
        return False
    
    print("\n🎉 All tests passed! Your email phishing detection service is working correctly.")
    return True

if __name__ == "__main__":
    success = test_email_detection()
    if not success:
        print("\n💥 Some tests failed. Please check the service and try again.")
        exit(1)
