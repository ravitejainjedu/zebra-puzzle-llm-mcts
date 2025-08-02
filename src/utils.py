import os
from dotenv import load_dotenv
import google.generativeai as genai

def setup_gemini():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("models/gemini-2.0-flash")
