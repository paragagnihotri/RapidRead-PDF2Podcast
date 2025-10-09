from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import shutil
import uuid
from backend.config import settings
from backend.models import ProcessingStatus, ScriptResponse, ErrorResponse, AudioGenerationResponse, PodcastResponse
from backend.services.crew_service import CrewService
from backend.services.pdf_service import PDFService
from backend.services.tts_service import TTSService

router = APIRouter()
crew_service = CrewService()
pdf_service = PDFService()
tts_service = TTSService()

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

@router.post("/generate-audio/{script_filename}", response_model=AudioGenerationResponse)
async def generate_audio(script_filename: str):
    """
    Generate single combined audio podcast from script file
    
    Args:
        script_filename: Name of the script file
        
    Returns:
        AudioGenerationResponse with combined audio file path
    """
    try:
        # Check if script exists
        script_path = settings.OUTPUT_DIR / script_filename
        
        if not script_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Script file not found"
            )
        
        # Generate combined audio
        audio_file, total_segments = await tts_service.generate_complete_podcast(
            script_path
        )
        
        # Get audio duration
        duration = tts_service.get_audio_duration(Path(audio_file))
        
        return AudioGenerationResponse(
            status="success",
            message="Audio generated successfully",
            audio_file=audio_file,
            duration=duration,
            total_segments=total_segments
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio generation error: {str(e)}")

@router.post("/process-complete/{file_id}", response_model=PodcastResponse)
async def process_complete(file_id: str):
    """
    Complete workflow: Process PDF and generate single combined audio file
    
    Args:
        file_id: Unique identifier of the uploaded file
        
    Returns:
        PodcastResponse with script and combined audio information
    """
    try:
        # Check if file exists
        file_path = settings.UPLOAD_DIR / f"{file_id}.pdf"
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="File not found. Please upload the file first."
            )
        
        # Step 1: Process PDF to script
        script_content, script_path = crew_service.process_pdf_to_script(file_path)
        
        # Step 2: Generate combined audio from script
        audio_file, total_segments = await tts_service.generate_complete_podcast(
            script_path
        )
        
        # Get audio duration
        duration = tts_service.get_audio_duration(Path(audio_file))
        
        # Clean up uploaded file
        file_path.unlink()
        
        return PodcastResponse(
            status="success",
            script_filename=script_path.name,
            audio_file=audio_file,
            duration=duration,
            total_segments=total_segments,
            message="Podcast generated successfully"
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

@router.get("/download-audio/{script_name}")
async def download_audio(script_name: str):
    """
    Download the complete combined audio file
    
    Args:
        script_name: Name of the script (without .txt extension)
        
    Returns:
        FileResponse with the combined audio file
    """
    try:
        # Remove .txt if present
        script_base = script_name.replace('.txt', '')
        audio_path = settings.AUDIO_DIR / script_base / "podcast_complete.mp3"
        
        if not audio_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Audio file not found"
            )
        
        return FileResponse(
            path=audio_path,
            filename=f"{script_base}_podcast.mp3",
            media_type='audio/mpeg'
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

@router.get("/audio-info/{script_name}")
async def get_audio_info(script_name: str):
    """
    Get information about the combined audio file
    
    Args:
        script_name: Name of the script
        
    Returns:
        Audio file information including duration
    """
    try:
        audio_folder = settings.AUDIO_DIR / script_name.replace('.txt', '')
        audio_file = audio_folder / "podcast_complete.mp3"
        
        if not audio_file.exists():
            return {
                "status": "success",
                "audio_exists": False,
                "message": "No audio file found for this script"
            }
        
        # Get audio duration
        duration = tts_service.get_audio_duration(audio_file)
        file_size = audio_file.stat().st_size
        
        return {
            "status": "success",
            "audio_exists": True,
            "audio_file": str(audio_file),
            "duration": duration,
            "file_size": file_size,
            "duration_formatted": f"{int(duration // 60)}:{int(duration % 60):02d}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))