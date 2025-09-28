import streamlit as st
import google.generativeai as genai
from google.generativeai.errors import APIError
from PIL import Image
import io

# --- Configuration ---
st.set_page_config(
    page_title="Generative AI Plant Doctor (Gemini 2.5 Flash)",
    layout="wide"
)

# --- Initialize Gemini Client ---
try:
    # Use st.secrets to securely retrieve the API key
    if "gemini" in st.secrets and "api_key" in st.secrets["gemini"]:
        api_key = st.secrets["gemini"]["api_key"]
    else:
        st.error("Gemini API key not found in .streamlit/secrets.toml. Please configure it.")
        st.stop()

    client = genai.Client(api_key=api_key)
    MODEL = "gemini-2.5-flash"
except Exception as e:
    st.error(f"Error initializing Gemini client: {e}")
    st.stop()

# --- Gemini API Call Function ---
def generate_response(prompt_text, image_obj):
    """Calls the Gemini API with a text prompt and an image."""
    try:
        # The content array holds both text and image parts
        contents = [image_obj, prompt_text]
        
        response = client.models.generate_content(
            model=MODEL,
            contents=contents
        )
        return response.text
    except APIError as e:
        st.error(f"Gemini API Error: Could not generate content. {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# --- Streamlit UI ---

st.title("🌱 AI Plant Disease Analyzer (Powered by Gemini)")
st.caption("Upload an agricultural image to analyze plant disease symptoms and get management advice.")

# --- Image Upload Section ---
uploaded_file = st.file_uploader(
    "Upload an Image of a Diseased Plant (JP
import streamlit as st
import google.generativeai as genai
from google.generativeai.errors import APIError
from PIL import Image
import io

# --- Configuration ---
st.set_page_config(
    page_title="Generative AI Plant Doctor (Gemini 2.5 Flash)",
    layout="wide"
)

# --- Initialize Gemini Client ---
try:
    # Use st.secrets to securely retrieve the API key
    if "gemini" in st.secrets and "api_key" in st.secrets["gemini"]:
        api_key = st.secrets["gemini"]["api_key"]
    else:
        st.error("Gemini API key not found in .streamlit/secrets.toml. Please configure it.")
        st.stop()

    client = genai.Client(api_key=api_key)
    MODEL = "gemini-2.5-flash"
except Exception as e:
    st.error(f"Error initializing Gemini client: {e}")
    st.stop()

# --- Gemini API Call Function ---
def generate_response(prompt_text, image_obj):
    """Calls the Gemini API with a text prompt and an image."""
    try:
        # The content array holds both text and image parts
        contents = [image_obj, prompt_text]
        
        response = client.models.generate_content(
            model=MODEL,
            contents=contents
        )
        return response.text
    except APIError as e:
        st.error(f"Gemini API Error: Could not generate content. {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# --- Streamlit UI ---

st.title("🌱 AI Plant Disease Analyzer (Powered by Gemini)")
st.caption("Upload an agricultural image to analyze plant disease symptoms and get management advice.")

# --- Image Upload Section ---
uploaded_file = st.file_uploader(
    "Upload an Image of a Diseased Plant (JP
