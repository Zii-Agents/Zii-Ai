import streamlit as st
from openai import OpenAI

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Zii-AI Assistant", page_icon="🤖", layout="centered"
)

# 2. Custom CSS Biar Makin Estetik ala Gemini
st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    stChatInput {
        border-radius: 20px;
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
      "🚀 **1B Token Power**\nTerhubung aman ke 9Router API dengan fitur"
      " multimodal terpadu."
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
    "Asisten cerdas serbaguna. Lampirkan gambar/dokumen langsung di kolom chat"
    " bawah!"
)

# Inisialisasi OpenAI Client dengan Base URL 9Router
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
    # Jika pesan berisi gambar/file yang dilampirkan sebelumnya
    if "file_url" in message and message["file_url"]:
      st.image(message["file_url"], caption="Lampiran", use_container_width=True)
    st.markdown(message["content"])

# 5. Kolom Input Chat Pintar (Menyatu dengan Upload File ala Gemini)
user_prompt = st.chat_input(
    "Ketik pesan atau lampirkan file...", accept_file="uploaded-file"
)

# Cek apakah user mengirim pesan atau file lewat chat input
if user_prompt:
  user_text = user_prompt.text
  uploaded_file = user_prompt.files[0] if user_prompt.files else None

  # Jika ada file yang di-upload bersamaan
  file_container = None
  if uploaded_file:
    # Tampilkan preview gambar/file di chat user
    file_container = uploaded_file

  # Simpan pesan user ke session
  st.session_state.messages.append(
      {"role": "user", "content": user_text, "file_url": file_container}
