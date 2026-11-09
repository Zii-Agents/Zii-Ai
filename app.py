import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Zii-AI", page_icon="🤖")

st.title("🤖 Zii-AI Assistant")
st.write("1B Token Power • Chat & Image Support")

# Pilihan Model AI
model_choice = st.selectbox(
    "Pilih Model AI:", ["DeepSeek V4 Flash", "GLM 5.3 Flash", "MiniMax M2.7"]
)

# Inisialisasi client OpenAI dengan base_url secure
client = OpenAI(
    api_key=st.secrets.get("OPENAI_API_KEY"),
    base_url="https://secure.rootly.my.id/v1",
)

# Simpan riwayat chat di session state
if "messages" not in st.session_state:
  st.session_state.messages = []

# Tampilkan pesan sebelumnya
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# Fitur Upload Gambar / File
uploaded_file = st.file_uploader(
    "Upload foto atau dokumen (opsional):", type=["png", "jpg", "jpeg", "pdf"]
)

# Input chat dari user
if user_input := st.chat_input("Ketik pesan di sini..."):
  # Tampilkan gambar kalau user ada upload foto
  if uploaded_file:
    st.image(uploaded_file, caption="Gambar yang di-upload", use_container_width=True)

  # Simpan pesan user
  st.session_state.messages.append({"role": "user", "content": user_input})
  with st.chat_message("user"):
    st.markdown(user_input)

  # Kirim ke API 9Router
  with st.chat_message("assistant"):
    with st.spinner("AI lagi mikir..."):
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
            {"role": "assistant", "content": reply}
        )
      except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

