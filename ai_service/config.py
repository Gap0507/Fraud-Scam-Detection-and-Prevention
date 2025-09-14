"""
Configuration file for FraudShield AI Service
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the directory where this config file is located
BASE_DIR = Path(__file__).parent

# Gemini API Configuration - load from environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Validate that API key is provided
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required. Please set it in your .env file or environment.")

# Other configuration
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Model paths
MODELS_DIR = BASE_DIR / "models"
AUDIO_MODEL_PATH = MODELS_DIR / "best_model10.pth"
VOSK_MODEL_PATH = MODELS_DIR / "vosk-model-en-us-0.22"
