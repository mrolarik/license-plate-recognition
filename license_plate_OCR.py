import streamlit as st
from PIL import Image, ImageDraw
import easyocr
import numpy as np

# Initialize EasyOCR reader with Thai and English support
@st.cache_resource
def load_reader():
    return easyocr.Reader(['th', 'en'], gpu=False)

reader = load_reader()

st.title("🚗 Thai License Plate Recognition")
st.write("อัปโหลดภาพป้ายทะเบียนรถ เพื่อดึงข้อความออกมา (รองรับภาษาไทย)")

# Upload image
uploaded_file = st.file_uploader("📷 เลือกรูปภาพ", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Open and display image
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="📸 ภาพที่อัปโหลด", use_column_width=True)

    # Convert to NumPy for EasyOCR
    img_array = np.array(image)

    with st.spinner("🔍 กำลังประมวลผล..."):
        results = reader.readtext(img_array)

    # Prepare for drawing bounding boxes
    draw = ImageDraw.Draw(image)
    found_texts = []

    for bbox, text, confidence in results:
        if confidence > 0.4:  # Adjust this threshold if needed
            found_texts.append((text, confidence))
            # Draw bounding box with PIL
            points = [tuple(point) for point in bbox]
            draw.line(points + [points[0]], fill="red", width=3)

    # Show image with boxes
    st.image(image, caption="🟥 ตรวจพบข้อความ", use_column_width=True)

    if found_texts:
        st.write("### 📝 ข้อความที่ตรวจพบ:")
        for text, conf in found_texts:
            st.write(f"- **{text}** ({conf*100:.2f}%)")
    else:
        st.warning("ไม่พบข้อความป้ายทะเบียนที่ชัดเจน")
