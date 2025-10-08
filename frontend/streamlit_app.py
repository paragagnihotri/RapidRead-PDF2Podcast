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
    .error-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #F8D7DA;
        border: 1px solid #F5C6CB;
        color: #721C24;
        margin: 1rem 0;
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

def process_pdf(file_id):
    """Process uploaded PDF"""
    try:
        response = requests.post(f"{API_BASE_URL}/process/{file_id}")
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

# Main UI
st.title("🎙️ PDF to Podcast Converter")
st.markdown("Transform your PDF documents into engaging podcast scripts using AI")

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
    engaging podcast-style conversation scripts between two speakers: 
    **Adam** and **Eve**.
    
    ### Features:
    - 📄 PDF text extraction
    - 🧹 Content cleaning
    - 🔍 Topic analysis
    - ✍️ Natural dialogue generation
    - 🎭 Expressive conversations
    - 📥 Script download
    """)
    
    st.header("⚙️ Settings")
    st.info("Using Gemini 2.0 Flash model")
    
    st.header("📚 Previous Scripts")
    scripts = list_scripts()
    if scripts:
        for script in scripts[:5]:  # Show last 5 scripts
            if st.button(f"📄 {script}", key=script):
                content = download_script(script)
                if content:
                    st.session_state.script_content = content.decode('utf-8')
                    st.session_state.script_filename = script
                    st.rerun()
    else:
        st.write("No scripts generated yet")

# Main content area
tab1, tab2 = st.tabs(["📤 Upload & Generate", "📝 View Script"])

with tab1:
    st.header("Upload PDF Document")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF document to convert into a podcast script"
    )
    
    if uploaded_file:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.success(f"✅ File uploaded: **{uploaded_file.name}** ({uploaded_file.size / 1024:.2f} KB)")
        
        with col2:
            if st.button("🚀 Generate Script", type="primary"):
                with st.spinner("Processing..."):
                    # Upload file
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("⬆️ Uploading PDF...")
                    progress_bar.progress(20)
                    upload_result = upload_pdf(uploaded_file)
                    
                    if "error" in upload_result:
                        st.error(f"❌ Upload failed: {upload_result['error']}")
                    else:
                        file_id = upload_result.get("file_id")
                        st.session_state.file_id = file_id
                        
                        status_text.text("🧹 Cleaning PDF text...")
                        progress_bar.progress(40)
                        time.sleep(0.5)
                        
                        status_text.text("🔍 Analyzing content...")
                        progress_bar.progress(60)
                        time.sleep(0.5)
                        
                        status_text.text("✍️ Writing dialogue...")
                        progress_bar.progress(80)
                        
                        # Process PDF
                        process_result = process_pdf(file_id)
                        
                        if "error" in process_result:
                            st.error(f"❌ Processing failed: {process_result['error']}")
                            progress_bar.empty()
                            status_text.empty()
                        else:
                            progress_bar.progress(100)
                            status_text.text("✅ Script generated successfully!")
                            
                            st.session_state.script_content = process_result.get("script")
                            st.session_state.script_filename = process_result.get("filename")
                            
                            time.sleep(1)
                            progress_bar.empty()
                            status_text.empty()
                            
                            st.balloons()
                            st.success("🎉 Podcast script generated successfully!")
                            st.info("👉 Switch to the 'View Script' tab to see your generated script")

with tab2:
    st.header("Generated Podcast Script")
    
    if st.session_state.script_content:
        col1, col2 = st.columns([4, 1])
        
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
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Characters", f"{char_count:,}")
        with col2:
            st.metric("Words", f"{word_count:,}")
        with col3:
            est_duration = word_count / 150  # Assuming 150 words per minute
            st.metric("Est. Duration", f"{est_duration:.1f} min")
    else:
        st.info("👆 Upload and generate a script to view it here")
        st.markdown("""
        ### What to expect:
        - **Natural dialogue** between Adam and Eve
        - **Comprehensive coverage** of all PDF topics
        - **Engaging conversation** with humor and expressions
        - **Audio-ready script** without stage directions
        """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Built with ❤️ using FastAPI, Streamlit, and CrewAI</p>",
    unsafe_allow_html=True
)