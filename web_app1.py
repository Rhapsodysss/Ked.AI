import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
import os
import json
import PIL.Image
import requests
import streamlit.components.v1 as components

# --- KONFIGURASI DASAR ---
BASE_HISTORY_DIR = "user_histories"
if not os.path.exists(BASE_HISTORY_DIR):
    os.makedirs(BASE_HISTORY_DIR)

ICONS = {
    "app_logo": "https://cdn-icons-png.flaticon.com/512/4712/4712027.png",
    "chat": "https://cdn-icons-png.flaticon.com/512/4712/4712043.png",
    "py": "https://cdn-icons-png.flaticon.com/512/5968/5968350.png",
    "settings": "https://cdn-icons-png.flaticon.com/512/2099/2099058.png",
    "upload": "https://cdn-icons-png.flaticon.com/512/1041/1041916.png",
    "reset": "https://cdn-icons-png.flaticon.com/512/1828/1828665.png"
}

MODERN_CSS = """
<style>
body {background-color: #0e1117; color: #e2e8f0; font-family: 'Segoe UI', sans-serif;}
[data-testid="stSidebar"] {background: linear-gradient(180deg, #1e293b, #0f172a);}
.chat-bubble {border-radius: 16px; padding: 12px 16px; margin: 6px 0; max-width: 80%; word-wrap: break-word;}
.user-bubble {background-color: #2563eb; color: white; margin-left: auto; border-top-right-radius: 0;}
.ai-bubble {background-color: #1e293b; border: 1px solid #334155; border-top-left-radius: 0;}
.copy-btn {font-size: 13px; background-color: #334155; color: #cbd5e1; padding: 4px 8px; border-radius: 6px; border: none; cursor: pointer;}
.copy-btn:hover {background-color: #475569;}
</style>
"""

# --- GEMINI SETUP ---
def setup_gemini_model():
    genai.configure(api_key="AIzaSyBQD0brSlNEnQmdAKbzcxo_cxrjc0-Gc4U")
    if "model" not in st.session_state:
        st.session_state.model = genai.GenerativeModel("gemini-2.0-flash")

# --- FILE HANDLER PER USER ---
def get_user_file():
    username = st.session_state.get("username", "guest").strip().lower().replace(" ", "_")
    return os.path.join(BASE_HISTORY_DIR, f"history_{username}.json")

def save_chat_history(history_list):
    user_file = get_user_file()
    try:
        with open(user_file, "w", encoding="utf-8") as f:
            json.dump(history_list, f, indent=4)
    except Exception as e:
        st.error(f"Gagal menyimpan riwayat: {e}")

