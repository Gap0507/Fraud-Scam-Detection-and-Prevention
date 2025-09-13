"""
Test runner for SMS Analyzer
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.sms_analyzer import SMSAnalyzer
from services.data_simulator import DataSimulator
from services.model_evaluator import ModelEvaluator
import json
from datetime import datetime

async def run_sms_tests():
    """Run comprehensive SMS analyzer tests"""
    print("🚀 Starting SMS Analyzer Tests...")
    print("=" * 50)
    
    # Initialize services
    print("📋 Initializing services...")
    sms_analyzer = SMSAnalyzer()
    await sms_analyzer.initialize()
    
    data_simulator = DataSimulator()
    evaluator = ModelEvaluator()
    await evaluator.initialize()
    
    print("✅ Services initialized successfully!")
    print()
    
    # Test 1: Basic functionality
    print("🧪 Test 1: Basic SMS Analysis")
    print("-" * 30)
    
    test_messages = [
        ("URGENT: You have an outstanding warrant. Call 555-0123 immediately or face arrest!", True),
        ("Your account balance is $1500. Thank you for banking with us.", False),
        ("CONGRATULATIONS! You've won $5000! Call 555-0456 to claim your prize.", True),
        ("Reminder: You have an appointment with Dr. Smith on 2024-12-01 at 9:00 AM.", False),
        ("Your OTP is 123456. Do not share with anyone. Valid for 5 minutes.", True)
    ]
    
    for i, (message, expected_scam) in enumerate(test_messages, 1):
        print(f"\nTest {i}: {'SCAM' if expected_scam else 'LEGITIMATE'}")
        print(f"Message: {message}")
        
        result = await sms_analyzer.analyze_sms(message, "555-0123")
        
        print(f"Predicted: {'SCAM' if result['is_scam'] else 'LEGITIMATE'}")
        print(f"Risk Score: {result['risk_score']:.3f}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Triggers: {', '.join(result['triggers'][:3])}")
        print(f"Correct: {'✅' if result['is_scam'] == expected_scam else '❌'}")
    
    print("\n" + "=" * 50)
    
    # Test 2: Generate and test dataset
    print("🧪 Test 2: Dataset Generation and Testing")
    print("-" * 40)
    
    print("Generating test dataset...")
    test_data = await data_simulator.generate_sms_data(count=100, scam_ratio=0.5)
    
    print(f"Generated {len(test_data)} test messages")
    scam_count = sum(1 for item in test_data if item["is_scam"])
    print(f"Scam messages: {scam_count}")
    print(f"Legitimate messages: {len(test_data) - scam_count}")
    
    # Test 3: Model evaluation
    print("\n🧪 Test 3: Model Evaluation")
    print("-" * 30)
    
    print("Running model evaluation...")
    evaluation = await evaluator.evaluate_model(test_data, "SMS Analyzer")
    
    print(f"Accuracy: {evaluation.metrics.accuracy:.4f}")
    print(f"Precision: {evaluation.metrics.precision:.4f}")
    print(f"Recall: {evaluation.metrics.recall:.4f}")
    print(f"F1 Score: {evaluation.metrics.f1_score:.4f}")
    print(f"False Positive Rate: {evaluation.metrics.false_positive_rate:.4f}")
    print(f"False Negative Rate: {evaluation.metrics.false_negative_rate:.4f}")
    
    # Test 4: Performance test
    print("\n🧪 Test 4: Performance Test")
    print("-" * 30)
    
    print("Testing performance with 50 messages...")
    start_time = datetime.now()
    
    for item in test_data[:50]:
        await sms_analyzer.analyze_sms(item["message"], item["sender"])
    
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    avg_time = total_time / 50
    
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time per message: {avg_time:.3f} seconds")
    print(f"Messages per second: {50/total_time:.2f}")
    
    # Test 5: Save results
    print("\n🧪 Test 5: Saving Results")
    print("-" * 30)
    
    # Save evaluation results
    results_filename = f"sms_evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    await evaluator.save_evaluation_results(evaluation, results_filename)
    print(f"Evaluation results saved to: {results_filename}")
    
    # Generate and save report
    report = await evaluator.generate_evaluation_report(evaluation)
    report_filename = f"sms_evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Evaluation report saved to: {report_filename}")
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(run_sms_tests())
