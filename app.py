import streamlit as st
import requests
from PIL import Image
import io
import base64

st.set_page_config(page_title="AstroVision AI", layout="centered")
st.title("🔭 AstroVision AI - Image Enhancer")

st.markdown("Upload your telescope image and enhance it using AI trained on high-res space data.")

uploaded_file = st.file_uploader("📷 Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Original Image", use_column_width=True)

    if st.button("✨ Enhance Image"):
        with st.spinner("Enhancing image... please wait ⏳"):
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            buffered.seek(0)

            files = {
                'file': ('image.png', buffered, 'image/png')
            }

            response = requests.post(
                "https://akhaliq-real-esrgan.hf.space/run/predict",
                files=files
            )

            if response.status_code == 200:
                result = response.json()
                if 'data' in result and len(result['data']) > 0:
                    enhanced_image_url = result['data'][0]
                    enhanced_response = requests.get(enhanced_image_url)
                    if enhanced_response.status_code == 200:
                        enhanced_image = Image.open(io.BytesIO(enhanced_response.content))
                        st.image(enhanced_image, caption="Enhanced Image", use_column_width=True)

                        # Download button
                        buf = io.BytesIO()
                        enhanced_image.save(buf, format="PNG")
                        byte_im = buf.getvalue()
                        b64 = base64.b64encode(byte_im).decode()
                        href = f'<a href="data:file/png;base64,{b64}" download="enhanced.png">📥 Download Enhanced Image</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    else:
                        st.error("Failed to retrieve the enhanced image.")
                else:
                    st.error("Enhancement failed. No data returned.")
            else:
                st.error(f"Enhancement failed with status code {response.status_code}.")
