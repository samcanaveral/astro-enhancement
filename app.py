import streamlit as st
import requests
from PIL import Image
import io
import base64

# --- Constants ---
API_URL = "https://api-inference.huggingface.co/models/CompVis/ldm-super-resolution-4x-openimages"  # example model
headers = {"Authorization": f"Bearer YOUR_HUGGINGFACE_TOKEN"}  # replace with your token

st.title("🔭 AstroVision AI - Image Enhancer")

# --- Upload Section ---
uploaded_file = st.file_uploader("Upload a telescope image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Original Image", use_column_width=True)

    if st.button("✨ Enhance Image"):
        with st.spinner("Enhancing with Hugging Face AI..."):

            image_bytes = uploaded_file.read()
            response = requests.post(API_URL, headers=headers, data=image_bytes)

            try:
                # Try to decode image from response
                if response.status_code == 200 and response.headers["content-type"].startswith("image/"):
                    enhanced_image = Image.open(io.BytesIO(response.content))
                    st.image(enhanced_image, caption="Enhanced Image", use_column_width=True)

                    # Download button
                    buffered = io.BytesIO()
                    enhanced_image.save(buffered, format="PNG")
                    b64 = base64.b64encode(buffered.getvalue()).decode()
                    href = f'<a href="data:file/png;base64,{b64}" download="enhanced.png">📥 Download Enhanced Image</a>'
                    st.markdown(href, unsafe_allow_html=True)

                    # Simulated object detection output
                    st.subheader("🔎 Detected Objects (Simulated)")
                    st.write("🪐 Example: 'Galaxy core', 'Gas cloud', 'Crater ring'")

                else:
                    st.error("❌ Enhancement failed. The model may be sleeping or returned an invalid response.")
                    st.text(f"Status code: {response.status_code}")
                    st.text(response.text)

            except Exception as e:
                st.error("🚨 Something went wrong while enhancing the image!")
                st.text(str(e))

     
