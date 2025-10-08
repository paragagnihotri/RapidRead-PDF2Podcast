import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application configuration settings"""
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Server settings
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    
    # Directory settings
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    UPLOAD_DIR: Path = BASE_DIR / os.getenv("UPLOAD_DIR", "uploads")
    OUTPUT_DIR: Path = BASE_DIR / os.getenv("OUTPUT_DIR", "outputs")
    
    # LLM settings
    LLM_MODEL: str = "gemini/gemini-2.0-flash"
    LLM_TEMPERATURE: float = 0.7
    
    # File upload settings
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS: set = {".pdf"}
    
    def __init__(self):
        """Create necessary directories on initialization"""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

settings = Settings()