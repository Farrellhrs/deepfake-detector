# Deployment Guide for Deepfake Detection App

## Quick Start for Developers

### 1. Update Configuration
Edit `config.py` and replace the placeholder URL:

```python
API_ENDPOINT = "https://your-actual-ngrok-url.ngrok.io"  # Your real ngrok URL here
```

### 2. Test the Setup
```bash
python test_api.py
```

### 3. Run the App
```bash
streamlit run app.py
```

### 4. Access the App
- Local: http://localhost:8501
- Network: Your computer's IP + :8501

## For Public Deployment

### Option 1: Streamlit Cloud
1. Push your code to GitHub
2. Go to https://share.streamlit.io/
3. Connect your repo
4. Deploy automatically

### Option 2: Heroku
1. Create `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```
2. Deploy to Heroku

### Option 3: Docker
```bash
docker build -t deepfake-detector .
docker run -p 8501:8501 deepfake-detector
```

## Environment Variables (Optional)

You can also use environment variables instead of editing config.py:

```bash
export API_ENDPOINT="https://your-ngrok-url.ngrok.io"
streamlit run app.py
```

## Security Notes for Production

- Use HTTPS endpoints only
- Implement rate limiting
- Add input validation
- Consider file size limits
- Add authentication if needed

## Troubleshooting

### Common Issues:

1. **"Service temporarily unavailable"**
   - Check that API_ENDPOINT is updated in config.py
   - Verify your API is running

2. **Connection errors**
   - Check ngrok tunnel is active
   - Verify API endpoint URL is correct

3. **Invalid predictions**
   - Ensure API returns exactly 17 probability values
   - Check API response format
