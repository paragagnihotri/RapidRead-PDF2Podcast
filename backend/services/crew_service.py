from crewai import Crew
from pathlib import Path
from datetime import datetime
from backend.agents.crew_agents import create_agents
from backend.tasks.crew_tasks import create_tasks
from backend.services.pdf_service import PDFService
from backend.config import settings

class CrewService:
    """Service for orchestrating CrewAI workflow"""
    
    def __init__(self):
        self.pdf_service = PDFService()
        self.agents = create_agents()
        self.tasks = create_tasks(self.agents)
    
    def process_pdf_to_script(self, pdf_path: Path, output_filename: str = None) -> tuple[str, Path]:
        """
        Process a PDF file and generate a podcast script
        
        Args:
            pdf_path: Path to the PDF file
            output_filename: Custom output filename (optional)
            
        Returns:
            Tuple of (script_content, output_file_path)
            
        Raises:
            Exception: If processing fails
        """
        try:
            # Extract text from PDF
            raw_content = self.pdf_service.extract_text(pdf_path)
            
            if not raw_content.strip():
                raise ValueError("No text content found in PDF")
            
            # Create CrewAI crew
            crew = Crew(
                agents=list(self.agents.values()),
                tasks=list(self.tasks.values()),
                verbose=True
            )
            
            # Execute the crew workflow
            response = crew.kickoff(inputs={"raw_content": raw_content})
            
            # Generate output filename
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"podcast_script_{timestamp}.txt"
            
            output_path = settings.OUTPUT_DIR / output_filename
            
            # Save the script
            script_content = self._format_script(str(response), pdf_path.stem)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            return script_content, output_path
            
        except Exception as e:
            raise Exception(f"Error processing PDF to script: {str(e)}")
    
    def _format_script(self, script: str, pdf_name: str) -> str:
        """
        Format the final script with header
        
        Args:
            script: Raw script content
            pdf_name: Name of the PDF file
            
        Returns:
            Formatted script content
        """
        header = f"""PODCAST SCRIPT
{pdf_name}
{"=" * 100}

"""
        return header + script