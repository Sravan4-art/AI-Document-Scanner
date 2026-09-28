# ============================================================
# IMPORT LIBRARIES
# ============================================================

import streamlit as st
import easyocr
import os
from PIL import Image
from docx import Document
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# GROQ API SETUP
# ============================================================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ============================================================
# CREATE FOLDERS
# ============================================================

os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Document Scanner",
    layout="wide"
)

# ============================================================
# TITLE
# ============================================================

st.title("AI Document Scanner using OCR + LLM")

st.write("""
Upload JPG, JPEG or PNG document images.

This AI system will:
- Extract text using OCR
- Understand document using LLM
- Generate structured JSON
- Export TXT, JSON and DOCX files
""")

# ============================================================
# FILE UPLOADER
# ============================================================

uploaded_file = st.file_uploader(
    "Upload Document Image",
    type=["jpg", "jpeg", "png"]
)

# ============================================================
# PROCESS DOCUMENT
# ============================================================

if uploaded_file is not None:

    # --------------------------------------------------------
    # SAVE UPLOADED IMAGE
    # --------------------------------------------------------

    file_path = os.path.join(
        "uploads",
        uploaded_file.name
    )

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # --------------------------------------------------------
    # DISPLAY IMAGE
    # --------------------------------------------------------

    image = Image.open(file_path)

    st.image(
        image,
        caption="Uploaded Document",
        use_container_width=True
    )

    st.success("Image Uploaded Successfully")

    # --------------------------------------------------------
    # OCR EXTRACTION
    # --------------------------------------------------------

    st.subheader("OCR Text Extraction")

    with st.spinner("Extracting text from image..."):

        reader = easyocr.Reader(['en'])# creates ocr engine

        result = reader.readtext(file_path)#extracts text from image

        extracted_text = ""

        for detection in result:
            extracted_text += detection[1] + "\n"

    # DISPLAY EXTRACTED TEXT

    st.text_area(
        "Extracted Text",
        extracted_text,
        height=250
    )

    # --------------------------------------------------------
    # LLM DOCUMENT UNDERSTANDING
    # --------------------------------------------------------

    st.subheader("LLM Document Understanding")

    prompt = f"""
    You are an intelligent document analyzer.

    Extract all important information from this document.

    Return proper structured JSON only.

    Document Text:
    {extracted_text}
    """

    with st.spinner("Processing document using LLM..."):

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        structured_output = response.choices[0].message.content

    # DISPLAY STRUCTURED OUTPUT

    st.text_area(
        "Structured JSON Output",
        structured_output,
        height=300
    )

    # --------------------------------------------------------
    # SAVE TXT FILE
    # --------------------------------------------------------

    txt_path = "outputs/extracted_text.txt"

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    # --------------------------------------------------------
    # SAVE JSON FILE
    # --------------------------------------------------------

    json_path = "outputs/structured_output.json"

    with open(json_path, "w", encoding="utf-8") as f:
        f.write(structured_output)

    # --------------------------------------------------------
    # SAVE DOCX FILE
    # --------------------------------------------------------

    doc = Document()

    doc.add_heading(
        "AI Document Scanner Output",
        level=1
    )

    doc.add_heading(
        "Extracted Text",
        level=2
    )

    doc.add_paragraph(extracted_text)

    doc.add_heading(
        "Structured JSON Output",
        level=2
    )

    doc.add_paragraph(structured_output)

    docx_path = "outputs/document_output.docx"

    doc.save(docx_path)

    st.success("Files Generated Successfully!")

    # --------------------------------------------------------
    # DOWNLOAD BUTTONS
    # --------------------------------------------------------

    st.subheader("⬇ Download Generated Files")

    col1, col2, col3 = st.columns(3)

    # TXT DOWNLOAD

    with col1:

        with open(txt_path, "rb") as file:

            st.download_button(
                label="Download TXT",
                data=file,
                file_name="extracted_text.txt",
                mime="text/plain"
            )

    # JSON DOWNLOAD

    with col2:

        with open(json_path, "rb") as file:

            st.download_button(
                label="Download JSON",
                data=file,
                file_name="structured_output.json",
                mime="application/json"
            )

    # DOCX DOWNLOAD

    with col3:

        with open(docx_path, "rb") as file:

            st.download_button(
                label="Download DOCX",
                data=file,
                file_name="document_output.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

