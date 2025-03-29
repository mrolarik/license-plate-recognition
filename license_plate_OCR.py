import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import easyocr
import numpy as np
import requests
from io import BytesIO

# ==== Load OCR Reader (Thai + English) ====
@st.cache_resource
def load_reader():
    return easyocr.Reader(['th', 'en'], gpu=False)

reader = load_reader()

# ==== Sidebar: Sample Image ====
st.sidebar.header("🖼️ ตัวอย่างภาพ")
sample_url = "https://i.imgur.com/4n1pUtM.jpg"
st.sidebar.image(sample_url, caption="ภาพตัวอย่าง", use_column_width=True)
use_sample = st.sidebar.button("ใช้ภาพตัวอย่างนี้")

# ==== Title and Info ====
st.title("🚗 Text Recognition (OCR)")
st.write("อัปโหลดภาพหรือป้อน URL เพื่อดึงข้อความจากภาพ (รองรับภาษาไทยและอังกฤษ)")

# ==== Input Method ====
image = None
if use_sample:
    try:
        response = requests.get(sample_url)
        image = Image.open(BytesIO(response.content)).convert("RGB")
        st.success("✅ โหลดภาพตัวอย่างสำเร็จ")
    except:
        st.error("❌ ไม่สามารถโหลดภาพตัวอย่างได้ กรุณาลองอีกครั้ง")

else:
    input_method = st.radio("เลือกรูปแบบการนำเข้ารูปภาพ:", ["📁 อัปโหลดรูปภาพ", "🌐 ป้อน URL รูปภาพ"])

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

# ==== Run OCR if image is ready ====
if image:
    st.image(image, caption="📸 ภาพที่นำเข้า", use_container_width=True)

    img_array = np.array(image)

    with st.spinner("🔍 กำลังตรวจจับข้อความ..."):
        results = reader.readtext(img_array)

    draw = ImageDraw.Draw(image)

    # ==== Load Font for Index Numbers ====
    try:
        font = ImageFont.truetype("arial.ttf", 24)  # You can replace with any TTF font
    except:
        font = ImageFont.load_default()

    found_texts = []

    # ==== Draw boxes and numbers ====
    for idx, (bbox, text, confidence) in enumerate(results, start=1):
        if confidence > 0.4:
            found_texts.append((idx, text, confidence))
            points = [tuple(point) for point in bbox]
            draw.line(points + [points[0]], fill="red", width=3)
            draw.text(points[0], str(idx), fill="yellow", font=font)

    st.image(image, caption="🟥 ตรวจพบข้อความ", use_container_width=True)

    # ==== Show Numbered Output Text ====
    if found_texts:
        st.write("### 📝 ข้อความที่ตรวจพบ:")
        for idx, text, conf in found_texts:
            st.write(f"{idx}. **{text}** ({conf*100:.2f}%)")
    else:
        st.warning("ไม่พบข้อความที่มีความมั่นใจเพียงพอ")
