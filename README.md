# 🎙️ PDF to Podcast Converter

Transform your PDF documents into engaging, natural podcast-style conversation scripts **and audio** using AI-powered multi-agent system with text-to-speech capabilities.

## 🌟 Features

- **PDF Processing**: Extract and clean text from PDF documents
- **Content Analysis**: Intelligent topic identification and structuring
- **Natural Dialogue Generation**: Create authentic conversations between two speakers (Adam & Eve)
- **Audio Generation**: Convert scripts to natural-sounding speech using Edge TTS
- **Audio Playback**: Listen to your podcast directly in the browser
- **Dual Mode**: Generate script only or complete podcast with audio
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Modern UI**: Beautiful Streamlit frontend with audio player
- **Modular Architecture**: Clean, maintainable, and extensible codebase

## 🎤 Voice Cast

- **Adam** - Voiced by `en-US-AndrewNeural` (Male, US English)
- **Eve** - Voiced by `en-US-AriaNeural` (Female, US English)

## 🏗️ Architecture

```
┌─────────────────┐
│   Streamlit UI  │
│   (Frontend)    │
│  + Audio Player │
└────────┬────────┘
         │
         │ HTTP Requests
         │
┌────────▼────────┐
│   FastAPI       │
│   (Backend)     │
└────────┬────────┘
         │
    ┌────┴────────────┐
    │         │       │
┌───▼───┐ ┌──▼──┐ ┌─▼────┐
│  PDF  │ │Crew │ │ TTS  │
│Service│ │Svc  │ │ Svc  │
└───────┘ └──┬──┘ └──────┘
             │
      ┌──────┴──────┐
      │   CrewAI    │
      │  5 Agents   │
      └─────────────┘
```

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Setup Steps

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd pdf-to-podcast
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
```

5. **Create necessary directories**
```bash
mkdir -p uploads outputs
```

## 🚀 Running the Application

### Start Backend (FastAPI)

```bash
# From project root
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Start Frontend (Streamlit)

Open a new terminal and run:

```bash
# From project root
streamlit run frontend/streamlit_app.py
```

The UI will open automatically in your browser at `http://localhost:8501`

## 📖 Usage

### Via Streamlit UI (Recommended)

1. Open the Streamlit app in your browser
2. Choose generation mode:
   - **Complete Podcast**: Generates script + audio (takes 3-5 minutes)
   - **Script Only**: Faster, generates script only (takes 1-2 minutes)
3. Upload a PDF document
4. Click "Generate Podcast" or "Generate Script"
5. Wait for processing
6. **View Script**: Read and download the generated dialogue
7. **Listen to Podcast**: Play audio segments directly in browser

### Generation Modes

#### Complete Podcast (Script + Audio)
```
Upload PDF → Generate Script → Generate Audio → Listen
```
- Best for immediate listening
- Takes 3-5 minutes
- Produces script + MP3 segments

#### Script Only (Faster)
```
Upload PDF → Generate Script → (Optional: Generate Audio Later)
```
- Faster processing (1-2 minutes)
- Can generate audio later from "View Script" tab
- Good for reviewing content first

### Via API

**1. Upload PDF:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.pdf"
```

Response:
```json
{
  "status": "success",
  "message": "File uploaded successfully",
  "file_id": "uuid-here"
}
```

**2. Process PDF:**
```bash
curl -X POST "http://localhost:8000/api/process/{file_id}" \
  -H "accept: application/json"
```

**3. Generate Audio from Script:**
```bash
curl -X POST "http://localhost:8000/api/generate-audio/{script_filename}" \
  -H "accept: application/json"
```

**4. Complete Workflow (Script + Audio):**
```bash
curl -X POST "http://localhost:8000/api/process-complete/{file_id}" \
  -H "accept: application/json"
```

**5. Download Audio Segment:**
```bash
curl -X GET "http://localhost:8000/api/download-audio/{script_name}/{audio_filename}" \
  --output segment.mp3
```

**6. List Audio Segments:**
```bash
curl -X GET "http://localhost:8000/api/audio-segments/{script_name}"
```

**7. Download Script:**
```bash
curl -X GET "http://localhost:8000/api/download/{filename}" \
  --output podcast_script.txt
