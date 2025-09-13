#!/usr/bin/env python3
"""
Test script for Gemini 2.5 Pro integration
Run this to verify the Gemini analyzer is working correctly
"""

import asyncio
import os
import sys
import tempfile
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from services.gemini_analyzer import GeminiAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_gemini_analyzer():
    """Test the Gemini analyzer with a sample audio file"""
    
    print("🧪 Testing Gemini 2.5 Pro Integration")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'demo_key':
        print("⚠️  WARNING: GEMINI_API_KEY not set or using demo key")
        print("   Set your API key: export GEMINI_API_KEY=your_key_here")
        print("   Get your key from: https://aistudio.google.com/")
        print()
    
    # Initialize analyzer
    analyzer = GeminiAnalyzer()
    
    try:
        print("🔄 Initializing Gemini analyzer...")
        await analyzer.initialize()
        
        if not analyzer.is_ready():
            print("❌ Gemini analyzer failed to initialize")
            return False
            
        print("✅ Gemini analyzer initialized successfully")
        print(f"   Model: {analyzer.get_model_info()}")
        print()
        
        # Test with a sample audio file (if available)
        sample_files = [
            "real_audio_test.wav",
            "speech_like_audio.flac", 
            "music_audio.wav",
            "Elevanlabs_Fake.wav"
        ]
        
        test_file = None
        for file_name in sample_files:
            if os.path.exists(file_name):
                test_file = file_name
                break
        
        if not test_file:
            print("⚠️  No sample audio files found for testing")
            print("   Available sample files:", sample_files)
            print("   Creating a dummy test...")
            
            # Create a dummy test file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                # Write minimal WAV header
                tmp.write(b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00')
                tmp.write(b'\x00' * 2048)  # Some silence
                test_file = tmp.name
        
        print(f"🎵 Testing with file: {test_file}")
        print("🔄 Running analysis...")
        
        # Run analysis
        result = await analyzer.analyze_audio(test_file)
        
        print("✅ Analysis completed!")
        print()
        print("📊 Results:")
        print(f"   Analysis ID: {result['analysis_id']}")
        print(f"   Is Deepfake: {result['is_deepfake']}")
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Risk Level: {result['risk_level']}")
        print(f"   Processing Time: {result['processing_time']:.2f}s")
        print(f"   Explanation: {result['explanation']}")
        
        if result.get('triggers'):
            print(f"   Triggers: {', '.join(result['triggers'])}")
        
        print()
        print("🎉 Gemini integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        logger.exception("Test failed")
        return False
    
    finally:
        # Clean up dummy file if created
        if test_file and test_file.startswith('/tmp'):
            try:
                os.unlink(test_file)
            except:
                pass

async def main():
    """Main test function"""
    success = await test_gemini_analyzer()
    
    if success:
        print("\n🚀 Ready to use Gemini 2.5 Pro in FraudShield!")
        print("   - Backend: New endpoints available at /analyze/audio/gemini, /analyze/video/gemini, /analyze/compare")
        print("   - Frontend: Visit /voice-channels for the new interface")
        sys.exit(0)
    else:
        print("\n💥 Gemini integration test failed!")
        print("   Check the error messages above and ensure GEMINI_API_KEY is set correctly")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
