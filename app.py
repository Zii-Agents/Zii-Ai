import os
import streamlit as st
from openai import OpenAI

# Ambil API key dan atur konfigurasi 9Router
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://router.rootly.my.id/v1"
)

st.title("Zii-AI")
st.write("Tanya apa saja, agent ini aktif 24 jam!")

# Pilihan model dari daftar kamu
model_choice = st.selectbox(
    "Pilih Model AI:",
    [
        "openai-compatible-chat-14db1a0f-609d-4fae-89e4-09ef54f83fce/zai-org/GLM-5.3-Flash",
        "openai-compatible-chat-14db1a0f-609d-4fae-89e4-09ef54f83fce/MiniMaxAI/MiniMax-M2.7",
        "openai-compatible-chat-14db1a0f-609d-4fae-89e4-09ef54f83fce/deepseek-ai/DeepSeek-V4-Flash-0731"
    ],
    format_func=lambda x: {
        "openai-compatible-chat-14db1a0f-609d-4fae-89e4-09ef54f83fce/zai-org/GLM-5.3-Flash": "GLM 5.3 Flash",
        "openai-compatible-chat-14db1a0f-609d-4fae-89e4-09ef54f83fce/MiniMaxAI/MiniMax-M2.7": "MiniMax M2.7",
        "openai-compatible-chat-14db1a0f-609d-4fae-89e4-09ef54f83fce/deepseek-ai/DeepSeek-V4-Flash-0731": "DeepSeek V4 Flash"
    }[x]
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ketik pesan di sini..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    response = client.chat.completions.create(
        model=model_choice,
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    )
    
    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)
