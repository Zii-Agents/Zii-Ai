import time
import streamlit as st
from openai import OpenAI

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Zii-AI Assistant", page_icon="🤖", layout="centered"
)

# 2. Custom CSS Biar Estetik
st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 3. Sidebar untuk Pengaturan Model, Upload File, & Riwayat Chat
with st.sidebar:
  st.image(
      "https://img.icons8.com/color/96/artificial-intelligence.png", width=70
  )
  st.title("Zii-AI Control")
  st.info(
      "🚀 **1B Token Power**\nTerhubung aman ke 9Router API dengan fitur"
      " multimodal."
  )

  st.markdown("---")

  # Pilihan Model AI Resmi 9Router
  model_choice = st.selectbox(
      "🤖 Pilih Model AI:",
      [
          "deepseek-ai/DeepSeek-V4-Flash-0731",
          "MiniMaxAI/MiniMax-M2.7",
          "zai-org/GLM-5.3-Flash",
      ],
  )

  st.markdown("---")

  # Fitur Upload File dipindah ke Sidebar agar layar utama bersih ala Gemini
  uploaded_file = st.file_uploader(
      "📎 Lampirkan File/Foto (Opsional):",
      type=["png", "jpg", "jpeg", "pdf"],
  )

  st.markdown("---")

  if st.button("🧹 Bersihkan Riwayat Chat", type="primary"):
    st.session_state.messages = []
    st.rerun()

  st.write("Dibuat dengan ❤️ oleh Zii")

# 4. Tampilan Utama
st.title("🤖 Zii-AI Assistant")
st.caption(
    "Asisten cerdas serbaguna. Ketik pesan di bawah, atau upload file lewat"
    " menu sidebar ☰ di pojok kiri atas."
)

# Inisialisasi OpenAI Client dengan Base URL 9Router
client = OpenAI(
    api_key=st.secrets.get("OPENAI_API_KEY"),
    base_url="https://secure.rootly.my.id/v1",
)

# Simpan riwayat chat di session state
if "messages" not in st.session_state:
  st.session_state.messages = []

# Tampilkan riwayat pesan chat sebelumnya
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    if message.get("file_url"):
      st.image(
          message["file_url"], caption="Lampiran File", use_container_width=True
      )
    st.markdown(message["content"])
    if message.get("resp_time"):
      st.caption(f"⚡ Respon dalam {message['resp_time']}")

# 5. Kolom Input Chat Utama (Bersih & Full Lebar di Bawah)
if user_input := st.chat_input("Ketik pesan di sini..."):
  file_container = uploaded_file if uploaded_file else None

  # Simpan pesan user ke session state
  st.session_state.messages.append(
      {"role": "user", "content": user_input, "file_url": file_container}
  )

  # Render pesan user di UI
  with st.chat_message("user"):
    if file_container:
      st.image(file_container, caption="Lampiran File", use_container_width=True)
    st.markdown(user_input)

  # Kirim permintaan ke API 9Router sekaligus hitung waktu respons (timer)
  with st.chat_message("assistant"):
    with st.spinner("✨ Zii-AI sedang meracik jawaban..."):
      start_time = time.time()
      try:
        response = client.chat.completions.create(
            model=model_choice,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
        )
        end_time = time.time()
        elapsed_time = round(end_time - start_time, 2)

        reply = response.choices[0].message.content
        st.markdown(reply)

        time_info = f"{elapsed_time} detik"
        st.caption(f"⚡ Respon dalam {time_info}")

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply,
            "file_url": None,
            "resp_time": time_info,
        })

        st.rerun()

      except Exception as e:
        st.error(
            f"Terjadi kesalahan saat menghubungi API: {e}\n\nTips: Coba ganti"
            " model di sidebar jika terkena limit (Error 429)."
        )
