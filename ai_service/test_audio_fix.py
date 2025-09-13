#!/usr/bin/env python3
"""
Test script to verify the audio detection fix
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.audio_analyzer import AudioAnalyzer

async def test_audio_fix():
    print("🔧 Testing Audio Detection Fix")
    print("=" * 40)
    
    # Initialize Audio analyzer
    audio_analyzer = AudioAnalyzer()
    print("Initializing Audio analyzer...")
    await audio_analyzer.initialize()
    print(f"Audio analyzer ready: {audio_analyzer.is_ready()}")
    
    # Test with sample audio files
    test_files = [
        ("Elevanlabs_Fake.wav", "Expected: FAKE"),
        ("real_audio.flac", "Expected: REAL")
    ]
    
    for file_path, expected in test_files:
        if os.path.exists(file_path):
            print(f"\n📁 Testing: {os.path.basename(file_path)}")
            print(f"   {expected}")
            
            result = await audio_analyzer.analyze_audio(file_path)
            
            print(f"   Deepfake Score: {result['deepfake_score']:.3f}")
            print(f"   Is Deepfake: {result['is_deepfake']}")
            print(f"   Risk Level: {result['risk_level']}")
            print(f"   Confidence: {result['confidence']:.3f}")
            print(f"   Processing Time: {result['processing_time']:.3f}s")
            print(f"   Audio Duration: {result['audio_metadata']['duration']:.2f}s")
            print(f"   Triggers: {result['triggers']}")
            
            # Check if the result makes sense
            if "Fake" in expected and result['is_deepfake']:
                print("   ✅ CORRECT: Fake audio detected as fake")
            elif "Real" in expected and not result['is_deepfake']:
                print("   ✅ CORRECT: Real audio detected as real")
            else:
                print("   ⚠️  UNEXPECTED: Result doesn't match expectation")
        else:
            print(f"❌ File not found: {file_path}")
    
    print("\n🎉 Audio detection fix test completed!")

if __name__ == "__main__":
    asyncio.run(test_audio_fix())
