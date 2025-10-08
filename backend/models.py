from pydantic import BaseModel
from typing import Optional, List

class ProcessingStatus(BaseModel):
    """Response model for processing status"""
    status: str
    message: str
    file_id: Optional[str] = None

class ScriptResponse(BaseModel):
    """Response model for generated script"""
    status: str
    script: str
    filename: str
    message: Optional[str] = None

class AudioGenerationResponse(BaseModel):
    """Response model for audio generation"""
    status: str
    message: str
    audio_files: List[str]
    playlist_file: Optional[str] = None
    total_segments: int

class PodcastResponse(BaseModel):
    """Response model for complete podcast generation"""
    status: str
    script_filename: str
    audio_files: List[str]
    playlist_file: str
    total_segments: int
    message: str

class ErrorResponse(BaseModel):
    """Response model for errors"""
    status: str
    error: str
    detail: Optional[str] = None