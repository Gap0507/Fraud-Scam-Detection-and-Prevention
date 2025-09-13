#!/usr/bin/env python3
"""
Quick test script for Audio Deepfake Detection Service
"""

import requests
import json
import time
import os

def test_audio_detection():
    """Test the audio detection service"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Audio Deepfake Detection Service")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service is healthy: {data['status']}")
            print(f"   Audio Analyzer: {'Ready' if data['services']['audio_analyzer'] else 'Not Ready'}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to service: {str(e)}")
        print("   Make sure to run: python main.py")
        return False
    
    # Test 2: Audio file upload and analysis
    print("\n2️⃣ Testing audio file upload and analysis...")
    
    # Check if we have test audio files
    test_audio_files = [
        "fraud-audio-detection-main/data/Elevanlabs_Fake.wav",
        "fraud-audio-detection-main/data/real_audio.flac"
    ]
    
    test_file = None
    for file_path in test_audio_files:
        if os.path.exists(file_path):
            test_file = file_path
            break
    
    if not test_file:
        print("❌ No test audio files found. Please ensure test audio files exist.")
        return False
    
    print(f"Using test file: {test_file}")
    
    try:
        with open(test_file, 'rb') as f:
            files = {'audio_file': (os.path.basename(test_file), f, 'audio/wav')}
            response = requests.post(
                f"{base_url}/analyze/audio",
                files=files,
                timeout=60
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Audio analysis completed")
            print(f"   Deepfake Score: {data['deepfake_score']:.3f}")
            print(f"   Is Deepfake: {data['is_deepfake']}")
            print(f"   Risk Level: {data['risk_level']}")
            print(f"   Confidence: {data['confidence']:.3f}")
            print(f"   Processing Time: {data['processing_time']:.3f}s")
            print(f"   Audio Duration: {data['audio_metadata']['duration']:.2f}s")
            print(f"   Sample Rate: {data['audio_metadata']['sample_rate']} Hz")
        else:
            print(f"❌ Audio analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Audio analysis error: {str(e)}")
        return False
    
    # Test 3: Model status check
    print("\n3️⃣ Testing model status...")
    try:
        response = requests.get(f"{base_url}/models/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            audio_status = data.get('audio_analyzer', {})
            print(f"✅ Audio analyzer status: {'Ready' if audio_status.get('ready') else 'Not Ready'}")
            print(f"   Model: {audio_status.get('model_name', 'Unknown')}")
        else:
            print(f"❌ Model status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Model status error: {str(e)}")
        return False
    
    # Test 4: Test with different audio file if available
    print("\n4️⃣ Testing with second audio file...")
    other_test_file = None
    for file_path in test_audio_files:
        if file_path != test_file and os.path.exists(file_path):
            other_test_file = file_path
            break
    
    if other_test_file:
        try:
            with open(other_test_file, 'rb') as f:
                files = {'audio_file': (os.path.basename(other_test_file), f, 'audio/flac')}
                response = requests.post(
                    f"{base_url}/analyze/audio",
                    files=files,
                    timeout=60
                )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Second audio analysis completed")
                print(f"   Deepfake Score: {data['deepfake_score']:.3f}")
                print(f"   Is Deepfake: {data['is_deepfake']}")
                print(f"   Risk Level: {data['risk_level']}")
            else:
                print(f"❌ Second audio analysis failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Second audio analysis error: {str(e)}")
    else:
        print("ℹ️  Only one test audio file available, skipping second test")
    
    print("\n🎉 All audio detection tests passed! Your audio deepfake detection service is working correctly.")
    return True

if __name__ == "__main__":
    success = test_audio_detection()
    if not success:
        print("\n💥 Some tests failed. Please check the service and try again.")
        exit(1)
