import streamlit as st
import requests
import time
from pathlib import Path
import base64

# Configuration
API_BASE_URL = "http://localhost:8000/api"

# Page config
st.set_page_config(
    page_title="PDF to Podcast Converter",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #D4EDDA;
        border: 1px solid #C3E6CB;
        color: #155724;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #D1ECF1;
        border: 1px solid #BEE5EB;
        color: #0C5460;
        margin: 1rem 0;
    }
    .audio-player {
        margin: 1rem 0;
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'file_id' not in st.session_state:
    st.session_state.file_id = None
if 'script_content' not in st.session_state:
    st.session_state.script_content = None
if 'script_filename' not in st.session_state:
    st.session_state.script_filename = None
if 'audio_files' not in st.session_state:
    st.session_state.audio_files = []
if 'current_segment' not in st.session_state:
    st.session_state.current_segment = 0

def check_api_health():
    """Check if the FastAPI backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def upload_pdf(file):
    """Upload PDF file to backend"""
    try:
        files = {"file": (file.name, file, "application/pdf")}
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def process_complete(file_id):
    """Process uploaded PDF and generate audio"""
    try:
        response = requests.post(f"{API_BASE_URL}/process-complete/{file_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def generate_audio(script_filename):
    """Generate audio from script"""
    try:
        response = requests.post(f"{API_BASE_URL}/generate-audio/{script_filename}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def download_script(filename):
    """Download generated script"""
    try:
        response = requests.get(f"{API_BASE_URL}/download/{filename}")
        response.raise_for_status()
        return response.content
    except Exception as e:
        return None

def list_scripts():
    """List all generated scripts"""
    try:
        response = requests.get(f"{API_BASE_URL}/scripts")
        response.raise_for_status()
        return response.json().get("scripts", [])
    except:
        return []

def get_audio_segments(script_name):
    """Get audio segments for a script"""
    try:
        # Remove .txt extension and get base name
        script_base = script_name.replace('.txt', '')
        response = requests.get(f"{API_BASE_URL}/audio-segments/{script_base}")
        response.raise_for_status()
        return response.json()
    except:
        return {"audio_files": [], "total_segments": 0}

def get_audio_url(script_name, audio_filename):
    """Get URL for audio file"""
    script_base = script_name.replace('.txt', '')
    return f"{API_BASE_URL}/download-audio/{script_base}/{audio_filename}"

# Main UI
st.title("🎙️ PDF to Podcast Converter")
st.markdown("Transform your PDF documents into engaging podcast scripts and audio")

# Check API health
if not check_api_health():
    st.error("⚠️ Backend API is not running. Please start the FastAPI server first.")
    st.code("python -m uvicorn backend.main:app --reload", language="bash")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("📋 About")
    st.markdown("""
    This application converts PDF documents into natural, 
    engaging podcast-style conversations and audio between two speakers: 
    **Adam** and **Eve**.
    
    ### Features:
    - 📄 PDF text extraction
    - 🧹 Content cleaning
    - 🔍 Topic analysis
    - ✍️ Natural dialogue generation
    - 🎭 Expressive conversations
    - 🎙️ Audio generation (TTS)
    - 🎵 Podcast playback
    """)
    
    st.header("⚙️ Settings")
    st.info("Using Gemini 2.0 Flash model")
    st.info("🎤 Voices: Andrew (Adam) & Aria (Eve)")
    
    st.header("📚 Previous Podcasts")
    scripts = list_scripts()
    if scripts:
        for script in scripts[:5]:  # Show last 5 scripts
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"📄 {script}", key=f"load_{script}"):
                    content = download_script(script)
                    if content:
                        st.session_state.script_content = content.decode('utf-8')
                        st.session_state.script_filename = script
                        
                        # Load audio segments if available
                        audio_data = get_audio_segments(script)
                        st.session_state.audio_files = audio_data.get("audio_files", [])
                        st.rerun()
            with col2:
                # Check if audio exists
                audio_data = get_audio_segments(script)
                if audio_data.get("total_segments", 0) > 0:
                    st.write("🎵")
    else:
        st.write("No podcasts generated yet")

# Main content area
tab1, tab2, tab3 = st.tabs(["📤 Upload & Generate", "📝 View Script", "🎵 Listen to Podcast"])

with tab1:
    st.header("Upload PDF Document")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        generation_mode = st.radio(
            "Generation Mode:",
            ["Complete Podcast (Script + Audio)", "Script Only"],
            help="Complete mode generates both script and audio. Script only is faster."
        )
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF document to convert into a podcast"
    )
    
    if uploaded_file:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.success(f"✅ File uploaded: **{uploaded_file.name}** ({uploaded_file.size / 1024:.2f} KB)")
        
        with col2:
            button_text = "🚀 Generate Podcast" if generation_mode.startswith("Complete") else "📝 Generate Script"
            if st.button(button_text, type="primary"):
                with st.spinner("Processing..."):
                    # Upload file
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("⬆️ Uploading PDF...")
                    progress_bar.progress(10)
                    upload_result = upload_pdf(uploaded_file)
                    
                    if "error" in upload_result:
                        st.error(f"❌ Upload failed: {upload_result['error']}")
                    else:
                        file_id = upload_result.get("file_id")
                        st.session_state.file_id = file_id
                        
                        if generation_mode.startswith("Complete"):
                            # Complete workflow
                            status_text.text("🧹 Cleaning PDF text...")
                            progress_bar.progress(20)
                            
                            status_text.text("🔍 Analyzing content...")
                            progress_bar.progress(40)
                            
                            status_text.text("✍️ Writing dialogue...")
                            progress_bar.progress(60)
                            
                            status_text.text("🎙️ Generating audio (this may take a few minutes)...")
                            progress_bar.progress(70)
                            
                            # Process complete
                            process_result = process_complete(file_id)
                            
                            if "error" in process_result:
                                st.error(f"❌ Processing failed: {process_result['error']}")
                                progress_bar.empty()
                                status_text.empty()
                            else:
                                progress_bar.progress(100)
                                status_text.text("✅ Podcast generated successfully!")
                                
                                # Load script
                                script_filename = process_result.get("script_filename")
                                script_content = download_script(script_filename)
                                
                                st.session_state.script_content = script_content.decode('utf-8') if script_content else ""
                                st.session_state.script_filename = script_filename
                                st.session_state.audio_files = process_result.get("audio_files", [])
                                
                                time.sleep(1)
                                progress_bar.empty()
                                status_text.empty()
                                
                                st.balloons()
                                st.success(f"🎉 Complete podcast generated! {process_result.get('total_segments', 0)} audio segments created")
                                st.info("👉 Switch to the 'Listen to Podcast' tab to play your audio")
                        
                        else:
                            # Script only
                            status_text.text("🧹 Cleaning PDF text...")
                            progress_bar.progress(30)
                            
                            status_text.text("🔍 Analyzing content...")
                            progress_bar.progress(60)
                            
                            status_text.text("✍️ Writing dialogue...")
                            progress_bar.progress(90)
                            
                            # Process script only
                            from backend.services.crew_service import CrewService
                            from pathlib import Path
                            
                            try:
                                # Process via API
                                response = requests.post(f"{API_BASE_URL}/process/{file_id}")
                                response.raise_for_status()
                                process_result = response.json()
                                
                                progress_bar.progress(100)
                                status_text.text("✅ Script generated successfully!")
                                
                                st.session_state.script_content = process_result.get("script")
                                st.session_state.script_filename = process_result.get("filename")
                                st.session_state.audio_files = []
                                
                                time.sleep(1)
                                progress_bar.empty()
                                status_text.empty()
                                
                                st.success("🎉 Script generated successfully!")
                                st.info("👉 Switch to the 'View Script' tab to see your script. You can generate audio later.")
                                
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                                progress_bar.empty()
                                status_text.empty()

with tab2:
    st.header("Generated Podcast Script")
    
    if st.session_state.script_content:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.success(f"📄 **{st.session_state.script_filename}**")
        
        with col2:
            if st.download_button(
                label="⬇️ Download",
                data=st.session_state.script_content,
                file_name=st.session_state.script_filename,
                mime="text/plain"
            ):
                st.success("Downloaded!")
        
        with col3:
            # Generate audio button if not already generated
            if not st.session_state.audio_files:
                if st.button("🎙️ Generate Audio"):
                    with st.spinner("Generating audio... This may take a few minutes."):
                        result = generate_audio(st.session_state.script_filename)
                        if "error" not in result:
                            st.session_state.audio_files = result.get("audio_files", [])
                            st.success(f"✅ Generated {result.get('total_segments', 0)} audio segments!")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {result['error']}")
        
        # Display script in a text area
        st.text_area(
            "Script Content",
            value=st.session_state.script_content,
            height=600,
            disabled=False,
            key="script_display"
        )
        
        # Character count
        char_count = len(st.session_state.script_content)
        word_count = len(st.session_state.script_content.split())
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Characters", f"{char_count:,}")
        with col2:
            st.metric("Words", f"{word_count:,}")
        with col3:
            est_duration = word_count / 150  # Assuming 150 words per minute
            st.metric("Est. Duration", f"{est_duration:.1f} min")
        with col4:
            audio_status = "✅ Ready" if st.session_state.audio_files else "⏳ Not Generated"
            st.metric("Audio Status", audio_status)
    else:
        st.info("👆 Upload and generate a script to view it here")
        st.markdown("""
        ### What to expect:
        - **Natural dialogue** between Adam and Eve
        - **Comprehensive coverage** of all PDF topics
        - **Engaging conversation** with humor and expressions
        - **Audio-ready script** without stage directions
        """)

with tab3:
    st.header("🎵 Listen to Your Podcast")
    
    if st.session_state.script_filename and st.session_state.audio_files:
        st.success(f"🎙️ Podcast: **{st.session_state.script_filename.replace('.txt', '')}**")
        st.info(f"📊 Total segments: **{len(st.session_state.audio_files)}**")
        
        # Audio player controls
        col1, col2 = st.columns([3, 1])
        
        with col1:
            segment_index = st.slider(
                "Select Segment",
                0,
                len(st.session_state.audio_files) - 1,
                st.session_state.current_segment,
                format="Segment %d"
            )
            st.session_state.current_segment = segment_index
        
        with col2:
            st.metric("Current", f"{segment_index + 1}/{len(st.session_state.audio_files)}")
        
        # Get current audio file
        if 0 <= segment_index < len(st.session_state.audio_files):
            audio_filename = st.session_state.audio_files[segment_index]
            audio_url = get_audio_url(st.session_state.script_filename, Path(audio_filename).name)
            
            # Display speaker info
            speaker = "Adam 👨" if "Adam" in audio_filename else "Eve 👩"
            st.markdown(f"### Currently Playing: **{speaker}**")
            
            # Audio player
            try:
                audio_response = requests.get(audio_url)
                if audio_response.status_code == 200:
                    st.audio(audio_response.content, format='audio/mp3')
                else:
                    st.warning("Audio file not found. Please regenerate the audio.")
            except Exception as e:
                st.error(f"Error loading audio: {str(e)}")
        
        st.markdown("---")
        
        # Segment list
        st.subheader("📋 All Segments")
        
        for idx, audio_file in enumerate(st.session_state.audio_files):
            filename = Path(audio_file).name
            speaker = "👨 Adam" if "Adam" in filename else "👩 Eve"
            
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**Segment {idx + 1}:** {speaker}")
            with col2:
                if st.button(f"▶️ Play", key=f"play_{idx}"):
                    st.session_state.current_segment = idx
                    st.rerun()
        
    elif st.session_state.script_filename and not st.session_state.audio_files:
        st.warning("⚠️ Audio not generated yet for this script")
        st.info("Go to the 'View Script' tab and click '🎙️ Generate Audio' to create audio segments")
        
        if st.button("🎙️ Generate Audio Now"):
            with st.spinner("Generating audio... This may take a few minutes."):
                result = generate_audio(st.session_state.script_filename)
                if "error" not in result:
                    st.session_state.audio_files = result.get("audio_files", [])
                    st.success(f"✅ Generated {result.get('total_segments', 0)} audio segments!")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result['error']}")
    else:
        st.info("👆 Generate a podcast first to listen to it here")
        st.markdown("""
        ### How it works:
        1. Upload a PDF document
        2. Choose "Complete Podcast" or "Script Only"
        3. Wait for generation (1-5 minutes)
        4. Listen to your AI-generated podcast!
        
        ### Features:
        - 🎙️ **Natural voices** (Andrew for Adam, Aria for Eve)
        - 🎵 **Sequential playback** of all segments
        - ⏯️ **Individual segment control**
        - 📊 **Progress tracking**
        """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Built with ❤️ using FastAPI, Streamlit, CrewAI, and Edge TTS</p>",
    unsafe_allow_html=True
)