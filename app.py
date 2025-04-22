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
    st.title("🌠 AstroVision AI")
    st.markdown("Upload a telescope image and enhance it using AI.")

    uploaded_file = st.file_uploader("📷 Upload an image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Original Image", use_column_width=True)

        enhance_button = st.button("✨ Enhance Image")
        detect_button = st.button("🔎 Detect Objects")

        if enhance_button:
            st.session_state.enhanced_url = None  # Reset any prior result

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

                    # ✅ Enhancement using Real-ESRGAN
                    payload = {
                        "version": "f121d640bd286e1fdc67f9799164c1d5be36ff74576ee11c803ae5b665dd46aa",
                        "input": {
                            "image": image_url,
                            "scale": 2,
                            "face_enhance": False
                        }
                    }

                    response = requests.post(
                        "https://api.replicate.com/v1/predictions",
                        headers=headers,
                        json=payload
                    )

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
                            output_url = result["output"][0] if isinstance(result["output"], list) else result["output"]
                            st.session_state.enhanced_url = output_url
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
                    href = f'<a href="data:file/png;base64,{b64}" download="enhanced.png">📅 Download Enhanced Image</a>'
                    st.markdown(href, unsafe_allow_html=True)

                except Exception as e:
                    st.error("Unexpected error occurred during enhancement.")
                    st.write("Error details:", str(e))

        if detect_button:
            if "enhanced_url" not in st.session_state or not st.session_state.enhanced_url:
                st.warning("Please enhance an image first.")
            else:
                st.info("Running object detection on enhanced image...")

                try:
                    headers = {
                        "Authorization": f"Token {REPLICATE_TOKEN}",
                        "Content-Type": "application/json"
                    }

                    # ✅ Updated to use AI-powered celestial object detection
                    detect_payload = {
                        "version": "e2db0152b4a8609a6d08458e30779c1846f38b947a1cf63dcb0a3d180911b06e",
                        "input": {
                            "image": st.session_state.enhanced_url
                        }
                    }

                    detect_response = requests.post(
                        "https://api.replicate.com/v1/predictions",
                        headers=headers,
                        json=detect_payload
                    )

                    if detect_response.status_code != 201:
                        st.error("Object detection call failed.")
                        st.write("Status Code:", detect_response.status_code)
                        st.write("Payload:", detect_payload)
                        st.write("Response:", detect_response.text)
                        st.stop()

                    detect_url = detect_response.json()["urls"]["get"]

                    while True:
                        detect_result = requests.get(detect_url, headers=headers).json()
                        if detect_result.get("status") == "succeeded":
                            detect_output = detect_result["output"]
                            break
                        elif detect_result.get("status") == "failed":
                            st.error("Detection failed.")
                            st.stop()
                        time.sleep(1)

                    if detect_output:
                        st.image(detect_output, caption="Detected Celestial Objects", use_column_width=True)
                    else:
                        st.warning("No objects detected or no visual result returned.")

                except Exception as e:
                    st.error("Unexpected error occurred during detection.")
                    st.write("Error details:", str(e))

except Exception as e:
    print("This script requires Streamlit. Please make sure you're running this in a Streamlit environment.")
    print("Error:", e)
