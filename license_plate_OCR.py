import streamlit as st
from PIL import Image, ImageDraw
import easyocr
import numpy as np
import requests
from io import BytesIO

# Initialize EasyOCR reader (Thai + English)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['th', 'en'], gpu=False)

reader = load_reader()

st.title("🚗 Text Recognition (OCR)")
st.write("อัปโหลดหรือป้อน URL ของภาพที่มีข้อความ ระบบจะตรวจจับและอ่านข้อความ (รองรับภาษาไทยและอังกฤษ)")

# ======== Input method: Upload or URL ========
input_method = st.radio("เลือกรูปแบบการนำเข้ารูปภาพ:", ["📁 อัปโหลดรูปภาพ", "🌐 ป้อน URL รูปภาพ"])

image = None

if input_method == "📁 อัปโหลดรูปภาพ":
    uploaded_file = st.file_uploader("📷 เลือกรูปภาพ", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")

elif input_method == "🌐 ป้อน URL รูปภาพ":
    image_url = st.text_input("🔗 วางลิงก์ URL ของรูปภาพที่ต้องการตรวจจับข้อความ")
    if image_url:
        try:
            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content)).convert("RGB")
            st.success("✅ โหลดรูปภาพสำเร็จ")
        except:
            st.error("❌ ไม่สามารถโหลดภาพจาก URL ได้ กรุณาตรวจสอบลิงก์")

# ======== If an image is loaded ========
if image:
    st.image(image, caption="📸 ภาพที่นำเข้า", use_container_width=True)

    img_array = np.array(image)

    with st.spinner("🔍 กำลังตรวจจับข้อความ..."):
        results = reader.readtext(img_array)

    draw = ImageDraw.Draw(image)
    found_texts = []

    for bbox, text, confidence in results:
        if confidence > 0.4:
            found_texts.append((text, confidence))
            points = [tuple(point) for point in bbox]
            draw.line(points + [points[0]], fill="red", width=3)

    st.image(image, caption="🟥 ตรวจพบข้อความ", use_container_width=True)

    if found_texts:
        st.write("### 📝 ข้อความที่ตรวจพบ:")
        for text, conf in found_texts:
            st.write(f"- **{text}** ({conf*100:.2f}%)")
    else:
        st.warning("ไม่พบข้อความที่มีความมั่นใจเพียงพอ")
