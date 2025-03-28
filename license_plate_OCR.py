import streamlit as st
from PIL import Image, ImageDraw
import easyocr
import numpy as np

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'], gpu=False)  # Use ['th', 'en'] for Thai support

st.title("🚗 License Plate Recognition App (No OpenCV)")
st.write("Upload an image with a license plate to extract the text.")

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Original Image", use_column_width=True)

    st.write("🔍 Detecting text...")
    img_array = np.array(image)
    results = reader.readtext(img_array)

    draw = ImageDraw.Draw(image)

    found_texts = []

    for (bbox, text, confidence) in results:
        if confidence > 0.4:  # Filter out low-confidence results
            found_texts.append((text, confidence))
            # Draw bounding box using PIL
            points = [tuple(point) for point in bbox]
            draw.line(points + [points[0]], fill="red", width=3)

    st.image(image, caption="Detected License Plate", use_column_width=True)

    if found_texts:
        st.write("### 📝 Recognized Text:")
        for text, conf in found_texts:
