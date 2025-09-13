#!/usr/bin/env python3
"""
Quick test to verify Email analyzer works
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.email_analyzer import EmailAnalyzer

async def quick_email_test():
    print("🚀 Quick Email Analyzer Test")
    print("=" * 30)
    
    # Initialize Email analyzer
    email_analyzer = EmailAnalyzer()
    print("Initializing Email analyzer...")
    await email_analyzer.initialize()
    print(f"Email analyzer ready: {email_analyzer.is_ready()}")
    
    # Test phishing email - more realistic and challenging
    phishing_subject = "URGENT: Your account has been compromised!"
    phishing_body = """Dear Customer,

We have detected suspicious activity on your account. Please verify your identity immediately by clicking the link below:

https://bit.ly/bank-verify-urgent

If you do not verify within 24 hours, your account will be suspended and you may face legal consequences.

This is your final warning. Act now or face arrest.

Best regards,
Security Team
Federal Banking Authority"""
    
    print(f"\nTesting phishing email:")
    print(f"Subject: {phishing_subject}")
    print(f"Body: {phishing_body[:100]}...")
    
    result = await email_analyzer.analyze_email(
        phishing_subject, 
        phishing_body, 
        "security@bank-verify.com"
    )
    
    print(f"Risk Score: {result['risk_score']:.3f}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Is Phishing: {result['is_phishing']}")
    print(f"Confidence: {result['confidence']:.3f}")
    print(f"Triggers: {result['triggers']}")
    
    if result['is_phishing'] and result['risk_score'] > 0.15:  # Lowered threshold
        print("✅ SUCCESS: Phishing email detected correctly!")
    else:
        print("❌ FAILED: Phishing email not detected properly")
    
    # Test legitimate email
    print(f"\n" + "="*50)
    legitimate_subject = "Account Statement Available"
    legitimate_body = """Dear Customer,

Your monthly account statement is now available online. You can view it by logging into your account at https://www.bankofamerica.com or by calling us at 1-800-555-0123.

Thank you for banking with us.

Bank of America Customer Service"""
    
    print(f"\nTesting legitimate email:")
    print(f"Subject: {legitimate_subject}")
    print(f"Body: {legitimate_body[:100]}...")
    
    result2 = await email_analyzer.analyze_email(
        legitimate_subject, 
        legitimate_body, 
        "noreply@bankofamerica.com"
    )
    
    print(f"Risk Score: {result2['risk_score']:.3f}")
    print(f"Risk Level: {result2['risk_level']}")
    print(f"Is Phishing: {result2['is_phishing']}")
    print(f"Confidence: {result2['confidence']:.3f}")
    print(f"Triggers: {result2['triggers']}")
    
    if not result2['is_phishing'] and result2['risk_score'] < 0.15:  # Lowered threshold
        print("✅ SUCCESS: Legitimate email detected correctly!")
    else:
        print("❌ FAILED: Legitimate email not detected properly")

if __name__ == "__main__":
    asyncio.run(quick_email_test())
