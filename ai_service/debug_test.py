#!/usr/bin/env python3
"""
Debug test to check SMS analyzer directly
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.sms_analyzer import SMSAnalyzer

async def test_sms_analyzer():
    """Test SMS analyzer directly"""
    print("🔍 Testing SMS Analyzer Directly")
    print("=" * 40)
    
    # Initialize SMS analyzer
    sms_analyzer = SMSAnalyzer()
    await sms_analyzer.initialize()
    
    # Test scam message
    scam_message = "URGENT: You have an outstanding warrant. Call 555-0123 immediately or face arrest!"
    print(f"\n📱 Testing scam message:")
    print(f"Message: {scam_message}")
    
    result = await sms_analyzer.analyze_sms(scam_message, "555-0123")
    
    print(f"\n📊 Results:")
    print(f"Risk Score: {result['risk_score']:.3f}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Is Scam: {result['is_scam']}")
    print(f"Confidence: {result['confidence']:.3f}")
    print(f"Triggers: {result['triggers']}")
    print(f"Explanation: {result['explanation']}")
    
    # Test legitimate message
    legit_message = "Your account balance is $1500. Thank you for banking with us."
    print(f"\n📱 Testing legitimate message:")
    print(f"Message: {legit_message}")
    
    result2 = await sms_analyzer.analyze_sms(legit_message, "555-0789")
    
    print(f"\n📊 Results:")
    print(f"Risk Score: {result2['risk_score']:.3f}")
    print(f"Risk Level: {result2['risk_level']}")
    print(f"Is Scam: {result2['is_scam']}")
    print(f"Confidence: {result2['confidence']:.3f}")
    print(f"Triggers: {result2['triggers']}")

if __name__ == "__main__":
    asyncio.run(test_sms_analyzer())
