import pymupdf as pdf
from pathlib import Path
from typing import Optional

class PDFService:
    """Service for handling PDF operations"""
    
    @staticmethod
    def extract_text(file_path: Path) -> str:
        """
        Extract text content from a PDF file
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content
            
        Raises:
            Exception: If PDF cannot be opened or read
        """
        try:
            source_doc = pdf.open(str(file_path))
            text = ""
            
            for page_num in range(len(source_doc)):
                page = source_doc[page_num]
                text += page.get_text()
            
            source_doc.close()
            return text
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    @staticmethod
    def validate_pdf(file_path: Path) -> bool:
        """
        Validate if the file is a valid PDF
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if valid PDF, False otherwise
        """
        try:
            doc = pdf.open(str(file_path))
            doc.close()
            return True
        except:
            return False