import sqlite3
import time
import streamlit as st
from openai import OpenAI

# 1. Konfigurasi Halaman & Mobile Fix untuk Sidebar
st.set_page_config(
    page_title="Tauhid-agent.ai"
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Custom CSS untuk Merapikan Tampilan & Mencegah Bug Sidebar di HP
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }
    section[data-testid="stSidebar"] {
        top: 0 !important;
        height: 100% !important;
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 1rem !important;
    }
    .main {
        background-color: #f8f9fa;
    }
    </style>
""", unsafe_allow_html=True)


# 3. Inisialisasi Database SQLite (Riwayat Chat Permanen)
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

# 4. Sidebar tauhid-Ai Menu
with st.sidebar:
  st.image(
      "https://img.icons8.com/color/96/artificial-intelligence.png", width=70
  )
  st.title("Tauhid-Ai Menu")
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

  st.write("Dibuat oleh Tauhid-agent")

# 5. Tampilan Utama
st.title("Tauhid-agent.ai")
st.caption("Asisten cerdas serbaguna. Gunakan menu upload di bawah untuk melampirkan file.")

client = OpenAI(
    api_key=st.secrets.get("OPENAI_API_KEY"),
    base_url="https://secure.rootly.my.id/v1",
)

messages = load_messages()

# Tampilkan riwayat chat dari database
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
if user_input := st.chat_input("Ketik pesan di sini..."):
  file_container = uploaded_file if uploaded_file else None

  save_message("user", user_input, file_container)

  with st.chat_message("user"):
    if file_container:
      st.image(file_container, caption="Lampiran File", use_container_width=True)
    st.markdown(user_input)

  with st.chat_message("assistant"):
    with st.spinner("Memproses respons..."):
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

        # Membersihkan tag <think> jika model memunculkannya
        if "</think>" in reply:
          reply = reply.split("</think>")[-1].strip()

        st.markdown(reply)

        time_info = f"{elapsed_time} detik"
        st.caption(f"Respon dalam {time_info}")

        save_message("assistant", reply, None, time_info)

      except Exception as e:
        st.error(
            f"Terjadi kesalahan saat menghubungi API: {e}\n\nTips: Coba ganti"
            " model di sidebar."
        )
