try:
    import streamlit as st
    import requests
    from PIL import Image
    import io
    import base64
    import time

    # 🔐 Replace with your Replicate API Token
    REPLICATE_TOKEN = st.secrets["REPLICATE_TOKEN"] if "REPLICATE_TOKEN" in st.secrets else ""
    IMGBB_KEY = st.secrets["IMGBB_KEY"] if "IMGBB_KEY" in st.secrets else ""

    if not REPLICATE_TOKEN:
        st.error("Replicate API token not found. Please set it in Streamlit secrets.")
        st.stop()

    if not IMGBB_KEY:
        st.error("ImgBB API key not found. Please set it in Streamlit secrets.")
        st.stop()

    # Upload section
    st.title("🔭 AstroVision AI")
    st.markdown("Upload a telescope image and enhance it using AI.")

    uploaded_file = st.file_uploader("📷 Upload an image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Original Image", use_column_width=True)

        if st.button("✨ Enhance Image"):
            with st.spinner("Enhancing..."):
                try:
                    img_bytes = io.BytesIO()
                    image.save(img_bytes, format='PNG')
                    img_bytes.seek(0)

                    upload = requests.post(
                        "https://api.imgbb.com/1/upload",
                        params={"key": IMGBB_KEY},
                        files={"image": img_bytes}
                    )

                    if upload.status_code != 200:
                        st.error("Image upload failed.")
                        st.write("Status Code:", upload.status_code)
                        st.write("Response:", upload.text)
                        st.stop()

                    image_url = upload.json()["data"]["url"]

                    headers = {
                        "Authorization": f"Token {REPLICATE_TOKEN}",
                        "Content-Type": "application/json"
                    }

                    # ✅ Using a working version ID from a different model (stability-ai/sdxl) for general image enhancement
                    payload = {
                        "version": "cde69fdcf8e054dd1df7e7d9d1b858141198df7f4b2e3fdfc269d376c80f89fc",
                        "input": {
                            "prompt": "high quality enhanced photo of deep space telescope capture",
                            "image": image_url
                        }
                    }

                    response = requests.post(
                        "https://api.replicate.com/v1/predictions",
                        headers=headers,
                        json=payload
                    )

                    if response.status_code == 401:
                        st.error("Unauthorized. Invalid Replicate token.")
                        st.write("Response:", response.text)
                        st.stop()

                    if response.status_code != 201:
                        st.error("Replicate call failed.")
                        st.write("Status Code:", response.status_code)
                        st.write("Payload:", payload)
                        st.write("Response:", response.text)
                        st.stop()

                    prediction_url = response.json()["urls"]["get"]

                    while True:
                        result = requests.get(prediction_url, headers=headers).json()
                        if result.get("status") == "succeeded":
                            output_url = result["output"]
                            break
                        elif result.get("status") == "failed":
                            st.error("Enhancement failed.")
                            st.stop()
                        time.sleep(1)

                    result_image = Image.open(requests.get(output_url, stream=True).raw)
                    st.image(result_image, caption="Enhanced Image", use_column_width=True)

                    buf = io.BytesIO()
                    result_image.save(buf, format="PNG")
                    byte_img = buf.getvalue()
                    b64 = base64.b64encode(byte_img).decode()
                    href = f'<a href="data:file/png;base64,{b64}" download="enhanced.png">📥 Download Enhanced Image</a>'
                    st.markdown(href, unsafe_allow_html=True)

                except Exception as e:
                    st.error("Unexpected error occurred.")
                    st.write("Error details:", str(e))

except Exception as e:
    print("This script requires Streamlit. Please make sure you're running this in a Streamlit environment.")
    print("Error:", e)


