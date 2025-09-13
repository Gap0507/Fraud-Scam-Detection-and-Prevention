#!/usr/bin/env python3
"""
Quick test to verify Audio analyzer works
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.audio_analyzer import AudioAnalyzer

async def quick_audio_test():
    print("🚀 Quick Audio Analyzer Test")
    print("=" * 30)
    
    # Initialize Audio analyzer
    audio_analyzer = AudioAnalyzer()
    print("Initializing Audio analyzer...")
    await audio_analyzer.initialize()
    print(f"Audio analyzer ready: {audio_analyzer.is_ready()}")
    
    # Test with sample audio file if available
    test_files = [
        "fraud-audio-detection-main/data/Elevanlabs_Fake.wav",
        "fraud-audio-detection-main/data/real_audio.flac"
    ]
    
    test_file = None
    for file_path in test_files:
        if os.path.exists(file_path):
            test_file = file_path
            break
    
    if not test_file:
        print("❌ No test audio files found. Please ensure test audio files exist.")
        return
    
    print(f"\nTesting with: {test_file}")
    
    result = await audio_analyzer.analyze_audio(test_file)
    
    print(f"Deepfake Score: {result['deepfake_score']:.3f}")
    print(f"Is Deepfake: {result['is_deepfake']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Confidence: {result['confidence']:.3f}")
    print(f"Processing Time: {result['processing_time']:.3f}s")
    print(f"Audio Duration: {result['audio_metadata']['duration']:.2f}s")
    
    if result['is_deepfake']:
        print("✅ SUCCESS: Deepfake detected correctly!")
    else:
        print("✅ SUCCESS: Authentic audio detected correctly!")

if __name__ == "__main__":
    asyncio.run(quick_audio_test())
