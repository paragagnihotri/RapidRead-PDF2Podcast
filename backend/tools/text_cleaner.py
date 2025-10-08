from crewai.tools import BaseTool
import re

class TextCleaner(BaseTool):
    """Custom tool for cleaning extracted PDF text"""
    
    name: str = "Text Cleaner"
    description: str = "Cleans extracted PDF text by removing extra whitespace, line breaks, and redundant headers/footers while preserving original content."

    def _run(self, raw_content: str) -> str:
        """
        Clean PDF text by removing artifacts and normalizing formatting
        
        Args:
            raw_content: Raw text extracted from PDF
            
        Returns:
            Cleaned text with artifacts removed
        """
        # Remove common PDF artifacts (headers, footers, page numbers)
        new_text = re.sub(
            r'(?im)^\s*(?:Page\s+\d+|\d+\s+of\s+\d+|Confidential|Draft|Version\s+\d+\.?\d*|Document ID:?\s*\w*|Date:?\s*[\d/-]+)\s*$',
            '', raw_content, flags=re.MULTILINE
        )
        
        # Normalize excessive line breaks
        new_text = re.sub(r'\n{3,}', '\n\n', new_text)
        
        # Strip whitespace from each line
        lines = [line.strip() for line in new_text.split('\n')]
        
        # Remove leading empty lines
        while lines and not lines[0]:
            lines.pop(0)
        
        # Remove trailing empty lines
        while lines and not lines[-1]:
            lines.pop()
        
        # Rejoin lines
        new_text = '\n'.join(lines)
        
        # Normalize spaces
        new_text = re.sub(r' +', ' ', new_text)
        new_text = re.sub(r' \n', '\n', new_text)
        
        return new_text.strip()