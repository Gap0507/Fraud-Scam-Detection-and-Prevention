#!/usr/bin/env python3
"""
Install dependencies for SMS Fraud Detection Service
"""

import subprocess
import sys
import os

def install_requirements():
    """Install requirements from requirements.txt"""
    try:
        print("🔧 Installing dependencies for SMS Fraud Detection Service...")
        print("=" * 60)
        
        # Check if requirements.txt exists
        if not os.path.exists("requirements.txt"):
            print("❌ requirements.txt not found!")
            return False
        
        # Install requirements
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully!")
            print("\n📦 Installed packages:")
            print("- FastAPI (Web framework)")
            print("- Uvicorn (ASGI server)")
            print("- Transformers (AI models)")
            print("- PyTorch (Deep learning)")
            print("- scikit-learn (ML utilities)")
            print("- Pydantic (Data validation)")
            print("- NumPy (Numerical computing)")
            print("\n🚀 You can now run: python main.py")
            return True
        else:
            print("❌ Installation failed!")
            print("Error:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error during installation: {str(e)}")
        return False

if __name__ == "__main__":
    success = install_requirements()
    if success:
        print("\n🎉 Setup complete! Your SMS fraud detection service is ready to run.")
    else:
        print("\n💥 Setup failed. Please check the error messages above.")
        sys.exit(1)
