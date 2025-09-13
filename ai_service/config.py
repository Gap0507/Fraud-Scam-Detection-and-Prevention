"""
Configuration file for FraudShield AI Service
"""

import os
from pathlib import Path

# Get the directory where this config file is located
BASE_DIR = Path(__file__).parent

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyCLCCsTVvpdQ7Ud5zFE5u6UlEFug_kXHCQ"

# You can also load from environment variable if set
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', GEMINI_API_KEY)

# Other configuration
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Model paths
MODELS_DIR = BASE_DIR / "models"
AUDIO_MODEL_PATH = MODELS_DIR / "best_model10.pth"
VOSK_MODEL_PATH = MODELS_DIR / "vosk-model-en-us-0.22"
