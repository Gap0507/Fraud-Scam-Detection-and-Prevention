#!/usr/bin/env python3
"""
Debug script to understand confidence values and fix the 100% issue
"""

import asyncio
import sys
import os
import torch
import torchaudio
import torchaudio.transforms as T
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.audio_analyzer import AudioAnalyzer

async def debug_audio_confidence():
    print("🐛 Debugging Audio Confidence Values")
    print("=" * 50)
    
    # Initialize Audio analyzer
    audio_analyzer = AudioAnalyzer()
    print("Initializing Audio analyzer...")
    await audio_analyzer.initialize()
    print(f"Audio analyzer ready: {audio_analyzer.is_ready()}")
    
    # Test with sample audio files
    test_files = [
        "Elevanlabs_Fake.wav",
        "real_audio.flac"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\n📁 Debugging: {os.path.basename(file_path)}")
            print("-" * 30)
            
            # Load and preprocess audio manually to see raw values
            waveform, sample_rate = torchaudio.load(file_path, backend="soundfile")
            processed_segments = audio_analyzer._preprocess_audio(waveform, sample_rate)
            
            print(f"   Audio shape: {waveform.shape}")
            print(f"   Sample rate: {sample_rate}")
            print(f"   Number of segments: {len(processed_segments)}")
            
            # Run inference on each segment (exactly like original)
            predicted_classes = []
            predicted = []
            
            for i, segment in enumerate(processed_segments):
                with torch.no_grad():
                    # Add batch dimension and normalize (exactly like original)
                    segment = segment.unsqueeze(0).to(audio_analyzer.device)
                    segment = (segment - audio_analyzer.imagenet_mean) / audio_analyzer.imagenet_std
                    
                    # Get prediction (exactly like original)
                    outputs = audio_analyzer.model(segment)
                    predicted_classes.append(torch.sigmoid(outputs))
                    predicted.append((torch.sigmoid(outputs) > 0.5).int())
                    
                    confidence = torch.sigmoid(outputs).item()
                    prediction = 1 if confidence > 0.5 else 0
                    print(f"   Segment {i+1}: confidence={confidence:.4f}, prediction={prediction}")
            
            # Calculate overall results (exactly like original)
            avg_confidence = torch.mean(torch.cat(predicted_classes)).item()
            is_deepfake = avg_confidence < 0.4
            deepfake_score = 1.0 - avg_confidence
            
            print(f"\n   📊 Overall Results:")
            print(f"   Average confidence: {avg_confidence:.4f}")
            print(f"   Is deepfake: {is_deepfake}")
            print(f"   Deepfake score: {deepfake_score:.4f}")
            print(f"   Threshold (0.4): {'< 0.4 = FAKE' if is_deepfake else '>= 0.4 = REAL'}")
            
            # Now test the full analysis
            result = await audio_analyzer.analyze_audio(file_path)
            print(f"\n   🎯 Full Analysis Result:")
            print(f"   Deepfake Score: {result['deepfake_score']:.4f}")
            print(f"   Is Deepfake: {result['is_deepfake']}")
            print(f"   Risk Level: {result['risk_level']}")
            print(f"   Confidence: {result['confidence']:.4f}")
            print(f"   Triggers: {result['triggers']}")
            
        else:
            print(f"❌ File not found: {file_path}")
    
    print("\n🎉 Debug completed!")

if __name__ == "__main__":
    asyncio.run(debug_audio_confidence())
