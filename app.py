import streamlit as st
import requests
from PIL import Image
import base64
from io import BytesIO

st.set_page_config(page_title="AstroVision AI", layout="centered")
st.title("🔭 AstroVision AI: Telescope Image Enhancer")

# Upload image
uploaded_file = st.file_uploader("Upload your telescope image (JPG or PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Show uploaded image
    st.image(uploaded_file, caption="🔍 Original Image", use_column_width=True)

    # Read image
    image = Image.open(uploaded_file)
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    image_bytes = buffered.getvalue()

    # Prepare request to Hugging Face Space
    api_url = "https://akhaliq-Real-ESRGAN.hf.space/run/predict"
    files = {"data": ("image.jpg", image_bytes, "image/jpeg")}

    with st.spinner("🚀 Enhancing your image..."):
        try:
            response = requests.post(api_url, files=files)
            result = response.json()

            # Decode base64 image
            enhanced_base64 = result["data"][0].split(",")[-1]
            enhanced_bytes = base64.b64decode(enhanced_base64)
            enhanced_image = Image.open(BytesIO(enhanced_bytes))

            st.success("✅ Enhancement complete!")
            st.image(enhanced_image, caption="✨ Enhanced Image", use_column_width=True)

            # Download button
            buffered = BytesIO()
            enhanced_image.save(buffered, format="JPEG")
            st.download_button("⬇️ Download Enhanced Image", data=buffered.getvalue(), file_name="enhanced_image.jpg", mime="image/jpeg")

            # Placeholder for object detection
            st.subheader("🔎 Object Detection (Coming Soon)")
            st.info("We'll identify stars, planets, and galaxies in your image in the next release!")

        except Exception as e:
            st.error("⚠️ Enhancement failed. Check the image or model status.")
            st.exception(e)
else:
    st.write("⬆️ Upload an image to get started.")


