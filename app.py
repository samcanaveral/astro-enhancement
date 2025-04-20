import streamlit as st
import requests
from PIL import Image
import io
import base64

# ✅ Your Hugging Face Token is inserted
API_TOKEN = "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"
API_URL = "https://api-inference.huggingface.co/models/akhaliq/Real-ESRGAN"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

st.set_page_config(page_title="AstroVision AI", layout="centered")
st.title("🔭 AstroVision AI - Image Enhancer")

st.markdown("Upload your telescope image and enhance it using AI trained on high-res space data.")

uploaded_file = st.file_uploader("📷 Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Original Image", use_column_width=True)

    if st.button("✨ Enhance Image"):
        with st.spinner("Enhancing image... please wait ⏳"):
            image_bytes = io.BytesIO()
            image.save(image_bytes, format="PNG")
            image_bytes = image_bytes.getvalue()

            try:
                response = requests.post(API_URL, headers=headers, data=image_bytes)

                if response.status_code == 200:
                    enhanced_image = Image.open(io.BytesIO(response.content))
                    st.image(enhanced_image, caption="Enhanced Image", use_column_width=True)

                    # ✅ Download button
                    buf = io.BytesIO()
                    enhanced_image.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    b64 = base64.b64encode(byte_im).decode()
                    href = f'<a href="data:file/png;base64,{b64}" download="enhanced.png">📥 Download Enhanced Image</a>'
                    st.markdown(href, unsafe_allow_html=True)
                else:
                    st.error("❌ Enhancement failed. Try again later.")
                    st.text(f"Status Code: {response.status_code}")
                    st.text(response.text)

            except Exception as e:
                st.error("🚨 An error occurred during enhancement.")
                st.text(str(e))
