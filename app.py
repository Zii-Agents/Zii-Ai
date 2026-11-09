import sqlite3
import time
import streamlit as st
from openai import OpenAI

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="zii-agent.ai", page_icon="🤖", layout="centered"
)


# 2. Inisialisasi Database SQLite
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

# 4. Sidebar Zii-Ai Menu
with st.sidebar:
  st.image(
      "https://img.icons8.com/color/96/artificial-intelligence.png", width=70
  )
  st.title("Zii-Ai Menu")
  st.info(
      "**zii-agent.ai**\nTerhubung ke 9Router API dengan penyimpanan riwayat"
      " permanen."
  )

  st.markdown("---")

  model_choice = st.selectbox(
      "Pilih Model AI:",
      [
          "zai-org/GLM-5.3-Flash",
          "deepseek-ai/DeepSeek-V4-Flash-0731",
          "MiniMaxAI/MiniMax-M2.7",
      ],
  )

  st.markdown("---")

  if st.button("Bersihkan Riwayat Chat", type="primary"):
    clear_db()
    st.rerun()

  st.write("Dibuat oleh Zii")

# 5. Tampilan Utama
st.title("Zii-Agent.Ai")
st.caption("Asisten cerdas serbaguna. Gunakan menu upload di bawah untuk melampirkan file.")

client = OpenAI(
    api_key=st.secrets.get("OPENAI_API_KEY"),
    base_url="https://secure.rootly.my.id/v1",
)

messages = load_messages()

# Tampilkan riwayat chat
for message in messages:
  with st.chat_message(message["role"]):
    if message.get("file_url"):
      st.image(
          message["file_url"], caption="Lampiran File", use_container_width=True
      )
    st.markdown(message["content"])
    if message.get("resp_time"):
      st.caption(f"Respon dalam {message['resp_time']}")

# Area Upload File
uploaded_file = st.file_uploader(
    "Upload foto atau dokumen (opsional):", type=["png", "jpg", "jpeg", "pdf"]
)

# Input Chat Utama
if user_input
