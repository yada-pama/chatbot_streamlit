import streamlit as st
from datetime import datetime
from model import run_model  # นำเข้าฟังก์ชันจากไฟล์ model.py

# ตั้งค่า session_state สำหรับเก็บประวัติการสนทนา
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []

if "current_session" not in st.session_state:
    st.session_state.current_session = None

# ฟังก์ชันเริ่มต้นเซสชันใหม่
def start_new_session():
    st.session_state.current_session = None

# ฟังก์ชันเพิ่มข้อความในเซสชันปัจจุบัน
def add_to_current_session(role, content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if st.session_state.current_session is not None:
        st.session_state.chat_sessions[st.session_state.current_session]["history"].append(
            {"role": role, "content": content, "timestamp": timestamp}
        )

# ส่วนบนซ้ายสำหรับตั้งค่ารุ่น
with st.sidebar.expander("⚙️ Settings", expanded=True):
    model_options = {
        "gpt-4o-mini": "GPT-4o Mini",
        "llama-3.1-405b": "Llama 3.1 405B",
        "llama-3.2-3b": "Llama 3.2 3B",
        "Gemini Pro 1.5": "Gemini Pro 1.5",
    }

    model = st.selectbox(
        "Choose your AI Model:",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x]
    )
    st.session_state["model"] = model

    api_key = st.text_input("API Key", type="password")
    st.session_state["api_key"] = api_key

    temperature = st.slider("Set Temperature:", min_value=0.0, max_value=2.0, value=1.0, step=0.1)
    st.session_state["temperature"] = temperature

# Sidebar สำหรับจัดการประวัติการสนทนา
st.sidebar.title("Chat History")
if st.sidebar.button("Start New Chat"):
    start_new_session()

# ส่วนหลักของแอปพลิเคชัน
st.title("Chat Application")

user_input = st.chat_input("Type your message here...")
if user_input:
    if st.session_state.current_session is None:
        st.session_state.chat_sessions.append({"title": "", "history": []})
        st.session_state.current_session = len(st.session_state.chat_sessions) - 1

    add_to_current_session("user", user_input)

    # เรียกใช้โมเดลจาก model.py
    response = run_model(
        input_text=user_input,
        model=model,
        temperature=temperature,
        api_key=api_key
    )

    add_to_current_session("assistant", response)

if st.session_state.current_session is not None:
    session = st.session_state.chat_sessions[st.session_state.current_session]
    for chat in session["history"]:
        role = "You" if chat["role"] == "user" else "Bot"
        st.write(f"**{role} :** {chat['content']}")
