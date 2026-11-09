import sqlite3
import time
import streamlit as st
from openai import OpenAI

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Zii-Agent", page_icon="🤖", layout="centered"
)


# 2. Inisialisasi Database SQLite (Supaya Chat Tetap Ada Saat Di-refresh)
def init_db():
  conn = sqlite3.connect("chat_history.db", check_same_thread=False)
  c = conn.cursor()
  c.execute(
      """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            file_url TEXT,
            resp_time TEXT
        )
    """
  )
  conn.commit()
  conn.close()


def load_messages():
  conn = sqlite3.connect("chat_history.db", check_same_thread=False)
  c = conn.cursor()
  c.execute("SELECT role, content, file_url, resp_time FROM messages")
  rows = c.fetchall()
  conn.close()

  messages = []
  for row in rows:
    messages.append({
        "role": row[0],
        "content": row[1],
        "file_url": row[2],
        "resp_time": row[3],
    })
  return messages


def save_message(role, content, file_url=None, resp_time=None):
  conn = sqlite3.connect("chat_history.db", check_same_thread=False)
  c = conn.cursor()
  c.execute(
      "INSERT INTO messages (role, content, file_url, resp_time) VALUES (?, ?,"
      " ?, ?)",
      (role, content, file_url, resp_time),
  )
  conn.commit()
  conn.close()


def clear_db():
  conn = sqlite3.connect("chat_history.db", check_same_thread=False)
  c = conn.cursor()
  c.execute("DELETE FROM messages")
  conn.commit()
  conn.close()


# Panggil inisialisasi database
init_db()

# 3. Custom CSS Minimalis
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

# 4. Sidebar untuk Pengaturan Model & Fitur Hapus Riwayat
with st.sidebar:
  st.image(
      "https://img.icons8.com/color/96/artificial-intelligence.png", width=70
  )
  st.title("Zii-AI Control")
  st.info(
      "🚀 **1B Token Power**\nTerhubung ke 9Router API dengan penyimpanan"
      " riwayat permanen."
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

  if st.button("🧹 Bersihkan Riwayat Chat", type="primary"):
    clear_db()
    st.rerun()

  st.write("Dibuat dengan oleh Zii")

# 5. Tampilan Utama
st.title("🤖 Zii-Agent.Ai")
st.caption(
    "Asisten cerdas serbaguna. Gunakan tombol upload di bawah lalu ketik pesan."
)

# Inisialisasi Client OpenAI via 9Router
client = OpenAI(
    api_key=st.secrets.get("OPENAI_API_KEY"),
    base_url="https://secure.rootly.my.id/v1",
)

# Load riwayat dari database SQLite
messages = load_messages()

# Tampilkan riwayat pesan chat yang tersimpan
for message in messages:
  with st.chat_message(message["role"]):
    if message.get("file_url"):
      st.image(
          message["file_url"], caption="Lampiran File", use_container_width=True
      )
    st.markdown(message["content"])
    if message.get("resp_time"):
      st.caption(f"⚡ Respon dalam {message['resp_time']}")

# 6. Area Upload File Pas di Atas Input Text (Sesuai Desain Awal)
uploaded_file = st.file_uploader(
    "📎 Upload foto atau dokumen (opsional):", type=["png", "jpg", "jpeg", "pdf"]
)

# 7. Input Chat Utama
if user_input := st.chat_input("Ketik pesan di sini..."):
  file_container = uploaded_file if uploaded_file else None

  # Simpan pesan user ke database SQLite
  save_message("user", user_input, file_container)

  # Tampilkan pesan user langsung di layar
  with st.chat_message("user"):
    if file_container:
      st.image(file_container, caption="Lampiran File", use_container_width=True)
    st.markdown(user_input)

  # Kirim request ke 9Router API & hitung durasi respons
  with st.chat_message("assistant"):
    with st.spinner("⚡ Sedang memproses pikiran AI..."):
      start_time = time.time()
      try:
        response = client.chat.completions.create(
            model=model_choice,
            messages=[
                {"role": m["role"], "content": m["content"]} for m in messages
            ]
            + [{"role": "user", "content": user_input}],
        )
        end_time = time.time()
        elapsed_time = round(end_time - start_time, 2)

        reply = response.choices[0].message.content
        st.markdown(reply)

        time_info = f"{elapsed_time} detik"
        st.caption(f"⚡ Respon dalam {time_info}")

        # Simpan respons bot ke database SQLite
        save_message("assistant", reply, None, time_info)

      except Exception as e:
        st.error(
            f"Terjadi kesalahan saat menghubungi API: {e}\n\nTips: Coba ganti"
            " model di sidebar jika terkena limit (Error 429)."
        )
