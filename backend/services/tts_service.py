import edge_tts
import re
import os
from pathlib import Path
from typing import List, Tuple, Optional
from pydub import AudioSegment
import asyncio
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
        output_folder: Path,
        combine: bool = True
    ) -> Tuple[str, int]:
        """
        Generate audio from script - creates single combined MP3 file
        
        Args:
            script_content: Complete script text
            output_folder: Directory to save audio files
            combine: If True, combines all segments into one file (default: True)
            
        Returns:
            Tuple of (combined_audio_path, total_segments)
        """
        # Parse dialogues from script
        dialogues = self.parse_script(script_content)
        
        if not dialogues:
            raise ValueError("No dialogues found in script")
        
        # Create output folder
        output_folder.mkdir(parents=True, exist_ok=True)
        temp_folder = output_folder / "temp_segments"
        temp_folder.mkdir(parents=True, exist_ok=True)
        
        segment_files = []
        
        # Generate audio for each dialogue segment
        for idx, (speaker, text) in enumerate(dialogues, 1):
            # Select voice based on speaker
            voice = self.adam_voice if speaker == "Adam" else self.eve_voice
            
            # Create temporary segment file
            segment_file = temp_folder / f"segment_{idx:03d}_{speaker}.mp3"
            
            try:
                # Generate audio
                await self.text_to_speech(text, voice, segment_file)
                segment_files.append(str(segment_file))
                
            except Exception as e:
                print(f"Error generating segment {idx}: {e}")
                continue
        
        if not segment_files:
            raise Exception("No audio segments were generated")
        
        if combine:
            # Combine all segments into one file
            combined_audio_path = output_folder / "podcast_complete.mp3"
            self._combine_audio_segments(segment_files, combined_audio_path)
            
            # Clean up temporary segment files
            for segment_file in segment_files:
                try:
                    Path(segment_file).unlink()
                except:
                    pass
            
            # Remove temp folder
            try:
                temp_folder.rmdir()
            except:
                pass
            
            return str(combined_audio_path), len(dialogues)
        else:
            # Return list of segment files (old behavior)
            return segment_files, len(dialogues)
    
    def _combine_audio_segments(self, segment_files: List[str], output_path: Path) -> None:
        """
        Combine multiple audio segments into a single MP3 file
        
        Args:
            segment_files: List of paths to audio segment files
            output_path: Path where combined audio will be saved
        """
        # Initialize combined audio
        combined = AudioSegment.empty()
        
        # Add each segment with a small pause between speakers
        for segment_file in segment_files:
            try:
                audio = AudioSegment.from_mp3(segment_file)
                combined += audio
                # Add 300ms pause between segments for natural flow
                combined += AudioSegment.silent(duration=300)
            except Exception as e:
                print(f"Error adding segment {segment_file}: {e}")
                continue
        
        # Export combined audio
        combined.export(str(output_path), format="mp3", bitrate="192k")
    
    async def generate_complete_podcast(
        self, 
        script_file_path: Path
    ) -> Tuple[str, int]:
        """
        Generate complete podcast from script file as single MP3
        
        Args:
            script_file_path: Path to script text file
            
        Returns:
            Tuple of (combined_audio_path, total_segments)
        """
        # Read script content
        with open(script_file_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # Create output folder for this script
        script_name = script_file_path.stem
        output_folder = settings.AUDIO_DIR / script_name
        
        # Generate combined audio
        audio_path, total_segments = await self.generate_podcast_audio(
            script_content, 
            output_folder,
            combine=True
        )
        
        return audio_path, total_segments
    
    def get_audio_duration(self, audio_path: Path) -> float:
        """
        Get duration of audio file in seconds
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Duration in seconds
        """
        try:
            audio = AudioSegment.from_mp3(str(audio_path))
            return len(audio) / 1000.0  # Convert milliseconds to seconds
        except:
            return 0.0