def load_chat_history():
    user_file = get_user_file()
    if not os.path.exists(user_file):
        return []
    try:
        with open(user_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# --- PERSONALITIES ---
PERSONALITIES = {
    "Default (Netral dan Informatif)": "Kamu adalah asisten AI profesional yang menjawab dengan jelas dan sopan.",
    "Creative Mode (Ide liar, gaya santai)": "Kamu adalah AI kreatif dan santai yang suka ide liar dan tidak biasa.",
    "Logic Mode (Serius dan detail, fokus debugging)": "Kamu adalah AI yang teliti dan logis seperti insinyur.",
    "Optimizer Mode (Efisiensi & performa)": "Kamu fokus membuat kode efisien dan cepat."
}

def copy_button(text, key):
    safe = json.dumps(text)
    components.html(f"""
        <button class='copy-btn' id='copy-{key}'>📋 Salin</button>
        <script>
        const btn = document.getElementById("copy-{key}");
        btn.onclick = async () => {{
            await navigator.clipboard.writeText({safe});
            btn.textContent = "✅ Disalin";
            setTimeout(() => btn.textContent = "📋 Salin", 2000);
        }}
        </script>
    """, height=30)

# --- CHATBOT ---
def chatbot_interface(model):
    st.markdown(MODERN_CSS, unsafe_allow_html=True)
    st.markdown(f"<h2><img src='{ICONS['chat']}' width='32'/> Ked.AI Chatbot</h2>", unsafe_allow_html=True)

    st.sidebar.markdown(f"<h3><img src='{ICONS['settings']}' width='20'/> Pengaturan</h3>", unsafe_allow_html=True)
    selected_personality = st.sidebar.selectbox("🧠 Kepribadian AI", list(PERSONALITIES.keys()))
    st.sidebar.divider()

    # tampilkan history
    for i, msg in enumerate(st.session_state.history):
        role = msg["role"]
        content = msg["parts"][0].get("text", "")
        if role == "user":
            st.markdown(f"<div class='chat-bubble user-bubble'>{content}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble ai-bubble'>{content}</div>", unsafe_allow_html=True)
            copy_button(content, i)

    uploaded_image = st.file_uploader("🖼️ Upload gambar (opsional):", type=["png", "jpg", "jpeg"])
    img = PIL.Image.open(uploaded_image) if uploaded_image else None
    if img:
        st.image(img, width=250, caption="Gambar diunggah")
    st.session_state["img"] = img

    prompt = st.chat_input("Tulis pesan...")
    if prompt:
        process_chat(model, prompt, selected_personality)

def process_chat(model, prompt, selected_personality):
    personality_prompt = PERSONALITIES[selected_personality]
    st.markdown(f"<div class='chat-bubble user-bubble'>{prompt}</div>", unsafe_allow_html=True)

    try:
        with st.spinner("💡 Sedang berpikir..."):
            img = st.session_state.get("img")
            contents = [f"{personality_prompt}\n\n{prompt}"]
            if img:
                contents.append(img)
            response = model.generate_content(contents)
            answer = response.text

        st.markdown(f"<div class='chat-bubble ai-bubble'>{answer}</div>", unsafe_allow_html=True)
        copy_button(answer, len(st.session_state.history))

        st.session_state.history.append({"role": "user", "parts": [{"text": prompt}]})
        st.session_state.history.append({"role": "model", "parts": [{"text": answer}]})
        save_chat_history(st.session_state.history)

    except GoogleAPIError as e:
        st.error(f"API Error: {e}")
    except Exception as e:
        st.error(f"Error: {e}")

# --- PY ASSIST ---
def py_assist_interface(model):
    st.markdown(MODERN_CSS, unsafe_allow_html=True)
    st.markdown(f"<h2><img src='{ICONS['py']}' width='32'/> Ked.AI Code Assistant</h2>", unsafe_allow_html=True)

    code = st.text_area("Masukkan kode Python:", height=300)
    question = st.text_input("Masalah atau pertanyaan:")
    if st.button("🚀 Analisis Kode"):
        if not code and not question:
            st.warning("Masukkan kode atau pertanyaan terlebih dahulu.")
        else:
            prompt = f"Sebagai ahli Python, bantu analisis kode berikut:\n\n{code}\n\n{question}"
            with st.spinner("🔍 Menganalisis..."):
                try:
                    response = model.generate_content([prompt])
                    st.markdown(f"<div class='chat-bubble ai-bubble'>{response.text}</div>", unsafe_allow_html=True)
                    copy_button(response.text, "py")
                except Exception as e:
                    st.error(f"Error: {e}")

# --- MAIN ---
def main():
    st.set_page_config(page_title="Ked.AI", layout="wide", page_icon=ICONS["app_logo"])
    setup_gemini_model()
    model = st.session_state.model

    st.markdown(f"<h1><img src='{ICONS['app_logo']}' width='56'/> Ked.AI - Smart Assistant</h1>", unsafe_allow_html=True)

    st.sidebar.markdown("### 👤 Masukkan Identitas")
    username = st.sidebar.text_input("Nama / ID Anda:", key="username")
    if not username:
        st.warning("⚠️ Masukkan nama Anda di sidebar untuk memulai.")
        return

    if "history" not in st.session_state:
        st.session_state.history = load_chat_history()

    menu = st.sidebar.radio("🧭 Navigasi", ["Chatbot", "Py Assist"])

    if menu == "Chatbot":
        chatbot_interface(model)
        if st.sidebar.button("🔄 Obrolan Baru"):
            st.session_state.history = []
            save_chat_history([])
            st.rerun()
    else:
        py_assist_interface(model)

if __name__ == "__main__":
    main()
