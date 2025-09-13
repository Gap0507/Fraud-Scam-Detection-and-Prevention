#!/usr/bin/env python3
"""
Quick test script for Chat Fraud Detection Service
"""

import requests
import json
import time

def test_chat_detection():
    """Test the chat detection service"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Chat Fraud Detection Service")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service is healthy: {data['status']}")
            print(f"   Chat Analyzer: {'Ready' if data['services']['chat_analyzer'] else 'Not Ready'}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to service: {str(e)}")
        print("   Make sure to run: python main.py")
        return False
    
    # Test 2: Romance scam detection
    print("\n2️⃣ Testing romance scam detection...")
    romance_scam_messages = [
        "Hi baby, I'm so glad we met online",
        "I love you so much, we should get married",
        "I need money urgently for my visa to come see you",
        "Please send $2000 via Western Union, I'll pay you back",
        "Don't tell anyone about this, it's our secret"
    ]
    
    try:
        response = requests.post(
            f"{base_url}/analyze/chat",
            json={
                "content": json.dumps(romance_scam_messages),
                "channel": "chat",
                "sender_info": "sweetheart_lover"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Romance scam detected: {data['is_fraud']}")
            print(f"   Risk Score: {data['risk_score']:.3f}")
            print(f"   Risk Level: {data['risk_level']}")
            print(f"   Triggers: {', '.join(data['triggers'][:3])}")
            print(f"   Processing Time: {data['processing_time']:.3f}s")
        else:
            print(f"❌ Romance scam detection failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Romance scam detection error: {str(e)}")
        return False
    
    # Test 3: Investment scam detection
    print("\n3️⃣ Testing investment scam detection...")
    investment_scam_messages = [
        "Hey! I have an exclusive investment opportunity for you",
        "Guaranteed 300% returns in just 30 days",
        "This is a limited time offer, act now!",
        "Send me $5000 and I'll show you how to make millions",
        "Don't miss out on this once-in-a-lifetime chance"
    ]
    
    try:
        response = requests.post(
            f"{base_url}/analyze/chat",
            json={
                "content": json.dumps(investment_scam_messages),
                "channel": "chat",
                "sender_info": "investment_guru"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Investment scam detected: {data['is_fraud']}")
            print(f"   Risk Score: {data['risk_score']:.3f}")
            print(f"   Risk Level: {data['risk_level']}")
            print(f"   Triggers: {', '.join(data['triggers'][:3])}")
            print(f"   Processing Time: {data['processing_time']:.3f}s")
        else:
            print(f"❌ Investment scam detection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Investment scam detection error: {str(e)}")
        return False
    
    # Test 4: Legitimate chat detection
    print("\n4️⃣ Testing legitimate chat detection...")
    legitimate_messages = [
        "Hey, how are you doing today?",
        "I'm good, thanks for asking!",
        "Want to grab coffee later?",
        "Sure, what time works for you?",
        "How about 3 PM at the usual place?"
    ]
    
    try:
        response = requests.post(
            f"{base_url}/analyze/chat",
            json={
                "content": json.dumps(legitimate_messages),
                "channel": "chat",
                "sender_info": "friend123"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Legitimate chat: {not data['is_fraud']}")
            print(f"   Risk Score: {data['risk_score']:.3f}")
            print(f"   Risk Level: {data['risk_level']}")
            print(f"   Processing Time: {data['processing_time']:.3f}s")
        else:
            print(f"❌ Legitimate chat detection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Legitimate chat detection error: {str(e)}")
        return False
    
    # Test 5: Gift card scam detection
    print("\n5️⃣ Testing gift card scam detection...")
    gift_card_scam_messages = [
        "Hi, this is Microsoft support",
        "Your computer has a virus and needs immediate attention",
        "I need you to buy iTunes gift cards to fix this",
        "Go to the store and buy $500 worth of gift cards",
        "Send me the codes from the back of the cards"
    ]
    
    try:
        response = requests.post(
            f"{base_url}/analyze/chat",
            json={
                "content": json.dumps(gift_card_scam_messages),
                "channel": "chat",
                "sender_info": "microsoft_support"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Gift card scam detected: {data['is_fraud']}")
            print(f"   Risk Score: {data['risk_score']:.3f}")
            print(f"   Risk Level: {data['risk_level']}")
            print(f"   Triggers: {', '.join(data['triggers'][:3])}")
            print(f"   Processing Time: {data['processing_time']:.3f}s")
        else:
            print(f"❌ Gift card scam detection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Gift card scam detection error: {str(e)}")
        return False
    
    print("\n🎉 All chat detection tests passed! Your chat fraud detection service is working correctly.")
    return True

if __name__ == "__main__":
    success = test_chat_detection()
    if not success:
        print("\n💥 Some tests failed. Please check the service and try again.")
        exit(1)
