"""
Test runner for Email Analyzer
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.email_analyzer import EmailAnalyzer
from services.email_data_simulator import EmailDataSimulator
from services.email_model_evaluator import EmailModelEvaluator
import json
from datetime import datetime

async def run_email_tests():
    """Run comprehensive email analyzer tests"""
    print("🚀 Starting Email Analyzer Tests...")
    print("=" * 50)
    
    # Initialize services
    print("📋 Initializing services...")
    email_analyzer = EmailAnalyzer()
    await email_analyzer.initialize()
    
    email_data_simulator = EmailDataSimulator()
    evaluator = EmailModelEvaluator()
    await evaluator.initialize()
    
    print("✅ Services initialized successfully!")
    print()
    
    # Test 1: Basic functionality
    print("🧪 Test 1: Basic Email Analysis")
    print("-" * 30)
    
    test_emails = [
        {
            "subject": "URGENT: Your account has been compromised!",
            "body": "Dear Customer,\n\nWe have detected suspicious activity on your account. Please verify your identity immediately by clicking the link below:\n\nhttps://bank-verify.com/secure\n\nIf you do not verify within 24 hours, your account will be suspended.\n\nBest regards,\nSecurity Team",
            "sender": "security@bank-verify.com",
            "expected_phishing": True
        },
        {
            "subject": "Account Statement Available",
            "body": "Dear Customer,\n\nYour monthly account statement is now available online. You can view it by logging into your account at https://www.bankofamerica.com or by calling us at 1-800-555-0123.\n\nThank you for banking with us.\n\nBank of America Customer Service",
            "sender": "noreply@bankofamerica.com",
            "expected_phishing": False
        },
        {
            "subject": "Microsoft Security Alert - Account Compromised",
            "body": "Microsoft Security Center\n\nWe detected unusual sign-in activity on your Microsoft account. Someone may have accessed your account from an unrecognized device.\n\nLocation: New York, NY\nTime: 2:30 PM\n\nIf this wasn't you, secure your account immediately:\nhttps://microsoft-security.net/login\n\nMicrosoft Security Team",
            "sender": "security@microsoft-security.net",
            "expected_phishing": True
        },
        {
            "subject": "Appointment Reminder - Tomorrow at 2:00 PM",
            "body": "Hello,\n\nThis is a reminder that you have an appointment scheduled for tomorrow at 2:00 PM with Dr. Smith.\n\nPlease arrive 15 minutes early. If you need to reschedule, please call 1-800-555-0456.\n\nThank you,\nCity Medical Center",
            "sender": "appointments@citymedical.com",
            "expected_phishing": False
        },
        {
            "subject": "Congratulations! You've Won $50,000!",
            "body": "Congratulations!\n\nYou have been selected as the winner of our annual lottery! You have won $50,000!\n\nTo claim your prize, please provide your personal information:\nhttps://lottery-claim.tk/winner\n\nThis offer expires in 48 hours. Don't miss out!\n\nLottery Department",
            "sender": "lottery@prize-winner.tk",
            "expected_phishing": True
        }
    ]
    
    for i, email in enumerate(test_emails, 1):
        print(f"\nTest {i}: {'PHISHING' if email['expected_phishing'] else 'LEGITIMATE'}")
        print(f"Subject: {email['subject']}")
        print(f"Sender: {email['sender']}")
        
        result = await email_analyzer.analyze_email(
            email["subject"], 
            email["body"], 
            email["sender"]
        )
        
        print(f"Predicted: {'PHISHING' if result['is_phishing'] else 'LEGITIMATE'}")
        print(f"Risk Score: {result['risk_score']:.3f}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Triggers: {', '.join(result['triggers'][:3])}")
        print(f"Correct: {'✅' if result['is_phishing'] == email['expected_phishing'] else '❌'}")
    
    print("\n" + "=" * 50)
    
    # Test 2: Generate and test dataset
    print("🧪 Test 2: Dataset Generation and Testing")
    print("-" * 40)
    
    print("Generating test dataset...")
    test_data = await email_data_simulator.generate_email_data(count=100, phishing_ratio=0.5)
    
    print(f"Generated {len(test_data)} test emails")
    phishing_count = sum(1 for item in test_data if item["is_phishing"])
    print(f"Phishing emails: {phishing_count}")
    print(f"Legitimate emails: {len(test_data) - phishing_count}")
    
    # Test 3: Model evaluation
    print("\n🧪 Test 3: Model Evaluation")
    print("-" * 30)
    
    print("Running model evaluation...")
    evaluation = await evaluator.evaluate_model(test_data, "Email Analyzer")
    
    print(f"Accuracy: {evaluation.metrics.accuracy:.4f}")
    print(f"Precision: {evaluation.metrics.precision:.4f}")
    print(f"Recall: {evaluation.metrics.recall:.4f}")
    print(f"F1 Score: {evaluation.metrics.f1_score:.4f}")
    print(f"False Positive Rate: {evaluation.metrics.false_positive_rate:.4f}")
    print(f"False Negative Rate: {evaluation.metrics.false_negative_rate:.4f}")
    
    # Test 4: Performance test
    print("\n🧪 Test 4: Performance Test")
    print("-" * 30)
    
    print("Testing performance with 20 emails...")
    start_time = datetime.now()
    
    for item in test_data[:20]:
        await email_analyzer.analyze_email(item["subject"], item["body"], item["sender"])
    
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    avg_time = total_time / 20
    
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time per email: {avg_time:.3f} seconds")
    print(f"Emails per second: {20/total_time:.2f}")
    
    # Test 5: Phishing type evaluation
    print("\n🧪 Test 5: Phishing Type Evaluation")
    print("-" * 40)
    
    print("Evaluating performance by phishing type...")
    type_results = await evaluator.evaluate_phishing_types(test_data)
    
    for phishing_type, results in type_results.items():
        print(f"\n{phishing_type}:")
        print(f"  Accuracy: {results['accuracy']:.4f}")
        print(f"  Precision: {results['precision']:.4f}")
        print(f"  Recall: {results['recall']:.4f}")
        print(f"  F1 Score: {results['f1_score']:.4f}")
        print(f"  Sample Count: {results['sample_count']}")
    
    # Test 6: Save results
    print("\n🧪 Test 6: Saving Results")
    print("-" * 30)
    
    # Save evaluation results
    results_filename = f"email_evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    await evaluator.save_evaluation_results(evaluation, results_filename)
    print(f"Evaluation results saved to: {results_filename}")
    
    # Generate and save report
    report = await evaluator.generate_evaluation_report(evaluation)
    report_filename = f"email_evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Evaluation report saved to: {report_filename}")
    
    print("\n" + "=" * 50)
    print("🎉 All email tests completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(run_email_tests())
