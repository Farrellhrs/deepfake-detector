"""
Test script for deepfake detection API
Run this to verify your API is working before deploying the Streamlit app
"""

import requests
import json
from config import API_ENDPOINT

def test_api_connection():
    """
    Test if the API endpoint is reachable
    """
    try:
        # Test basic connectivity
        response = requests.get(f"{API_ENDPOINT}/", timeout=10)
        print(f"✅ API is reachable at {API_ENDPOINT}")
        print(f"Status code: {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {API_ENDPOINT}")
        print("Make sure your API is running and ngrok tunnel is active")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_detect_endpoint(test_file_path: str | None = None):
    """
    Test the /detect endpoint with a sample file
    
    Args:
        test_file_path: Path to a test video file (optional)
    """
    if not test_file_path:
        print("No test file provided, skipping endpoint test")
        return
        
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{API_ENDPOINT}/detect", files=files, timeout=30)
            
        if response.status_code == 200:
            result = response.json()
            predictions = result.get('predictions', [])
            
            print(f"✅ /detect endpoint working!")
            print(f"Response: {json.dumps(result, indent=2)}")
            print(f"Number of predictions: {len(predictions)}")
            
            if len(predictions) == 17:
                print("✅ Correct number of predictions received")
            else:
                print(f"⚠️ Expected 17 predictions, got {len(predictions)}")
                
        else:
            print(f"❌ API returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except FileNotFoundError:
        print(f"❌ Test file not found: {test_file_path}")
    except Exception as e:
        print(f"❌ Error testing detect endpoint: {str(e)}")

if __name__ == "__main__":
    print("🧪 Deepfake Detection API Test")
    print("=" * 40)
    
    print(f"🔍 Testing connection to: {API_ENDPOINT}")
    
    if API_ENDPOINT == "https://your-ngrok-url.ngrok.io":
        print("❌ API endpoint not configured!")
        print("Please update API_ENDPOINT in config.py with your actual ngrok URL")
        exit(1)
    
    test_api_connection()
    
    print(f"\n🔍 Testing /detect endpoint...")
    test_file_path = input("Enter path to test video file (optional, press Enter to skip): ").strip()
    
    if test_file_path:
        test_detect_endpoint(test_file_path)
    else:
        print("Skipping endpoint test")
    
    print("\n✅ Test completed!")
