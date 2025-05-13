import streamlit as st
import os
from google import genai
import google.generativeai as genai
from google.genai import types
from io import BytesIO
# from python_docx import Document
from docx import Document
# Tải API Key từ môi trường (cập nhật nếu cần)

# API_KEY = os.getenv("AIzaSyAfQfOJgGCRxJyDMjr9Kv5XpBGTZX_pASQ")
# API_KEY = "AIzaSyAfQfOJgGCRxJyDMjr9Kv5XpBGTZX_pASQ"
def generate_transcription(file_path):
    API_KEY = st.secrets["GEMINI_API_KEY"]  # Lấy API Key từ Streamlit Secrets
    if not API_KEY:
        raise ValueError("API Key is missing. Please set the GEMINI_API_KEY in the Streamlit secrets.")
    
    # Khởi tạo client Google GenAI
   client = genai.Client(api_key=API_KEY)
    files = [
        client.files.upload(file=file_path),
    ]
    model = "gemini-2.5-flash-preview-04-17"
    
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_uri(file_uri=files[0].uri, mime_type=files[0].mime_type)],
        ),
        types.Content(
            role="model",
            parts=[types.Part.from_text(text="lấy nội dung đàm thoại của file âm thanh này")],
        ),
    ]
    
    response = client.models.generate_content(model=model, contents=contents)
    return response.text
    
# Tạo và tải xuống file Word (.docx)
def create_word_document(transcription):
    doc = Document()
    doc.add_heading('Transcription from Audio File', 0)
    doc.add_paragraph(transcription)
    
    # Lưu vào bộ nhớ tạm
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Giao diện Streamlit
def main():
    st.title("Audio Transcription to Word")
    st.write("Tải lên file âm thanh để trích xuất nội dung và lưu dưới dạng file Word.")
    
    uploaded_file = st.file_uploader("Chọn file âm thanh", type=["mp3", "m4a", "wav"])

    if uploaded_file is not None:
        # Tạo file tạm từ file tải lên
        with open("temp_audio_file", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Gọi hàm để trích xuất nội dung
        transcription = generate_transcription("temp_audio_file")
        st.write("Nội dung trích xuất từ âm thanh:")
        st.text_area("Transcript", transcription, height=200)

        # Tạo và cho phép tải xuống file Word
        word_file = create_word_document(transcription)
        st.download_button(
            label="Tải về file Word",
            data=word_file,
            file_name="transcription.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

if __name__ == "__main__":
    main()
