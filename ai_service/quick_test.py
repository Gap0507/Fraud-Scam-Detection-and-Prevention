#!/usr/bin/env python3
"""
Quick test to verify SMS analyzer works
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.sms_analyzer import SMSAnalyzer

async def quick_test():
    print("🚀 Quick SMS Analyzer Test")
    print("=" * 30)
    
    # Initialize SMS analyzer
    sms_analyzer = SMSAnalyzer()
    print("Initializing SMS analyzer...")
    await sms_analyzer.initialize()
    print(f"SMS analyzer ready: {sms_analyzer.is_ready()}")
    
    # Test scam message
    scam_msg = "URGENT: You have an outstanding warrant. Call 555-0123 immediately or face arrest!"
    print(f"\nTesting: {scam_msg}")
    
    result = await sms_analyzer.analyze_sms(scam_msg, "555-0123")
    
    print(f"Risk Score: {result['risk_score']:.3f}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Is Scam: {result['is_scam']}")
    print(f"Confidence: {result['confidence']:.3f}")
    print(f"Triggers: {result['triggers']}")
    
    if result['is_scam'] and result['risk_score'] > 0.7:
        print("✅ SUCCESS: Scam detected correctly!")
    else:
        print("❌ FAILED: Scam not detected properly")

if __name__ == "__main__":
    asyncio.run(quick_test())
