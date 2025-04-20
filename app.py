import base64

# Hugging Face Space URL
api_url = "https://sczhou-real-esrgan.hf.space/run/predict"

# Convert uploaded file to bytes
image_bytes = uploaded_file.read()

# Send request to Hugging Face
files = {"data": ("image.jpg", image_bytes, "image/jpeg")}
response = requests.post(api_url, files=files)

if response.ok:
    result = response.json()
    # Extract base64 result
    enhanced_base64 = result["data"][0].split(",")[-1]
    enhanced_image = Image.open(BytesIO(base64.b64decode(enhanced_base64)))
    st.image(enhanced_image, caption="Enhanced Image", use_column_width=True)
else:
    st.error("❌ Enhancement failed. Try again with a different image or check the model status.")

