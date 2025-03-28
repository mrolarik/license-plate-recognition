import streamlit as st
from PIL import Image, ImageDraw
import easyocr
import numpy as np

# Initialize EasyOCR (add 'th' if you want Thai)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = load_reader()

st.title("🚗 License Plate Recognition")
st.write("Upload an image of a license plate and extract the text. No OpenCV used!")

uploaded_file = st.file_uploader("📷 Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(image)

    st.image(image, caption="Original Image", use_column_width=True)

    with st.spinner("🔍 Detecting license plate..."):
        results = reader.readtext(img_array)

    draw = ImageDraw.Draw(image)
    found_texts = []

    for bbox, text, confidence in results:
        if confidence > 0.4:
            found_texts.append((text, confidence))
            # Draw bounding box
            points = [tuple(point) for point in bbox]
            draw.line(points + [points[0]], fill="red", width=3)

    st.image(image, caption="Detected License Plate", use_column_width=True)

    if found_texts:
        st.write("### 📝 Recognized Text:")
        for text, conf in found_texts:
            st.markdown(f"- **{text}** ({conf*100:.2f}%)")
    else:
        st.warning("No high-confidence license plate text detected.")
