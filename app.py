import streamlit as st
import requests
from PIL import Image
import io
import base64
import time

# 🔐 Replace with your Replicate API Token
REPLICATE_TOKEN = "r8_XTelSOe16FTpiFXMGo9fMEfp9cmjXWe2KJBt0"


# Upload section
st.title("🔭 AstroVision AI")
st.markdown("Upload a telescope image (or face) and enhance it using AI.")

uploaded_file = st.file_uploader("📷 Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Original Image", use_column_width=True)

    if st.button("✨ Enhance with CodeFormer"):
        with st.spinner("Enhancing..."):

            # Upload to https://api.imgbb.com/1/upload or other image host
            imgbb_api_key = "0851f77a6130985f037b0c3e4afceeb5"

            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            upload = requests.post(
                "https://api.imgbb.com/1/upload",
                params={"key": imgbb_api_key},
                files={"image": img_bytes}
            )

            if upload.status_code != 200:
                st.error("Image upload failed.")
                st.stop()

            image_url = upload.json()["data"]["url"]

            # Set up Replicate payload
            headers = {"Authorization": f"Token {REPLICATE_TOKEN}"}
            payload = {
                "version": "f9bc7a86c3cf8caa8f0fbb89e4b73463a3deca9201c70525085a05230e4e1693",
                "input": {
                    "image": image_url,
                    "face_upsample": True,
                    "codeformer_fidelity": 0.7
                }
            }

            # Call Replicate
            response = requests.post(
                "https://api.replicate.com/v1/predictions",
                headers=headers,
                json=payload
            )

            if response.status_code != 201:
                st.error("Replicate call failed.")
                st.stop()

            prediction_url = response.json()["urls"]["get"]

            # Wait for result
            while True:
                result = requests.get(prediction_url, headers=headers).json()
                if result["status"] == "succeeded":
                    output_url = result["output"][0]
                    break
                elif result["status"] == "failed":
                    st.error("Enhancement failed.")
                    st.stop()
                time.sleep(1)

            # Show enhanced image
            result_image = Image.open(requests.get(output_url, stream=True).raw)
            st.image(result_image, caption="Enhanced Image", use_column_width=True)

            # Add download button
            buf = io.BytesIO()
            result_image.save(buf, format="PNG")
            byte_img = buf.getvalue()
            b64 = base64.b64encode(byte_img).decode()
            href = f'<a href="data:file/png;base64,{b64}" download="enhanced.png">📥 Download Enhanced Image</a>'
            st.markdown(href, unsafe_allow_html=True)
