#!/usr/bin/env python3
"""
Install Gemini dependencies for FraudShield
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Install Gemini dependencies"""
    print("🔧 Installing Gemini 2.5 Pro dependencies for FraudShield")
    print("=" * 60)
    
    # Required packages
    packages = [
        "google-generativeai==0.3.2"
    ]
    
    success_count = 0
    total_packages = len(packages)
    
    for package in packages:
        print(f"📦 Installing {package}...")
        if install_package(package):
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"📊 Installation Summary: {success_count}/{total_packages} packages installed")
    
    if success_count == total_packages:
        print("🎉 All dependencies installed successfully!")
        print()
        print("Next steps:")
        print("1. Get your Gemini API key from: https://aistudio.google.com/")
        print("2. Set the environment variable: export GEMINI_API_KEY=your_key_here")
        print("3. Run the test: python test_gemini_integration.py")
        print("4. Start the server: python main.py")
        print("5. Visit /voice-channels in the frontend")
    else:
        print("⚠️  Some packages failed to install. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
