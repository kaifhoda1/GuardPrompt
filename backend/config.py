# GuardPrompt Configuration
# All settings in one place — change here, affects everything

APP_NAME = "GuardPrompt"
APP_VERSION = "0.1.0"
DEBUG = True

# Detection settings
SEMANTIC_ENABLED = True        # Set False to skip Mistral (faster, less accurate)
BLOCK_THRESHOLD = 80           # Score >= this → block
FLAG_THRESHOLD = 40            # Score >= this → flag

# Server settings
HOST = "0.0.0.0"
PORT = 8000
