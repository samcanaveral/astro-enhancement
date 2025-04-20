import streamlit as st
import requests
from PIL import Image
import base64
from io import BytesIO

st.set_page_config(page_title="Telescope Image Enhancer", layout="centered")

st.title("🔭 AstroVision AI: Enhance Your Telescope Images")
uploaded_file = st.file_uploader("Upload your raw telescope image (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Show original image
    image = Image.open(uploaded_file)
    st.image(image, caption="Original Image", use_column_width=True)

    # Convert image to bytes
    image_bytes = uploaded_file.read()

    # Hugging Face API Endpoint
    api_url = "https://akhaliq-Real-ESRGAN.hf.space/run/predict"
    files = {"data": ("image.jpg", image_bytes, "image/jpeg")}

    with st.spinner("✨ Enhancing your image with AI..."):
        try:
            response = requests.post(api_url, files=files)
            result = response.json()

            # Parse base64 string (check model returns correctly)
            enhanced_base64 = result["data"][0].split(",")[-1]
            enhanced_image = Image.open(BytesIO(base64.b64decode(enhanced_base64)))

            st.success("✅ Image enhanced successfully!")
            st.image(enhanced_image, caption="Enhanced Image", use_column_width=True)
        except Exception as e:
            st.error("❌ Enhancement failed. Try again with a different image or check the model.")
            st.exception(e)


