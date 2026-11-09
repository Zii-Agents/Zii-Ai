import time
import streamlit as st
from openai import OpenAI

# 1. Konfigurasi Halaman & Meta UI
st.set_page_config(
    page_title="Gemini", 
    page_icon="✨", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. CSS Kustom untuk Mengubah Tampilan Streamlit Menjadi Gemini UI Presisi
st.markdown("""
    <style>
    /* Styling Header & Navbar */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 7rem !important;
        max-width: 720px;
    }
    
    /* Hilangkan Uploader Bawaan yang Mengganggu */
    [data-testid="stFileUploader"] {
        padding: 0;
    }
    [data-testid="stFileUploader"] section {
        padding: 0 !important;
        border: none !important;
        background: transparent !important;
    }
    [data-testid="stFileUploader"] section > input + div {
        display: none !important;
    }

    /* Kustomisasi Box Chat Input agar Melayang dan Ber-rounded Capsule */
    .stChatInputContainer {
        border-radius: 28px !important;
        border: 1px solid #e0e0e0 !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05) !important;
        background-color: #ffffff !important;
    }

    /* Respon Caption & Timer */
    .timer-badge {
        font-size: 0.78rem;
        color: #707070;
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Floating Model Switcher & Header Ala Gemini (Top Bar)
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    model_choice = st.selectbox(
        "Model Selection",
        [
            "zai-org/GLM-5.3-Flash",
            "deepseek-ai/DeepSeek-V4-Flash-0731",
            "MiniMaxAI/MiniMax-M2.7"
        ],
        label_visibility="collapsed"
    )

with st.sidebar:
    st.title("⚙️ Pengaturan Zii-AI")
    st.info("Koneksi API 9Router Aktif")
    if st.button("🧹 Hapus Chat", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 4. Inisialisasi API & Session State
client = OpenAI(
    api_key=st.secrets.get("OPENAI_API_KEY"),
    base_url="https://secure.rootly.my.id/v1",
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan Riwayat Percakapan
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("file_bytes"):
            st.image(message["file_bytes"], caption="Lampiran File", use_container_width=True)
        st.markdown(message["content"])
        if message.get("resp_time"):
            st.markdown(f'<div class="timer-badge">⚡ {message["resp_time"]}</div>', unsafe_allow_html=True)

# 5. File Upload Compact di Atas Input (Atau Integrasi Tombol Lampiran)
with st.popover("➕ Lampirkan File / Gambar", use_container_width=True):
    uploaded_file = st.file_uploader(
        "Pilih file", 
        type=["png", "jpg", "jpeg", "pdf"],
        label_visibility="collapsed"
    )

# Input Chat Utama
if user_input := st.chat_input("Minta Zii-AI..."):
    file_data = uploaded_file.getvalue() if uploaded_file else None

    # Simpan dan Tampilkan Pesan User
    st.session_state.messages.append({
        "role": "user", 
        "content": user_input, 
        "file_bytes": file_data
    })
    
    with st.chat_message("user"):
        if file_data:
            st.image(file_data, caption="Lampiran File", use_container_width=True)
        st.markdown(user_input)

    # Kirim Request ke API & Hitung Latensi Response
    with st.chat_message("assistant"):
        with st.spinner("✨ Meracik jawaban..."):
            start_time = time.time()
            try:
                response = client.chat.completions.create(
                    model=model_choice,
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                )
                elapsed_time = round(time.time() - start_time, 2)
                reply = response.choices[0].message.content
                
                st.markdown(reply)
                time_info = f"{elapsed_time} detik"
                st.markdown(f'<div class="timer-badge">⚡ Respon dalam {time_info}</div>', unsafe_allow_html=True)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply,
                    "file_bytes": None,
                    "resp_time": time_info,
                })
            except Exception as e:
                st.error(f"Gagal memproses pesan: {e}")
