import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import io
import os
from typing import Optional, List
import time
import json
import tempfile
import yt_dlp
import re
from config import API_ENDPOINT, API_TIMEOUT, PAGE_TITLE, PAGE_ICON, HIGH_CONFIDENCE_THRESHOLD, MEDIUM_CONFIDENCE_THRESHOLD

# Label mapping for deepfake detection results
LABEL_MAP = {
    0: "AI_GEN",
    1: "ANIME_1D", 
    2: "ANIME_2D",
    3: "VIDEO_GAME",
    4: "KLING",
    5: "HIGGSFIELD",
    6: "WAN",
    7: "MIDJOURNEY",
    8: "HAILUO",
    9: "RAY",
    10: "VEO",
    11: "RUNWAY",
    12: "SORA",
    13: "CHATGPT",
    14: "PIKA",
    15: "HUNYUAN",
    16: "VIDU"
}

def is_valid_instagram_url(url: str) -> bool:
    """Check if URL is a valid Instagram post URL"""
    instagram_patterns = [
        r'^https?://(www\.)?instagram\.com/p/[A-Za-z0-9_-]+/?',
        r'^https?://(www\.)?instagram\.com/reel/[A-Za-z0-9_-]+/?',
        r'^https?://(www\.)?instagram\.com/tv/[A-Za-z0-9_-]+/?'
    ]
    return any(re.match(pattern, url) for pattern in instagram_patterns)

