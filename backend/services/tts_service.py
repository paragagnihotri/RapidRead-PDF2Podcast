import edge_tts
import re
import os
from pathlib import Path
from typing import List, Tuple, Optional
from backend.config import settings

class TTSService:
    """Service for Text-to-Speech conversion using Edge TTS"""
    
    def __init__(self):
        self.adam_voice = settings.ADAM_VOICE
        self.eve_voice = settings.EVE_VOICE
        self.rate = settings.TTS_RATE
        self.volume = settings.TTS_VOLUME
        self.pitch = settings.TTS_PITCH
    
    def parse_script(self, script_content: str) -> List[Tuple[str, str]]:
        """
        Parse script content to extract speaker dialogues
        
        Args:
            script_content: Raw script text with speaker labels
            
        Returns:
            List of tuples containing (speaker, dialogue_text)
        """
        # Pattern to match "Speaker: dialogue text" format
        pattern = r'(Adam|Eve):\s*(.+?)(?=\n(?:Adam:|Eve:|$))'
        matches = re.findall(pattern, script_content, re.DOTALL)
        
        dialogues = []
        for speaker, text in matches:
            text = text.strip()
            if text:
                dialogues.append((speaker, text))
        
        return dialogues
    
    async def text_to_speech(
        self, 
        text: str, 
        voice: str, 
        output_file: Path,
        rate: Optional[str] = None,
        volume: Optional[str] = None,
        pitch: Optional[str] = None
    ) -> None:
        """
        Convert text to speech using Edge TTS
        
        Args:
            text: Text to convert
            voice: Voice ID to use
            output_file: Path to save audio file
            rate: Speech rate adjustment
            volume: Volume adjustment
            pitch: Pitch adjustment
        """
        rate = rate or self.rate
        volume = volume or self.volume
        pitch = pitch or self.pitch
        
        communicate = edge_tts.Communicate(
            text, 
            voice, 
            rate=rate, 
            volume=volume, 
            pitch=pitch
        )
        await communicate.save(str(output_file))
    
    async def generate_podcast_audio(
        self, 
        script_content: str, 
        output_folder: Path
    ) -> Tuple[List[str], int]:
        """
        Generate audio segments from script
        
        Args:
            script_content: Complete script text
            output_folder: Directory to save audio files
            
        Returns:
            Tuple of (list of audio file paths, total segments)
        """
        # Parse dialogues from script
        dialogues = self.parse_script(script_content)
        
        if not dialogues:
            raise ValueError("No dialogues found in script")
        
        # Create output folder
        output_folder.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        
        # Generate audio for each dialogue segment
        for idx, (speaker, text) in enumerate(dialogues, 1):
            # Select voice based on speaker
            voice = self.adam_voice if speaker == "Adam" else self.eve_voice
            
            # Create output filename
            output_file = output_folder / f"segment_{idx:03d}_{speaker}.mp3"
            
            try:
                # Generate audio
                await self.text_to_speech(text, voice, output_file)
                generated_files.append(str(output_file))
                
            except Exception as e:
                print(f"Error generating segment {idx}: {e}")
                continue
        
        return generated_files, len(dialogues)
    
    def create_playlist(self, output_folder: Path) -> str:
        """
        Create M3U playlist file for audio segments
        
        Args:
            output_folder: Directory containing audio files
            
        Returns:
            Path to playlist file
        """
        playlist_file = output_folder / "playlist.m3u"
        
        # Get all MP3 files sorted by name
        files = sorted([f.name for f in output_folder.glob("*.mp3")])
        
        with open(playlist_file, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for file in files:
                f.write(f"#EXTINF:-1,{file}\n")
                f.write(f"{file}\n")
        
        return str(playlist_file)
    
    async def generate_complete_podcast(
        self, 
        script_file_path: Path
    ) -> Tuple[List[str], str, int]:
        """
        Generate complete podcast from script file
        
        Args:
            script_file_path: Path to script text file
            
        Returns:
            Tuple of (audio_files, playlist_file, total_segments)
        """
        # Read script content
        with open(script_file_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # Create output folder for this script
        script_name = script_file_path.stem
        output_folder = settings.AUDIO_DIR / script_name
        
        # Generate audio segments
        audio_files, total_segments = await self.generate_podcast_audio(
            script_content, 
            output_folder
        )
        
        # Create playlist
        playlist_file = self.create_playlist(output_folder)
        
        return audio_files, playlist_file, total_segments