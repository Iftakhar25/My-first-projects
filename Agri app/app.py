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
    "Upload an Image of a Diseased Plant (JPEG, PNG)",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    st.success("Image successfully uploaded. Now select an action below.")
    
    # Initialize the image object for API call
    image_for_api = image

    # Create a container for the buttons
    st.subheader("Select an Action:")
    col1, col2 = st.columns(2)

    # --- Button 1: Find Disease ---
    with col1:
        if st.button("🔬 1. Find Disease & Symptoms", use_container_width=True):
            with st.spinner("Analyzing image for disease recognition..."):
                # Specific Prompt for Disease Finding
                disease_prompt = (
                    "Analyze the uploaded agricultural image. First, identify the crop (if possible) and the visual symptoms shown. "
                    "Then, based on the symptoms, identify the most likely plant disease/issue. "
                    "Explain the disease briefly, listing the key symptoms visible in the photo. "
                    "Format the output clearly under the headings: 'Crop Identification', 'Likely Disease', and 'Visible Symptoms'."
                )
                
                result = generate_response(disease_prompt, image_for_api)
                
                if result:
                    st.session_state['disease_result'] = result
                    st.session_state['active_tab'] = 'disease'

    # --- Button 2: Suggestions & Advise ---
    with col2:
        if st.button("🧑‍🌾 2. Management & Advice", use_container_width=True):
            with st.spinner("Generating practical advice and management strategies..."):
                # Specific Prompt for Advice
                advice_prompt = (
                    "Based on the plant disease visible in the uploaded image, provide practical and actionable suggestions for its management and control. "
                    "Include advice on cultural practices (e.g., fertilization, sanitation, water management), and chemical control (mentioning general classes or active ingredients, NOT specific brand names). "
                    "Provide the response in an easy-to-read, step-by-step list or bullet points."
                )
                
                result = generate_response(advice_prompt, image_for_api)
                
                if result:
                    st.session_state['advice_result'] = result
                    st.session_state['active_tab'] = 'advice'

    # --- Results Display ---
    st.markdown("---")
    
    # Use session state to manage which result to display
    if 'disease_result' in st.session_state and st.session_state.get('active_tab') == 'disease':
        st.subheader("🔬 Disease and Symptom Analysis:")
        st.markdown(st.session_state['disease_result'])
        
    if 'advice_result' in st.session_state and st.session_state.get('active_tab') == 'advice':
        st.subheader("🧑‍🌾 Management Suggestions and Advice:")
        st.markdown(st.session_state['advice_result'])

    # --- Button 3: Custom Prompt ---
    st.subheader("3. Ask a Custom Question")
    custom_prompt = st.text_input(
        "Enter your specific question about the uploaded image:",
        placeholder="e.g., 'What soil deficiency might cause these leaf spots?' or 'Is this photo showing a fungal or bacterial infection?'"
    )

    if st.button("❓ Get Custom Answer", disabled=(not custom_prompt)):
        if custom_prompt:
            with st.spinner(f"Answering your custom question: '{custom_prompt}'..."):
                # Combined Prompt for Custom Question
                full_custom_prompt = (
                    f"Analyze the uploaded agricultural image and answer the following question as precisely as possible. "
                    f"Question: {custom_prompt}"
                )
                
                custom_result = generate_response(full_custom_prompt, image_for_api)
                
                if custom_result:
                    st.subheader("❓ Custom Question Answer:")
                    st.markdown(custom_result)

else:
    # Initial state when no file is uploaded
    st.info("Please upload an image to begin the plant disease analysis.")
