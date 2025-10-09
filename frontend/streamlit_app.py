import streamlit as st
import requests
import time
from pathlib import Path

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
    .audio-player {
        margin: 2rem 0;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .audio-info {
        color: white;
        font-size: 1.1rem;
        margin-bottom: 1rem;
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
if 'audio_file' not in st.session_state:
    st.session_state.audio_file = None
if 'audio_duration' not in st.session_state:
    st.session_state.audio_duration = None

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

def get_audio_info(script_name):
    """Get audio information for a script"""
    try:
        script_base = script_name.replace('.txt', '')
        response = requests.get(f"{API_BASE_URL}/audio-info/{script_base}")
        response.raise_for_status()
        return response.json()
    except:
        return {"audio_exists": False}

def get_audio_url(script_name):
    """Get URL for combined audio file"""
    script_base = script_name.replace('.txt', '')
    return f"{API_BASE_URL}/download-audio/{script_base}"

def format_duration(seconds):
    """Format duration in seconds to MM:SS"""
    if not seconds:
        return "00:00"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

# Main UI
st.title("🎙️ PDF to Podcast Converter")
st.markdown("Transform your PDF documents into engaging podcast audio")

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
    engaging podcast audio with two speakers: 
    **Adam** and **Eve**.
    
    ### Features:
    - 📄 PDF text extraction
    - 🧹 Content cleaning
    - 🔍 Topic analysis
    - ✍️ Natural dialogue generation
    - 🎙️ Complete audio podcast
    - 🎵 Single MP3 file output
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
                        
                        # Load audio info if available
                        audio_info = get_audio_info(script)
                        if audio_info.get("audio_exists"):
                            st.session_state.audio_file = audio_info.get("audio_file")
                            st.session_state.audio_duration = audio_info.get("duration")
                        else:
                            st.session_state.audio_file = None
                            st.session_state.audio_duration = None
                        st.rerun()
            with col2:
                # Check if audio exists
                audio_info = get_audio_info(script)
                if audio_info.get("audio_exists"):
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
                                st.session_state.audio_file = process_result.get("audio_file")
                                st.session_state.audio_duration = process_result.get("duration")
                                
                                time.sleep(1)
                                progress_bar.empty()
                                status_text.empty()
                                
                                st.balloons()
                                duration_text = format_duration(process_result.get("duration", 0))
                                st.success(f"🎉 Complete podcast generated! Duration: {duration_text}")
                                st.info("👉 Switch to the 'Listen to Podcast' tab to play your audio")
                        
                        else:
                            # Script only
                            status_text.text("🧹 Cleaning PDF text...")
                            progress_bar.progress(30)
                            
                            status_text.text("🔍 Analyzing content...")
                            progress_bar.progress(60)
                            
                            status_text.text("✍️ Writing dialogue...")
                            progress_bar.progress(90)
                            
                            try:
                                # Process via API
                                response = requests.post(f"{API_BASE_URL}/process/{file_id}")
                                response.raise_for_status()
                                process_result = response.json()
                                
                                progress_bar.progress(100)
                                status_text.text("✅ Script generated successfully!")
                                
                                st.session_state.script_content = process_result.get("script")
                                st.session_state.script_filename = process_result.get("filename")
                                st.session_state.audio_file = None
                                st.session_state.audio_duration = None
                                
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
                label="⬇️ Download Script",
                data=st.session_state.script_content,
                file_name=st.session_state.script_filename,
                mime="text/plain"
            ):
                st.success("Downloaded!")
        
        with col3:
            # Generate audio button if not already generated
            if not st.session_state.audio_file:
                if st.button("🎙️ Generate Audio", key="gen_audio"):
                    with st.spinner("Generating audio... This may take a few minutes."):
                        result = generate_audio(st.session_state.script_filename)
                        if "error" not in result:
                            st.session_state.audio_file = result.get("audio_file")
                            st.session_state.audio_duration = result.get("duration")
                            duration_text = format_duration(result.get("duration", 0))
                            st.success(f"✅ Audio generated! Duration: {duration_text}")
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
        
        # Statistics
        char_count = len(st.session_state.script_content)
        word_count = len(st.session_state.script_content.split())
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Characters", f"{char_count:,}")
        with col2:
            st.metric("Words", f"{word_count:,}")
        with col3:
            if st.session_state.audio_duration:
                duration_text = format_duration(st.session_state.audio_duration)
                st.metric("Audio Duration", duration_text)
            else:
                est_duration = word_count / 150
                st.metric("Est. Duration", f"{est_duration:.1f} min")
        with col4:
            audio_status = "✅ Ready" if st.session_state.audio_file else "⏳ Not Generated"
            st.metric("Audio Status", audio_status)
    else:
        st.info("👆 Upload and generate a script to view it here")
        st.markdown("""
        ### What to expect:
        - **Natural dialogue** between Adam and Eve
        - **Comprehensive coverage** of all PDF topics
        - **Engaging conversation** with humor and expressions
        - **Single audio file** ready for listening
        """)

with tab3:
    st.header("🎵 Listen to Your Podcast")
    
    if st.session_state.script_filename and st.session_state.audio_file:
        # Audio player section
        st.markdown('<div class="audio-player">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f'<p class="audio-info">🎙️ <b>{st.session_state.script_filename.replace(".txt", "")}</b></p>', unsafe_allow_html=True)
        with col2:
            if st.session_state.audio_duration:
                duration_text = format_duration(st.session_state.audio_duration)
                st.markdown(f'<p class="audio-info">⏱️ {duration_text}</p>', unsafe_allow_html=True)
        
        # Get audio URL and play
        audio_url = get_audio_url(st.session_state.script_filename)
        
        try:
            audio_response = requests.get(audio_url)
            if audio_response.status_code == 200:
                st.audio(audio_response.content, format='audio/mp3')
            else:
                st.warning("⚠️ Audio file not found. Please regenerate the audio.")
        except Exception as e:
            st.error(f"❌ Error loading audio: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Download button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            try:
                audio_response = requests.get(audio_url)
                if audio_response.status_code == 200:
                    st.download_button(
                        label="📥 Download Complete Podcast (MP3)",
                        data=audio_response.content,
                        file_name=f"{st.session_state.script_filename.replace('.txt', '')}_podcast.mp3",
                        mime="audio/mpeg",
                        use_container_width=True
                    )
            except:
                pass
        
        st.markdown("---")
        
        # Podcast info
        st.subheader("📊 Podcast Information")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("**Format:** MP3 (192kbps)")
        with col2:
            st.info("**Speakers:** Adam & Eve")
        with col3:
            if st.session_state.audio_duration:
                file_size = st.session_state.audio_duration * 24  # Approximate KB
                st.info(f"**Size:** ~{file_size/1024:.1f} MB")
        
        st.success("✨ Your podcast is ready! Press play to listen or download for offline playback.")
        
    elif st.session_state.script_filename and not st.session_state.audio_file:
        st.warning("⚠️ Audio not generated yet for this script")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎙️ Generate Audio Now", type="primary", use_container_width=True):
                with st.spinner("Generating audio... This may take a few minutes."):
                    result = generate_audio(st.session_state.script_filename)
                    if "error" not in result:
                        st.session_state.audio_file = result.get("audio_file")
                        st.session_state.audio_duration = result.get("duration")
                        duration_text = format_duration(result.get("duration", 0))
                        st.success(f"✅ Audio generated! Duration: {duration_text}")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result['error']}")
        
        st.info("💡 Go to the 'View Script' tab to review your script before generating audio")
        
    else:
        st.info("👆 Generate a podcast first to listen to it here")
        st.markdown("""
        ### How it works:
        1. **Upload** a PDF document
        2. **Choose** "Complete Podcast" or "Script Only"
        3. **Wait** for generation (3-8 minutes)
        4. **Listen** to your AI-generated podcast!
        
        ### Features:
        - 🎙️ **Natural voices** (Andrew for Adam, Aria for Eve)
        - 🎵 **Single audio file** - no interruptions
        - 📥 **Download** for offline listening
        - ⚡ **Instant playback** in browser
        - 🎧 **High quality** MP3 (192kbps)
        """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Built with ❤️ using FastAPI, Streamlit, CrewAI, and Edge TTS</p>",
    unsafe_allow_html=True
)
