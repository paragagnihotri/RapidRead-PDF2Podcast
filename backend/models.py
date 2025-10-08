from pydantic import BaseModel
from typing import Optional

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

class ErrorResponse(BaseModel):
    """Response model for errors"""
    status: str
    error: str
    detail: Optional[str] = None