@echo off
echo Starting Deepfake Detection Web App...
echo.

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Streamlit not found. Installing requirements...
    pip install -r requirements.txt
)

echo.
echo Opening Streamlit app...
echo Press Ctrl+C to stop the application
echo.

streamlit run app.py