def download_instagram_video(url: str) -> Optional[str]:
    """Download video from Instagram URL"""
    try:
        temp_dir = tempfile.mkdtemp()
        ydl_opts = {
            'outtmpl': os.path.join(temp_dir, 'instagram_video.%(ext)s'),
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
            for file in os.listdir(temp_dir):
                if file.startswith('instagram_video.'):
                    return os.path.join(temp_dir, file)
        return None
    except:
        return None

def cleanup_temp_files(file_path: str):
    """Clean up temporary downloaded files"""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            temp_dir = os.path.dirname(file_path)
            if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                os.rmdir(temp_dir)
    except:
        pass

class VideoFile:
    """Wrapper for downloaded files to work with Streamlit"""
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.name = os.path.basename(file_path)
        self.type = "video/mp4"
        self.size = os.path.getsize(file_path)
    
    def getvalue(self):
        with open(self.file_path, 'rb') as f:
            return f.read()

def send_video_to_api(video_file) -> Optional[dict]:
    """Send video file to deepfake detection API"""
    try:
        files = {
            'file': (video_file.name, video_file.getvalue(), video_file.type)
        }
        
        response = requests.post(
            f"{API_ENDPOINT}/detect",
            files=files,
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Service Error: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the detection service. Please try again later.")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again with a smaller video.")
        return None
    except Exception as e:
        st.error("An error occurred while processing your video.")
        return None

def process_predictions(predictions: List[float]) -> pd.DataFrame:
    """Process prediction probabilities into a formatted DataFrame"""
    data = []
    for idx, prob in enumerate(predictions):
        label_name = LABEL_MAP.get(idx, f"UNKNOWN_{idx}")
        probability_percent = prob * 100
        data.append({
            "Label Name": label_name,
            "Probability (%)": probability_percent
        })
    
    df = pd.DataFrame(data)
    df = df.sort_values("Probability (%)", ascending=False)
    df = df.reset_index(drop=True)
    return df

def create_probability_chart(df: pd.DataFrame):
    """Create a horizontal bar chart for probabilities"""
    top_df = df.head(10)
    
    fig = px.bar(
        top_df,
        x="Probability (%)",
        y="Label Name",
        orientation='h',
        title="Top 10 Detection Probabilities",
        color="Probability (%)",
        color_continuous_scale="Viridis"
    )
    
    fig.update_layout(
        height=500,
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False
    )
    
    return fig

def main():
    """Main Streamlit application"""
    
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            text-align: center;
            color: #1f77b4;
            margin-bottom: 2rem;
        }
        .subtitle {
            text-align: center;
            color: #666;
            font-size: 1.1em;
            margin-bottom: 2rem;
        }
        .stButton > button {
            width: 100%;
            background-color: #1f77b4;
            color: white;
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown('<h1 class="main-header">🎭 Deepfake Detection System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Upload a video file or paste an Instagram link to check for AI-generated content</p>', unsafe_allow_html=True)
    
    # Create columns for layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Upload section with tabs
        st.markdown("### 📁 Choose Video Source")
        st.markdown("Select how you want to provide the video for analysis")
        
        tab1, tab2 = st.tabs(["📁 Upload File", "📱 Instagram Link"])
        
        uploaded_file = None
        instagram_url = None
        
        with tab1:
            st.markdown("Select a video file from your device")
            uploaded_file = st.file_uploader(
                "Choose a video file",
                type=['mp4', 'avi', 'mov', 'mkv'],
                help="Supported formats: MP4, AVI, MOV, MKV"
            )
        
        with tab2:
            st.markdown("Paste an Instagram post URL - video will be automatically downloaded and analyzed")
            instagram_url = st.text_input(
                "Instagram URL",
                placeholder="https://www.instagram.com/p/ABC123...",
                help="Paste the URL of an Instagram post, reel, or IGTV video"
            )
            
            if instagram_url and not is_valid_instagram_url(instagram_url):
                st.error("❌ Please enter a valid Instagram URL")
        
        # Check what input we have
        has_file_upload = uploaded_file is not None
        has_instagram_url = instagram_url and is_valid_instagram_url(instagram_url)
        
        # Process button
        process_button = st.button("🔍 Analyze Video", type="primary")
        
        # Display preview for uploaded files only
        if uploaded_file is not None:
            st.markdown("### 📹 Video Preview")
            st.video(uploaded_file)
            
            file_details = {
                "Source": "Uploaded File",
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / (1024*1024):.2f} MB",
                "File type": uploaded_file.type
            }
            
            st.markdown("**File Details:**")
            for key, value in file_details.items():
                st.text(f"{key}: {value}")
        
        elif instagram_url and is_valid_instagram_url(instagram_url):
            st.markdown("### 📱 Instagram Video Ready")
            st.info(f"Ready to analyze Instagram video: {instagram_url}")
        
        # Process the video when button is clicked
        if process_button:
            if not has_file_upload and not has_instagram_url:
                st.error("Please upload a video file or provide a valid Instagram URL first!")
            else:
                # Check if API endpoint is configured
                if API_ENDPOINT == "https://your-ngrok-url.ngrok.io":
                    st.error("⚠️ Service temporarily unavailable. Please try again later.")
                    st.info("💡 If you're the developer, update the API_ENDPOINT in config.py")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    temp_file_path = None
                    
                    try:
                        video_to_process = None
                        
                        # Handle Instagram URL - download automatically
                        if has_instagram_url:
                            status_text.text("📱 Downloading video from Instagram...")
                            progress_bar.progress(20)
                            
                            downloaded_path = download_instagram_video(instagram_url)
                            if downloaded_path:
                                video_to_process = VideoFile(downloaded_path)
                                temp_file_path = downloaded_path
                                status_text.text("✅ Instagram video downloaded!")
                                progress_bar.progress(40)
                            else:
                                progress_bar.empty()
                                status_text.empty()
                                st.error("❌ Failed to download Instagram video. The post might be private or the URL is incorrect.")
                                return
                        else:
                            # Use uploaded file
                            video_to_process = uploaded_file
                            progress_bar.progress(40)
                        
                        status_text.text("📤 Sending video for analysis...")
                        progress_bar.progress(60)
                        
                        # Send video to API
                        api_response = send_video_to_api(video_to_process)
                        progress_bar.progress(80)
                        
                        if api_response is not None:
                            status_text.text("🔄 Processing results...")
                            progress_bar.progress(90)
                            
                            predictions = api_response.get('predictions', [])
                            
                            if len(predictions) == 17:
                                df = process_predictions(predictions)
                                
                                progress_bar.progress(100)
                                status_text.text("✅ Analysis complete!")
                                time.sleep(1)
                                
                                progress_bar.empty()
                                status_text.empty()
                                
                                st.markdown("---")
                                st.markdown("### 📊 Detection Results")
                                
                                # Show top prediction
                                top_prediction = df.iloc[0]
                                confidence = top_prediction["Probability (%)"]
                                
                                if confidence > HIGH_CONFIDENCE_THRESHOLD:
                                    st.error(f"🚨 High confidence AI-generated content detected!")
                                elif confidence > MEDIUM_CONFIDENCE_THRESHOLD:
                                    st.warning(f"⚠️ Possible AI-generated content detected.")
                                else:
                                    st.success(f"✅ Low probability of AI-generated content.")
                                
                                st.markdown(f"**Most likely classification:** {top_prediction['Label Name']} ({confidence:.2f}%)")
                                
                                # Create tabs for different views
                                tab1, tab2, tab3 = st.tabs(["📋 Table View", "📈 Chart View", "📊 Summary"])
                                
                                with tab1:
                                    st.markdown("#### Detailed Predictions")
                                    display_df = df.copy()
                                    display_df["Probability (%)"] = display_df["Probability (%)"].apply(lambda x: f"{x:.2f}%")
                                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                                
                                with tab2:
                                    st.markdown("#### Probability Visualization")
                                    chart = create_probability_chart(df)
                                    st.plotly_chart(chart, use_container_width=True)
                                
                                with tab3:
                                    st.markdown("#### Summary Statistics")
                                    col_a, col_b = st.columns(2)
                                    
                                    with col_a:
                                        st.metric("Highest Probability", f"{df.iloc[0]['Probability (%)']:.2f}%")
                                        st.metric("Average Probability", f"{df['Probability (%)'].mean():.2f}%")
                                    
                                    with col_b:
                                        st.metric("Lowest Probability", f"{df.iloc[-1]['Probability (%)']:.2f}%")
                                        predictions_above_10 = len(df[df['Probability (%)'] > 10])
                                        st.metric("Predictions > 10%", predictions_above_10)
                                
                                # Download results
                                st.markdown("---")
                                csv = df.to_csv(index=False)
                                
                                # Generate filename
                                if has_instagram_url:
                                    filename = f"instagram_analysis_{int(time.time())}.csv"
                                else:
                                    filename = f"video_analysis_{uploaded_file.name}_{int(time.time())}.csv"
                                
                                st.download_button(
                                    label="📥 Download Results as CSV",
                                    data=csv,
                                    file_name=filename,
                                    mime="text/csv"
                                )
                                
                            else:
                                progress_bar.empty()
                                status_text.empty()
                                st.error(f"Invalid service response: Expected 17 predictions, got {len(predictions)}")
                        else:
                            progress_bar.empty()
                            status_text.empty()
                            st.error("Failed to analyze the video. Please try again.")
                    
                    except Exception as e:
                        progress_bar.empty()
                        status_text.empty()
                        st.error("An unexpected error occurred while processing your video.")
                    
                    finally:
                        # Clean up temporary Instagram files
                        if temp_file_path:
                            cleanup_temp_files(temp_file_path)

    # Sidebar with information
    with st.sidebar:
        st.markdown("### ℹ️ About")
        st.markdown("""
        This AI detection system analyzes videos to identify AI-generated or deepfake content.
        
        **How it works:**
        1. Upload a video file OR paste an Instagram link
        2. Our AI analyzes the content automatically
        3. Get detailed predictions across 17 AI categories
        """)
        
        st.markdown("### 📱 Supported Sources")
        st.markdown("""
        - **Local files**: MP4, AVI, MOV, MKV
        - **Instagram**: Posts, Reels, IGTV (public videos only)
        """)
        
        st.markdown("### 🎯 Detection Categories")
        st.markdown("The system can identify:")
        
        # Group labels by category
        ai_tools = ["MIDJOURNEY", "CHATGPT", "SORA", "RUNWAY", "PIKA"]
        video_tools = ["KLING", "HAILUO", "VEO", "HUNYUAN", "VIDU"]
        anime_game = ["ANIME_1D", "ANIME_2D", "VIDEO_GAME"]
        other_tools = ["AI_GEN", "HIGGSFIELD", "WAN", "RAY"]
        
        with st.expander("🎨 AI Art Tools"):
            for label in ai_tools:
                st.text(f"• {label}")
        
        with st.expander("🎬 Video Generation"):
            for label in video_tools:
                st.text(f"• {label}")
                    
        with st.expander("🎮 Animation & Games"):
            for label in anime_game:
                st.text(f"• {label}")
                    
        with st.expander("🤖 Other AI Tools"):
            for label in other_tools:
                st.text(f"• {label}")
        
        st.markdown("---")
        st.markdown("### 🔒 Privacy")
        st.markdown("""
        - Videos are processed securely
        - No data is stored permanently
        - Instagram videos are temporarily downloaded and deleted after analysis
        """)

if __name__ == "__main__":
    main()
