import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import io
import os
from typing import Optional, List, Tuple
import time
import json
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

def send_video_to_api(video_file) -> Optional[dict]:
    """
    Send video file to deepfake detection API
    
    Args:
        video_file: Uploaded video file from Streamlit
        
    Returns:
        API response as dictionary or None if error
    """
    try:
        # Prepare the file for upload
        files = {
            'file': (video_file.name, video_file.getvalue(), video_file.type)
        }
        
        # Make API request
        response = requests.post(
            f"{API_ENDPOINT}/detect",
            files=files,
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Service Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the detection service. Please try again later.")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. The video might be too large or the service is busy.")
        return None
    except Exception as e:
        st.error(f"Unexpected error occurred while processing your video.")
        return None

def process_predictions(predictions: List[float]) -> pd.DataFrame:
    """
    Process prediction probabilities into a formatted DataFrame
    
    Args:
        predictions: List of 17 probabilities (0-1) for each label
        
    Returns:
        DataFrame with Label Name and Probability columns, sorted by probability
    """
    # Create DataFrame
    data = []
    for idx, prob in enumerate(predictions):
        label_name = LABEL_MAP.get(idx, f"UNKNOWN_{idx}")
        probability_percent = prob * 100
        data.append({
            "Label Name": label_name,
            "Probability (%)": probability_percent
        })
    
    df = pd.DataFrame(data)
    # Sort by probability in descending order
    df = df.sort_values("Probability (%)", ascending=False)
    df = df.reset_index(drop=True)
    
    return df

