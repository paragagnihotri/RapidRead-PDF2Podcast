from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import shutil
import uuid
from backend.config import settings
from backend.models import ProcessingStatus, ScriptResponse, ErrorResponse
from backend.services.crew_service import CrewService
from backend.services.pdf_service import PDFService

router = APIRouter()
crew_service = CrewService()
pdf_service = PDFService()

@router.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "PDF to Podcast API is running"}

@router.post("/upload", response_model=ProcessingStatus)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file for processing
    
    Args:
        file: PDF file to upload
        
    Returns:
        ProcessingStatus with file_id
    """
    try:
        # Validate file extension
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        file_path = settings.UPLOAD_DIR / f"{file_id}.pdf"
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Validate PDF
        if not pdf_service.validate_pdf(file_path):
            file_path.unlink()
            raise HTTPException(
                status_code=400,
                detail="Invalid or corrupted PDF file"
            )
        
        return ProcessingStatus(
            status="success",
            message="File uploaded successfully",
            file_id=file_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process/{file_id}", response_model=ScriptResponse)
async def process_pdf(file_id: str):
    """
    Process an uploaded PDF and generate podcast script
    
    Args:
        file_id: Unique identifier of the uploaded file
        
    Returns:
        ScriptResponse with generated script
    """
    try:
        # Check if file exists
        file_path = settings.UPLOAD_DIR / f"{file_id}.pdf"
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="File not found. Please upload the file first."
            )
        
        # Process PDF to script
        script_content, output_path = crew_service.process_pdf_to_script(file_path)
        
        # Clean up uploaded file
        file_path.unlink()
        
        return ScriptResponse(
            status="success",
            script=script_content,
            filename=output_path.name,
            message="Script generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if exists
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@router.get("/download/{filename}")
async def download_script(filename: str):
    """
    Download a generated script file
    
    Args:
        filename: Name of the script file
        
    Returns:
        FileResponse with the script file
    """
    try:
        file_path = settings.OUTPUT_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Script file not found"
            )
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='text/plain'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scripts")
async def list_scripts():
    """
    List all generated script files
    
    Returns:
        List of script filenames
    """
    try:
        scripts = [f.name for f in settings.OUTPUT_DIR.glob("*.txt")]
        return {
            "status": "success",
            "scripts": sorted(scripts, reverse=True)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))