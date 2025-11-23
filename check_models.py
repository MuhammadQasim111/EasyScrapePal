import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load .env from D:\webscraper_project\project\.env
current_dir = os.path.dirname(os.path.abspath(__file__))
# We need to point to the D: drive location if we are running this from C: but the file is intended for D:
# However, let's just assume we run this script and it tries to find .env in the same dir.
# If I write this to C:\Users\hp\Desktop\webscraper\project\check_models.py, I should copy it to D: first or just read the .env from D: directly.

env_path = r"D:\webscraper_project\project\.env"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("API Key not found!")
else:
    genai.configure(api_key=api_key)
    print("Listing available models...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"Error: {e}")
