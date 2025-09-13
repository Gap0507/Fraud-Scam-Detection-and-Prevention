#!/usr/bin/env python3
"""
Generate test audio files for audio deepfake detection testing
"""

import numpy as np
import soundfile as sf
import os

def generate_real_audio():
    """Generate a simple real audio file for testing"""
    
    # Audio parameters
    sample_rate = 16000  # 16kHz sample rate
    duration = 3.0  # 3 seconds
    frequency = 440  # A4 note (440 Hz)
    
    # Generate a simple sine wave (real audio)
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create a more complex waveform (not just pure sine)
    # Mix of fundamental frequency and harmonics
    audio = (np.sin(2 * np.pi * frequency * t) * 0.5 +
             np.sin(2 * np.pi * frequency * 2 * t) * 0.3 +
             np.sin(2 * np.pi * frequency * 3 * t) * 0.2)
    
    # Add some natural variation (slight amplitude modulation)
    envelope = 1 + 0.1 * np.sin(2 * np.pi * 0.5 * t)  # Slow amplitude variation
    audio = audio * envelope
    
    # Normalize audio
    audio = audio / np.max(np.abs(audio)) * 0.8
    
    # Save as WAV file
    output_file = "real_audio_test.wav"
    sf.write(output_file, audio, sample_rate)
    
    print(f"✅ Generated real audio test file: {output_file}")
    print(f"   Duration: {duration}s")
    print(f"   Sample rate: {sample_rate} Hz")
    print(f"   Frequency: {frequency} Hz")
    
    return output_file

def generate_speech_like_audio():
    """Generate speech-like audio for more realistic testing"""
    
    sample_rate = 16000
    duration = 4.0
    
    # Generate multiple frequency components to simulate speech
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Simulate formants (speech characteristics)
    audio = (np.sin(2 * np.pi * 200 * t) * 0.4 +  # F0 (fundamental)
             np.sin(2 * np.pi * 800 * t) * 0.3 +  # F1 (first formant)
             np.sin(2 * np.pi * 1200 * t) * 0.2 + # F2 (second formant)
             np.sin(2 * np.pi * 2500 * t) * 0.1)  # F3 (third formant)
    
    # Add some noise to make it more realistic
    noise = np.random.normal(0, 0.05, len(audio))
    audio = audio + noise
    
    # Add amplitude modulation to simulate speech rhythm
    modulation = 1 + 0.3 * np.sin(2 * np.pi * 2 * t)  # 2 Hz modulation
    audio = audio * modulation
    
    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.7
    
    # Save as FLAC file
    output_file = "speech_like_audio.flac"
    sf.write(output_file, audio, sample_rate)
    
    print(f"✅ Generated speech-like audio test file: {output_file}")
    print(f"   Duration: {duration}s")
    print(f"   Sample rate: {sample_rate} Hz")
    print(f"   Contains formants and natural variation")
    
    return output_file

def generate_music_audio():
    """Generate simple music audio for testing"""
    
    sample_rate = 16000
    duration = 5.0
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create a simple melody (C major scale)
    notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]  # C4 to C5
    note_duration = duration / len(notes)
    
    audio = np.zeros_like(t)
    
    for i, freq in enumerate(notes):
        start_idx = int(i * note_duration * sample_rate)
        end_idx = int((i + 1) * note_duration * sample_rate)
        
        if end_idx > len(t):
            end_idx = len(t)
            
        note_t = t[start_idx:end_idx]
        note_audio = np.sin(2 * np.pi * freq * note_t)
        
        # Add envelope to avoid clicks
        envelope = np.exp(-note_t * 2)  # Decay envelope
        note_audio = note_audio * envelope
        
        audio[start_idx:end_idx] = note_audio
    
    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.6
    
    # Save as WAV file
    output_file = "music_audio.wav"
    sf.write(output_file, audio, sample_rate)
    
    print(f"✅ Generated music audio test file: {output_file}")
    print(f"   Duration: {duration}s")
    print(f"   Sample rate: {sample_rate} Hz")
    print(f"   Contains C major scale melody")
    
    return output_file

if __name__ == "__main__":
    print("🎵 Generating Test Audio Files")
    print("=" * 40)
    
    # Generate different types of real audio
    files = []
    
    try:
        files.append(generate_real_audio())
        files.append(generate_speech_like_audio())
        files.append(generate_music_audio())
        
        print(f"\n🎉 Successfully generated {len(files)} test audio files:")
        for file in files:
            print(f"   - {file}")
        
        print(f"\n📁 Files saved in: {os.getcwd()}")
        print("\n💡 These files should be detected as REAL audio by the deepfake detector.")
        
    except Exception as e:
        print(f"❌ Error generating audio files: {e}")
        print("Make sure you have soundfile installed: pip install soundfile")
