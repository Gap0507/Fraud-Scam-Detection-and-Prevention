#!/usr/bin/env python3
"""
Quick test script for SMS Fraud Detection Service
"""

import requests
import json
import time

def test_sms_detection():
    """Test the SMS detection service"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing SMS Fraud Detection Service")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service is healthy: {data['status']}")
            print(f"   Text Analyzer: {'Ready' if data['services']['text_analyzer'] else 'Not Ready'}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to service: {str(e)}")
        print("   Make sure to run: python main.py")
        return False
    
    # Test 2: Scam message detection
    print("\n2️⃣ Testing scam message detection...")
    scam_message = "URGENT: You have an outstanding warrant. Call 555-0123 immediately or face arrest!"
    
    try:
        response = requests.post(
            f"{base_url}/analyze/text",
            json={
                "content": scam_message,
                "channel": "sms",
                "sender_info": "555-0123"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Scam detected: {data['is_fraud']}")
            print(f"   Risk Score: {data['risk_score']:.3f}")
            print(f"   Risk Level: {data['risk_level']}")
            print(f"   Triggers: {', '.join(data['triggers'][:3])}")
            print(f"   Processing Time: {data['processing_time']:.3f}s")
        else:
            print(f"❌ Scam detection failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Scam detection error: {str(e)}")
        return False
    
    # Test 3: Legitimate message detection
    print("\n3️⃣ Testing legitimate message detection...")
    legitimate_message = "Your account balance is $1500. Thank you for banking with us."
    
    try:
        response = requests.post(
            f"{base_url}/analyze/text",
            json={
                "content": legitimate_message,
                "channel": "sms",
                "sender_info": "555-0789"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Legitimate message: {not data['is_fraud']}")
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
    print("\n4️⃣ Testing data simulation...")
    try:
        response = requests.get(f"{base_url}/simulate/data?count=5&channel=sms", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Generated {len(data['data'])} test messages")
            scam_count = sum(1 for item in data['data'] if item['is_scam'])
            print(f"   Scam messages: {scam_count}")
            print(f"   Legitimate messages: {len(data['data']) - scam_count}")
        else:
            print(f"❌ Data simulation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Data simulation error: {str(e)}")
        return False
    
    print("\n🎉 All tests passed! Your SMS fraud detection service is working correctly.")
    return True

if __name__ == "__main__":
    success = test_sms_detection()
    if not success:
        print("\n💥 Some tests failed. Please check the service and try again.")
        exit(1)