def create_probability_chart(df: pd.DataFrame):
    """
    Create a horizontal bar chart for probabilities
    
    Args:
        df: DataFrame with Label Name and Probability columns
        
    Returns:
        Plotly bar chart
    """
    # Take top 10 for better visualization
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
    
    # Page configuration
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for centered layout and styling
    st.markdown("""
        <style>
        .main-header {
            text-align: center;
            color: #1f77b4;
            margin-bottom: 2rem;
        }
        .upload-section {
            background-color: #f0f2f6;
            padding: 2rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        .results-section {
            margin-top: 2rem;
        }
        .stButton > button {
            width: 100%;
            background-color: #1f77b4;
            color: white;
            border-radius: 5px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            font-size: 1.1em;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown('<h1 class="main-header">🎭 Deepfake Detection System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Upload a video to check if it contains AI-generated or deepfake content</p>', unsafe_allow_html=True)
    
    # Create two columns for layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Upload section
        st.markdown("### 📁 Upload Video")
        st.markdown("Select a video file to analyze for deepfake content")
        
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=['mp4', 'avi', 'mov', 'mkv'],
            help="Supported formats: MP4, AVI, MOV, MKV"
        )
        
        # Process button
        process_button = st.button("🔍 Analyze Video", type="primary")
        
        # Display uploaded video
        if uploaded_file is not None:
            st.markdown("### 📹 Uploaded Video")
            st.video(uploaded_file)
            
            # Show file details
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / (1024*1024):.2f} MB",
                "File type": uploaded_file.type
            }
            
            st.markdown("**File Details:**")
            for key, value in file_details.items():
                st.text(f"{key}: {value}")
        
        # Process the video when button is clicked
        if process_button:
            if uploaded_file is None:
                st.error("Please upload a video file first!")
            else:
                # Check if API endpoint is configured
                if API_ENDPOINT == "https://your-ngrok-url.ngrok.io":
                    st.error("⚠️ Service temporarily unavailable. Please try again later.")
                    st.info("💡 If you're the developer, update the API_ENDPOINT in config.py")
                else:
                    # Create a progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        status_text.text("📤 Uploading video to detection service...")
                        progress_bar.progress(25)
                        
                        # Send video to API
                        api_response = send_video_to_api(uploaded_file)
                        progress_bar.progress(75)
                        
                        if api_response is not None:
                            status_text.text("🔄 Processing results...")
                            progress_bar.progress(90)
                            
                            # Extract predictions from response
                            predictions = api_response.get('predictions', [])
                            
                            if len(predictions) == 17:
                                # Process predictions
                                df = process_predictions(predictions)
                                
                                progress_bar.progress(100)
                                status_text.text("✅ Analysis complete!")
                                time.sleep(1)  # Brief pause to show completion
                                
                                # Clear progress indicators
                                progress_bar.empty()
                                status_text.empty()
                                
                                st.markdown("---")
                                st.markdown("### 📊 Detection Results")
                                
                                # Show top prediction
                                top_prediction = df.iloc[0]
                                confidence = top_prediction["Probability (%)"]
                                
                                if confidence > HIGH_CONFIDENCE_THRESHOLD:
                                    alert_type = "error"
                                    emoji = "🚨"
                                    message = "High confidence AI-generated content detected!"
                                elif confidence > MEDIUM_CONFIDENCE_THRESHOLD:
                                    alert_type = "warning" 
                                    emoji = "⚠️"
                                    message = "Possible AI-generated content detected."
                                else:
                                    alert_type = "success"
                                    emoji = "✅"
                                    message = "Low probability of AI-generated content."
                                
                                if alert_type == "error":
                                    st.error(f"{emoji} {message}")
                                elif alert_type == "warning":
                                    st.warning(f"{emoji} {message}")
                                else:
                                    st.success(f"{emoji} {message}")
                                
                                st.markdown(f"**Most likely classification:** {top_prediction['Label Name']} ({confidence:.2f}%)")
                                
                                # Create tabs for different views
                                tab1, tab2, tab3 = st.tabs(["📋 Table View", "📈 Chart View", "📊 Summary Stats"])
                                
                                with tab1:
                                    st.markdown("#### Detailed Predictions")
                                    
                                    # Format the DataFrame for better display
                                    display_df = df.copy()
                                    display_df["Probability (%)"] = display_df["Probability (%)"].apply(lambda x: f"{x:.2f}%")
                                    
                                    st.dataframe(
                                        display_df,
                                        use_container_width=True,
                                        hide_index=True
                                    )
                                
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
                                
                                # Download results option
                                st.markdown("---")
                                csv = df.to_csv(index=False)
                                st.download_button(
                                    label="📥 Download Results as CSV",
                                    data=csv,
                                    file_name=f"detection_results_{uploaded_file.name}_{int(time.time())}.csv",
                                    mime="text/csv"
                                )
                                
                            else:
                                progress_bar.empty()
                                status_text.empty()
                                st.error(f"Invalid service response: Expected 17 predictions, got {len(predictions)}")
                                
                                # Show debug information for developers only
                                if st.checkbox("🔍 Show debug information (developers only)"):
                                    st.json(api_response)
                        else:
                            progress_bar.empty()
                            status_text.empty()
                            st.error("Failed to analyze the video. Please try again.")
                    
                    except Exception as e:
                        progress_bar.empty()
                        status_text.empty()
                        st.error(f"An unexpected error occurred while processing your video.")
                        
                        # Show error details for developers only
                        if st.checkbox("🔍 Show error details (developers only)"):
                            st.text(str(e))

    # Sidebar with information
    with st.sidebar:
        st.markdown("### ℹ️ About")
        st.markdown("""
        This AI detection system analyzes uploaded videos to identify if they contain artificially generated or deepfake content.
        
        **How it works:**
        1. Upload your video file
        2. Our AI analyzes the content
        3. Get detailed predictions across 17 AI categories
        """)
        
        st.markdown("### 🎯 Detection Categories")
        st.markdown("The system can identify:")
        
        # Group labels by category for better display
        ai_tools = ["MIDJOURNEY", "CHATGPT", "SORA", "RUNWAY", "PIKA"]
        video_tools = ["KLING", "HAILUO", "VEO", "HUNYUAN", "VIDU"]
        anime_game = ["ANIME_1D", "ANIME_2D", "VIDEO_GAME"]
        other_tools = ["AI_GEN", "HIGGSFIELD", "WAN", "RAY"]
        
        with st.expander("🎨 AI Art Tools"):
            for label in ai_tools:
                if label in LABEL_MAP.values():
                    st.text(f"• {label}")
        
        with st.expander("🎬 Video Generation"):
            for label in video_tools:
                if label in LABEL_MAP.values():
                    st.text(f"• {label}")
                    
        with st.expander("🎮 Animation & Games"):
            for label in anime_game:
                if label in LABEL_MAP.values():
                    st.text(f"• {label}")
                    
        with st.expander("🤖 Other AI Tools"):
            for label in other_tools:
                if label in LABEL_MAP.values():
                    st.text(f"• {label}")
        
        st.markdown("---")
        st.markdown("### 🔒 Privacy")
        st.markdown("""
        - Videos are processed securely
        - No data is stored permanently
        - Analysis is performed in real-time
        """)

if __name__ == "__main__":
    main()
