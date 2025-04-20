import streamlit as st
import requests
from PIL import Image
from io import BytesIO

st.title("🔭 Telescope Image Enhancer")
st.caption("Upload your raw telescope photo and let AI make it look like a Hubble masterpiece.")

uploaded_file = st.file_uploader("📤 Upload your image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Original Image", use_column_width=True)

    st.write("✨ Enhancing your image with Hugging Face AI...")

    # Send image to Hugging Face model (example: Real-ESRGAN)
    api_url = "https://akhaliq-real-esrgan.hf.space/run/predict"

    files = {
        "data": (uploaded_file.name, uploaded_file, uploaded_file.type)
    }

    response = requests.post(api_url, files=files)

    if response.ok:
        result = response.json()
        enhanced_url = result["data"][0]  # Assumes model returns image URL
        st.image(enhanced_url, caption="Enhanced Image", use_column_width=True)
    else:
        st.error("Something went wrong while enhancing the image. Try again!")
