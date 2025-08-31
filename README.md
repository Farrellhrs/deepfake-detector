# Deepfake Detection Web App

A user-friendly Streamlit web application for detecting AI-generated and deepfake content in uploaded videos.

## 🎯 For Users

### How to Use the App

1. **Upload Video**: Click "Choose a video file" and select your video
2. **Analyze**: Click "Analyze Video" to start the detection process
3. **View Results**: See if your video contains AI-generated content
4. **Download Results**: Optionally save the analysis as a CSV file

### Supported Formats
- MP4, AVI, MOV, MKV

### What It Detects
The system can identify 17 different types of AI-generated content including:
- Popular AI video tools (Sora, Runway, Pika, etc.)
- AI art generators (Midjourney, ChatGPT, etc.)
- Animation and game content
- Other AI-generated media

---

## 🛠 For Developers

### Setup Instructions

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Configure API Endpoint

Update the `API_ENDPOINT` in `config.py` with your actual ngrok URL:

```python
API_ENDPOINT = "https://your-actual-ngrok-url.ngrok.io"
```

#### 3. Start Your Deepfake Detection API

Make sure your deepfake detection API is running and accessible via ngrok.

#### 4. Run the Streamlit App

```bash
streamlit run app.py
```

Or use the provided batch file on Windows:
```bash
run_app.bat
```

### Testing

Use the test script to verify your API connection:

```bash
python test_api.py
```

### Deployment Checklist

Before deploying for public use:

1. ✅ Update `API_ENDPOINT` in `config.py`
2. ✅ Test API connection with `test_api.py`
3. ✅ Test video upload and detection
4. ✅ Deploy Streamlit app

### Docker Deployment

```bash
# Build the image
docker build -t deepfake-detector .

# Run the container
docker run -p 8501:8501 deepfake-detector
```

## Label Categories

The system detects the following 17 categories:

| Index | Label Name |
|-------|------------|
| 0 | AI_GEN |
| 1 | ANIME_1D |
| 2 | ANIME_2D |
| 3 | VIDEO_GAME |
| 4 | KLING |
| 5 | HIGGSFIELD |
| 6 | WAN |
| 7 | MIDJOURNEY |
| 8 | HAILUO |
| 9 | RAY |
| 10 | VEO |
| 11 | RUNWAY |
| 12 | SORA |
| 13 | CHATGPT |
| 14 | PIKA |
| 15 | HUNYUAN |
| 16 | VIDU |

## Troubleshooting

- **Connection Error**: Verify ngrok URL and API status
- **Timeout Error**: Check video file size and API performance
- **Invalid Predictions**: Ensure API returns exactly 17 probability values
- **File Upload Issues**: Verify video format is supported

## Development

To modify or extend the application:

1. **Add new labels**: Update `LABEL_MAP` dictionary
2. **Change styling**: Modify CSS in the `st.markdown()` calls
3. **Add features**: Extend the main function with new Streamlit components
4. **API modifications**: Update `send_video_to_api()` function