```

**8. List All Scripts:**
```bash
curl -X GET "http://localhost:8000/api/scripts"
```

## 🤖 AI Agents

The application uses 5 specialized CrewAI agents:

1. **PDF Cleaner Agent**: Removes PDF artifacts while preserving content
2. **Content Analyzer Agent**: Identifies topics, themes, and key points
3. **Dialogue Builder Agent**: Designs conversation structure and flow
4. **Script Writer Agent**: Writes natural, expressive dialogue
5. **Quality Assurance Agent**: Reviews and polishes the final script

## 📁 Project Structure

```
pdf-to-podcast/
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Configuration
│   ├── models.py               # Pydantic models
│   ├── routes.py               # API routes
│   ├── agents/
│   │   ├── __init__.py
│   │   └── crew_agents.py      # Agent definitions
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── crew_tasks.py       # Task definitions
│   ├── tools/
│   │   ├── __init__.py
│   │   └── text_cleaner.py     # Custom tools
│   └── services/
│       ├── __init__.py
│       ├── pdf_service.py      # PDF operations
│       └── crew_service.py     # CrewAI orchestration
├── frontend/
│   └── streamlit_app.py        # Streamlit UI
├── uploads/                    # Temporary uploads
├── outputs/                    # Generated scripts
├── .env                        # Environment variables
├── requirements.txt
└── README.md
```

## 🔧 Configuration

Edit `.env` file to customize:

- `GEMINI_API_KEY`: Your Gemini API key (required)
- `BACKEND_HOST`: Backend server host (default: 0.0.0.0)
- `BACKEND_PORT`: Backend server port (default: 8000)
- `UPLOAD_DIR`: Directory for uploaded files (default: uploads)
- `OUTPUT_DIR`: Directory for generated scripts (default: outputs)

### TTS Voice Configuration

You can customize voices in `backend/config.py`:

```python
# Current voices
ADAM_VOICE = "en-US-AndrewNeural"  # Male voice
EVE_VOICE = "en-US-AriaNeural"     # Female voice

# Alternative voices available:
# Male: en-US-EricNeural, en-US-BrianNeural, en-GB-RyanNeural
# Female: en-US-SaraNeural, en-GB-SoniaNeural, en-AU-NatashaNeural
```

### Audio Settings

```python
TTS_RATE = "+3%"    # Speech rate (faster/slower)
TTS_VOLUME = "+5%"  # Volume adjustment
TTS_PITCH = "+1Hz"  # Pitch variation
```

## 🎯 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/` | Health check |
| POST | `/api/upload` | Upload PDF file |
| POST | `/api/process/{file_id}` | Generate script only |
| POST | `/api/generate-audio/{script_filename}` | Generate audio from script |
| POST | `/api/process-complete/{file_id}` | Generate script + audio |
| GET | `/api/download/{filename}` | Download script |
| GET | `/api/download-audio/{script}/{audio}` | Download audio segment |
| GET | `/api/scripts` | List all scripts |
| GET | `/api/audio-segments/{script_name}` | List audio segments |

## 📝 Example Output

The generated podcasts feature:

### Script
- Natural speech patterns with fillers ("you know", "like", "actually")
- Emotional expressions (laughter, excitement, curiosity)
- Balanced dialogue between two speakers
- Technical accuracy with conversational flow
- Audio-ready format (no stage directions)

### Audio
- High-quality neural TTS voices
- Natural prosody and intonation
- Engaging conversational pace
- Individual MP3 segments for each dialogue turn
- M3U playlist for sequential playback
- Typical output: 20-50 segments depending on content

### File Structure
```
outputs/
├── podcast_script_20231215_143022.txt

audio_outputs/
└── podcast_script_20231215_143022/
    ├── segment_001_Adam.mp3
    ├── segment_002_Eve.mp3
    ├── segment_003_Adam.mp3
    ├── ...
    └── playlist.m3u
```

## 🛠️ Troubleshooting

**Backend not starting:**
- Check if port 8000 is available
- Verify GEMINI_API_KEY is set in .env
- Ensure all dependencies are installed

**Streamlit not connecting to backend:**
- Ensure backend is running on port 8000
- Check firewall settings
- Verify API_BASE_URL in streamlit_app.py

**PDF processing fails:**
- Check PDF is not corrupted
- Ensure PDF contains extractable text (not just images)
- Check backend logs for detailed errors

**Audio generation fails:**
- Check internet connection (Edge TTS requires online access)
- Verify script file exists in outputs directory
- Check audio_outputs directory permissions
- Try regenerating with smaller PDF first

**Audio not playing:**
- Check browser compatibility (Chrome/Edge recommended)
- Verify audio files were generated in audio_outputs folder
- Check browser console for errors
- Try downloading audio file directly

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with [CrewAI](https://github.com/joaomdmoura/crewAI)
- Powered by [Google Gemini](https://ai.google.dev/)
- UI with [Streamlit](https://streamlit.io/)
- API with [FastAPI](https://fastapi.tiangolo.com/)
- Text-to-Speech with [Edge TTS](https://github.com/rany2/edge-tts)

## ⚡ Performance Notes

- **Script Generation**: 1-3 minutes (depends on PDF size and content complexity)
- **Audio Generation**: 2-5 minutes (depends on script length, ~5-10 seconds per segment)
- **Complete Workflow**: 3-8 minutes total
- **Recommended PDF Size**: Under 50 pages for optimal performance

## 🎓 Use Cases

- 📚 **Educational Content**: Convert textbooks and papers into audio lessons
- 📰 **News & Articles**: Transform written content into podcast format
- 📊 **Reports & Documentation**: Make technical docs more accessible
- 🎯 **Training Materials**: Create audio training modules
- 📖 **Research Papers**: Listen to academic content on-the-go

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

**Made with ❤️ using AI agents**