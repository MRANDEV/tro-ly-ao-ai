import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
import requests
from streamlit_mic_recorder import mic_recorder


# Nạp chìa khóa API từ file .env
load_dotenv()

# Cấu hình giao diện Web
st.set_page_config(page_title="Trợ Lý Áo AI", page_icon="🤖")
st.components.v1.html(f'<div style="display:flex; justify-content:center;"><iframe src="https://lottie.host" style="border:none; width:200px; height:200px;"></iframe></div>', height=200)

st.title("🤖 Trợ Lý Ảo của An")
st.caption("Ứng dụng AI chạy bằng Python")

# Khởi tạo kết nối với Google AI
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Chưa tìm thấy GEMINI_API_KEY trong file .env!")
    st.stop()

client = genai.Client(api_key=api_key)

# Lưu lịch sử trò chuyện để bot nhớ nội dung câu hỏi trước
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lại các tin nhắn cũ ra màn hình
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- ĐOẠN CODE THÊM CHỨC NĂNG VOICE CHAT ---
st.write("🎤 Hoặc bấm giữ nút dưới đây để nói chuyện bằng giọng nói:")
audio_file = mic_recorder(
    start_prompt="🔴 Bắt đầu nói",
    stop_prompt="⏹️ Hoàn thành nói",
    key='recorder'
)

if audio_file:
    audio_bytes = audio_file['bytes']
    with st.chat_message("user"):
        st.audio(audio_bytes, format='audio/wav')
    st.session_state.messages.append({"role": "user", "content": "🎵 [Tin nhắn thoại]"})
    
    with st.chat_message("assistant"):
        with st.spinner("AI đang nghe..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        {"mime_type": "audio/wav", "data": audio_bytes},
                        "Hãy lắng nghe và trả lời ngắn gọn câu hỏi này."
                    ]
                )
                bot_reply = response.text
                st.write(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"Lỗi: {e}")
# --------------------------------------------


# Khung nhập câu hỏi của người dùng
if prompt := st.chat_input("Hỏi tôi bất kỳ điều gì..."):
    # 1. Hiện câu hỏi của người dùng lên màn hình
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 2. Gửi câu hỏi cho Gemini và nhận câu trả lời
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            with st.spinner("AI đang suy nghĩ..."):
                response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=prompt
                )
                bot_reply = response.text
            message_placeholder.write(bot_reply)
            
            
            # Lưu câu trả lời vào lịch sử
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        except Exception as e:
            message_placeholder.error(f"Lỗi kết nối: {e}")