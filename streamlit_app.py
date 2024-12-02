import streamlit as st
import requests
import json
import pandas as pd


st.title("🌀 FEEDBACK108")


# ใส่ API Key สำหรับ Typhoon API
api_key = "sk-6EGVjVrPBYHxOS5xbEGTS4oALtLeev8rE0cTFQuo5qLPKuCL"


# ตรวจสอบว่ามีการสร้าง session_state สำหรับเก็บประวัติหรือไม่
if "messages" not in st.session_state:
    st.session_state.messages = []  # เก็บข้อความสนทนาในรูปแบบ [{"role": "user/assistant", "content": "ข้อความ"}]


# ฟังก์ชันสำหรับส่งคำขอไปยัง Typhoon API
def generate_response(input_text):
    if not api_key.startswith("sk-"):
        st.warning("Please enter a valid Typhoon API key!", icon="⚠")
        return "Invalid API Key"


    payload = {
        "model": "typhoon-instruct",
        "temperature": 0.7,
        "messages": st.session_state.messages,  # ส่งประวัติการสนทนาไปยัง API
    }


    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


    try:
        response = requests.post(
            'https://api.opentyphoon.ai/v1/chat/completions',
            headers=headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        data = response.json()


        if 'choices' in data and len(data['choices']) > 0:
            content = data['choices'][0]['message']['content']
            return content
        else:
            return "No response content found from the API."
    except requests.exceptions.RequestException as e:
        return f"Error occurred: {e}"




# UI สำหรับแสดงประวัติการสนทนา
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").markdown(message["content"])
    elif message["role"] == "assistant":
        # ตรวจสอบว่าข้อความเป็น JSON หรือข้อความทั่วไป
        try:
            # ลองโหลดข้อความเป็น JSON ถ้าสำเร็จแสดงเป็น Visualization
            data = json.loads(message["content"])
            df = pd.DataFrame(data)
            st.bar_chart(df)
        except (json.JSONDecodeError, ValueError):
            # ถ้าไม่ใช่ JSON ให้แสดงข้อความปกติ
            st.chat_message("assistant").markdown(message["content"])




# ฟังก์ชันสำหรับรับข้อความจากผู้ใช้
user_input = st.chat_input("Type your message here...")  # รับข้อความที่ผู้ใช้ป้อน


if user_input:
    # บันทึกข้อความผู้ใช้ใน session_state
    st.session_state.messages.append({"role": "user", "content": user_input})
   
    # แสดงข้อความผู้ใช้ทันที
    st.chat_message("user").markdown(user_input)


    # ส่งข้อความไปยัง Typhoon API และรับคำตอบ
    with st.spinner("Generating response..."):
        assistant_response = generate_response(user_input)


    # บันทึกข้อความตอบกลับใน session_state
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})


    # แสดงข้อความตอบกลับหรือ Visualization
    try:
        data = json.loads(assistant_response)
        df = pd.DataFrame(data)
        st.bar_chart(df)
    except (json.JSONDecodeError, ValueError):
        st.chat_message("assistant").markdown(assistant_response)
