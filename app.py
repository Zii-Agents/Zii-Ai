import streamlit as st
from openai import OpenAI

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Zii-AI Assistant", page_icon="🤖", layout="centered"
)

# 2. Custom CSS Biar Makin Estetik
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

# 3. Sidebar untuk Pengaturan Model & Riwayat
with st.sidebar:
  st.image(
      "https://img.icons8.com/color/96/artificial-intelligence.png", width=70
  )
  st.title("Zii-AI Control")
  st.info(
      "🚀 **1B Token Power**\nTerhubung aman ke 9Router API dengan dukungan"
      " chat & file."
  )

  st.markdown("---")

  # Pilihan Model AI dengan ID Resmi 9Router
  model_choice = st.selectbox(
      "🤖 Pilih Model AI:",
      [
          "deepseek-ai/DeepSeek-V4-Flash-0731",
          "MiniMaxAI/MiniMax-M2.7",
          "zai-org/GLM-5.3-Flash",
      ],
  )

  if st.button("🧹 Bersihkan Riwayat Chat", type="primary"):
    st.session_state.messages = []
    st.rerun()

  st.markdown("---")
  st.write("Dibuat dengan ❤️ oleh Zii")

# 4. Tampilan Utama
st.title("🤖 Zii-AI Assistant")
st.caption(
    "Asisten cerdas serbaguna. Silakan upload file/gambar lalu ketik pesan di"
    " bawah."
)

# Inisialisasi OpenAI Client dengan Base URL 9Router yang aman
client = OpenAI(
    api_key=st.secrets.get("OPENAI_API_KEY"),
    base_url="https://secure.rootly.my.id/v1",
)

# Simpan riwayat chat di session state
if "messages" not in st.session_state:
  st.session_state.messages = []

# Tampilkan riwayat pesan chat
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    if message.get("file_url"):
      st.image(
          message["file_url"], caption="Lampiran File", use_container_width=True
      )
    st.markdown(message["content"])

# 5. Fitur Upload File Terpisah yang Stabil
uploaded_file = st.file_uploader(
    "📎 Upload foto atau dokumen (opsional):", type=["png", "jpg", "jpeg", "pdf"]
)

# 6. Kolom Input Chat
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

  # Kirim permintaan ke API 9Router
  with st.chat_message("assistant"):
    with st.spinner("✨ Zii-AI sedang meracik jawaban..."):
      try:
        response = client.chat.completions.create(
            model=model_choice,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
        )
        reply = response.choices[0].message.content
        st.markdown(reply)
        st.session_state.messages.append(
            {"role": "assistant", "content": reply, "file_url": None}
        )
      except Exception as e:
        st.error(f"Terjadi kesalahan saat menghubungi API: {e}")

