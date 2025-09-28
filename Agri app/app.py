# app.py
import os
import io
import base64
import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

# ---------------------------
# Config / Setup
# ---------------------------
st.set_page_config(page_title="AgriDiag — Gemini Plant Disease Assistant", layout="wide")

st.title("AgriDiag — Plant disease detection & advice (Gemini 2.5-Flash)")
st.caption("Upload a clear image of the plant/leaf/stem. Click a button to analyze. (Proof of concept; not a lab diagnosis.)")

# Get API key from environment or Streamlit secrets
GEMINI_KEY = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)
if not GEMINI_KEY:
    st.error("Gemini API key not set. Set GEMINI_API_KEY in environment or in Streamlit secrets.")
    st.stop()

# Initialize Gemini client (google-genai reads GEMINI_API_KEY env var automatically)
client = genai.Client()

# ---------------------------
# Sidebar: upload + options
# ---------------------------
with st.sidebar:
    st.header("Upload image")
    uploaded_file = st.file_uploader("Choose a plant image (leaf, stem, fruit). Recommended: clear, focused photo.", type=["jpg","jpeg","png","webp","heic"])
    st.markdown("---")
    st.markdown("**Image Notes / Tips**\n- Take close-up of the symptomatic area\n- Include overall plant view + close leaf detail if possible\n- Avoid excessive blurring or shadows")
    st.markdown("---")
    st.caption("If your image is > 10–15MB, consider resizing before upload (browser / phone).")

# ---------------------------
# Helper: send image + prompt to Gemini
# ---------------------------
def call_gemini_with_image(image_bytes: bytes, prompt_text: str, thinking_budget: int = 0):
    """
    Send image (inline bytes) and prompt_text to Gemini 2.5-flash.
    Returns: text output from model (string).
    """
    try:
        # Build parts: image part + text part
        img_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
        # The prompt text should come after the image part per best practice
        contents = [img_part, prompt_text]

        # Optionally you can set thinking_budget>0 to enable model "thinking"
        cfg = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=thinking_budget)
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=cfg
        )
        return response.text
    except Exception as e:
        return f"Error calling Gemini API: {e}"

# ---------------------------
# UI: Show uploaded image
# ---------------------------
if uploaded_file:
    try:
        image = Image.open(uploaded_file)
    except Exception as e:
        st.error(f"Couldn't open image: {e}")
        st.stop()

    # Display image
    st.image(image, use_column_width=True, caption=f"Uploaded: {uploaded_file.name}")

    # Convert to JPEG bytes (Gemini examples prefer JPEG; ensures consistent mime)
    buf = io.BytesIO()
    rgb = image.convert("RGB")
    rgb.save(buf, format="JPEG", quality=90)
    image_bytes = buf.getvalue()

    # Quick sanity size check
    size_mb = len(image_bytes) / (1024 * 1024)
    if size_mb > 18:
        st.warning(f"Image size {size_mb:.1f} MB — close to the inline limit (~20MB). Consider resizing for reliability.")

    # ---------------------------
    # Prompts for the three buttons
    # ---------------------------

    # 1) Find disease (prebuilt instruction)
    prompt_find_disease = (
        "You are an expert plant pathologist and agronomist. Analyze the supplied image and:\n"
        "1) Name the most likely disease(s) or disorder(s) (be explicit about uncertainty).\n"
        "2) List the visible symptoms you see (e.g., leaf spots, lesions, discoloration, wilting) linked to the image.\n"
        "3) Suggest the most probable causal agent (fungus, bacteria, virus, nutrient deficiency, abiotic stress) and why.\n"
        "4) Provide a short confidence estimate (low/medium/high) and what additional observations or simple tests would increase confidence.\n"
        "Answer concisely in bullet points and prioritize actionable diagnostic clues."
    )

    # 2) Suggestions & advice (prebuilt instruction)
    prompt_suggestions = (
        "You are an experienced crop protection specialist. Based on the supplied image and"
        " likely disease/disorder, provide practical control and management advice in order:\n"
        "A) Immediate short-term actions (isolation, sanitation, removal of affected tissue).\n"
        "B) Cultural and non-chemical solutions (crop rotation, irrigation changes, pruning, resistant varieties).\n"
        "C) If chemical control is recommended: list pesticide types (active ingredient classes), approximate application rates or guidance (give ranges), and safety/environmental precautions.\n"
        "D) Monitoring plan: what to watch for, when to re-check, and when to seek lab confirmation.\n"
        "End with a short list of low-cost confirmatory tests or photos to take for diagnosis."
    )

    # 3) Custom prompt (user-supplied)
    custom_user_prompt = st.text_input("Custom question about this image (use this with 'Ask (custom prompt)')",
                                      placeholder="e.g. 'What lab test should I run to confirm fungal infection?'")

    # Buttons
    st.markdown("### Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔬 Find disease (auto)"):
            with st.spinner("Analyzing image for likely disease..."):
                output = call_gemini_with_image(image_bytes, prompt_find_disease, thinking_budget=500)  # moderate thinking budget
            st.subheader("Likely disease(s) & diagnostic clues")
            st.write(output)

    with col2:
        if st.button("🩺 Suggestions & Advice"):
            with st.spinner("Generating management suggestions and safety advice..."):
                output = call_gemini_with_image(image_bytes, prompt_suggestions, thinking_budget=400)
            st.subheader("Practical suggestions & monitoring plan")
            st.write(output)

    with col3:
        if st.button("❓ Ask (custom prompt)"):
            if not custom_user_prompt.strip():
                st.warning("Please enter a custom prompt in the text box before clicking this button.")
            else:
                combined_prompt = (
                    "You are a helpful plant pathology assistant. Use the image to inform your answer.\n\n"
                    f"User question: {custom_user_prompt}\n\n"
                    "Provide a concise, practical answer and list any assumptions you made."
                )
                with st.spinner("Asking the model about your custom question..."):
                    output = call_gemini_with_image(image_bytes, combined_prompt, thinking_budget=200)
                st.subheader("Model answer to your question")
                st.write(output)

    # Footer: small note
    st.markdown("---")
    st.info("Tip: If output seems uncertain, re-take the photo with closer focus on symptomatic areas and try again. The app is a decision-support tool; confirm important actions with local experts.")

else:
    st.info("Please upload an image to get started. Use the sidebar to upload a close, well-lit photo of the symptomatic plant area.")
