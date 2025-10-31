import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
import os
import json
import PIL.Image
import requests
import streamlit.components.v1 as components

CHAT_HISTORY_FILE = "chatbot_history.json"

# --- GANTI IKON DI SINI (boleh URL atau file lokal) ---
ICONS = {
    "app_logo": "https://cdn-icons-png.flaticon.com/512/4712/4712027.png",
    "chat": "https://cdn-icons-png.flaticon.com/512/4712/4712043.png",
    "py": "https://cdn-icons-png.flaticon.com/512/5968/5968350.png",
    "settings": "https://cdn-icons-png.flaticon.com/512/2099/2099058.png",
    "upload": "https://cdn-icons-png.flaticon.com/512/1041/1041916.png",
    "reset": "https://cdn-icons-png.flaticon.com/512/1828/1828665.png"
}

# --- CSS MODERN ---
MODERN_CSS = f"""
<style>
body {{
    background-color: #0e1117;
    color: #e2e8f0;
    font-family: 'Segoe UI', sans-serif;
    scroll-behavior: smooth;
}}

[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #1e293b, #0f172a);
    border-right: 1px solid #334155;
}}

.chat-bubble {{
    border-radius: 16px;
    padding: 12px 16px;
    margin: 6px 0;
    max-width: 80%;
    word-wrap: break-word;
    line-height: 1.5;
    transition: all 0.2s ease;
}}
.user-bubble {{
    background-color: #2563eb;
    color: white;
    margin-left: auto;
    border-top-right-radius: 0;
    box-shadow: 0 0 8px rgba(37, 99, 235, 0.4);
}}
.ai-bubble {{
    background-color: #1e293b;
    border: 1px solid #334155;
    border-top-left-radius: 0;
    box-shadow: 0 0 6px rgba(51, 65, 85, 0.3);
}}

.copy-btn {{
    font-size: 13px;
    background-color: #334155;
    color: #cbd5e1;
    padding: 4px 8px;
    border-radius: 6px;
    border: none;
    cursor: pointer;
    transition: all 0.2s ease;
}}
.copy-btn:hover {{
    background-color: #475569;
    transform: scale(1.05);
}}

/* ====== IKON ====== */
.main-logo {{
    width: 56px;
    height: 56px;
    margin-right: 12px;
    vertical-align: middle;
    border-radius: 12px;
    transition: all 0.3s ease;
}}
.icon {{
    width: 32px;
    height: 32px;
    margin-right: 8px;
    vertical-align: middle;
    border-radius: 8px;
    transition: all 0.3s ease;
}}
.sidebar-icon {{
    width: 24px;
    height: 24px;
    margin-right: 6px;
    opacity: 0.95;
    vertical-align: middle;
    transition: all 0.3s ease;
}}

/* ====== EFEK HOVER HIDUP ====== */
.main-logo:hover {{
    transform: scale(1.1) rotate(3deg);
    box-shadow: 0 0 12px rgba(37, 99, 235, 0.5);
}}
.icon:hover {{
    transform: scale(1.15);
    filter: drop-shadow(0 0 6px rgba(96, 165, 250, 0.4));
}}
.sidebar-icon:hover {{
    transform: scale(1.2);
    filter: drop-shadow(0 0 6px rgba(148, 163, 184, 0.4));
}}

h1, h2 {{
    display: flex;
    align-items: center;
    gap: 10px;
}}
</style>
"""


# --- SAVE / LOAD CHAT HISTORY ---


def save_chat_history(history_list):
    try:
        with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_list, f, indent=4)
    except Exception as e:
        st.error(f"Gagal menyimpan riwayat: {e}")


def load_chat_history():
    if not os.path.exists(CHAT_HISTORY_FILE):
        return []
    try:
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# --- GEMINI CLIENT ---


def setup_gemini_client():
    if "client" not in st.session_state:
        st.session_state.client = genai.Client(
            api_key="AIzaSyBQD0brSlNEnQmdAKbzcxo_cxrjc0-Gc4U"
        )


def get_chatbot_session(client):
    if "history" not in st.session_state:
        st.session_state.history = load_chat_history()
    return client.chats.create(
        model="gemini-2.0-flash",
        history=st.session_state.history,
    )


# --- PERSONALITIES ---
PERSONALITIES = {
    "Default (Netral dan Informatif)": (
        "Kamu adalah asisten AI profesional yang menjawab dengan jelas, "
        "ringkas, dan sopan. Gunakan bahasa yang mudah dipahami."
    ),
    "Creative Mode (Ide liar, gaya santai)": (
        "Kamu adalah AI yang kreatif dan santai, suka memberikan ide-ide liar, "
        "unik, bahkan sedikit tidak biasa. Gunakan gaya bahasa santai dan antusias."
    ),
    "Logic Mode (Serius dan detail, fokus debugging)": (
        "Kamu adalah AI yang teliti dan logis seperti insinyur perangkat lunak. "
        "Jawabanmu harus rinci, analitis, dan selalu memberikan alasan di balik solusi."
    ),
    "Optimizer Mode (Efisiensi & performa)": (
        "Kamu adalah AI yang berfokus pada optimasi dan efisiensi. "
        "Selalu cari cara agar kode lebih cepat, lebih ringan, dan hemat sumber daya."
    )
}

# --- COPY BUTTON ---


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

# --- CHATBOT UI ---


def chatbot_interface(client, chat_session):
    st.markdown(MODERN_CSS, unsafe_allow_html=True)

    st.markdown(
        f"<h2><img src='{ICONS['chat']}' class='icon'/> Ked.AI Chatbot</h2>",
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        f"<h3><img src='{ICONS['settings']}' class='sidebar-icon'/> Pengaturan</h3>", unsafe_allow_html=True)

    selected_personality = st.sidebar.selectbox(
        "🧠 Kepribadian AI", list(PERSONALITIES.keys()), key="pers"
    )
    st.sidebar.divider()

    for i, msg in enumerate(st.session_state.history):
        role = msg["role"]
        content = msg["parts"][0].get("text", "")
        if role == "user":
            st.markdown(
                f"<div class='chat-bubble user-bubble'>{content}</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div class='chat-bubble ai-bubble'>{content}</div>", unsafe_allow_html=True)
            copy_button(content, i)

    uploaded_image = st.file_uploader(
        f"🖼️ Upload gambar (opsional):",
        type=["png", "jpg", "jpeg"],
        key="img_up"
    )
    if uploaded_image:
        img = PIL.Image.open(uploaded_image)
        st.image(img, width=250, caption="Gambar yang diunggah",
                 use_container_width=False)
        st.session_state["img"] = img
    else:
        st.session_state["img"] = None

    prompt = st.chat_input("Tulis pesan...")
    if prompt:
        process_chat(client, chat_session, prompt)

# --- PROSES CHAT ---


def process_chat(client, chat_session, prompt):
    selected_personality = st.session_state.get("pers", "Default")
    personality_prompt = PERSONALITIES[selected_personality]

    st.markdown(
        f"<div class='chat-bubble user-bubble'>{prompt}</div>", unsafe_allow_html=True)

    with st.spinner("💡 Sedang berpikir..."):
        try:
            img = st.session_state.get("img")
            if img:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[f"{personality_prompt}\n\n{prompt}", img],
                )
            else:
                response = chat_session.send_message(
                    f"{personality_prompt}\n\n{prompt}")

            answer = response.text
            st.markdown(
                f"<div class='chat-bubble ai-bubble'>{answer}</div>", unsafe_allow_html=True)
            copy_button(answer, len(st.session_state.history))

            st.session_state.history.append(
                {"role": "user", "parts": [{"text": prompt}]})
            st.session_state.history.append(
                {"role": "model", "parts": [{"text": answer}]})
            save_chat_history(st.session_state.history)

        except GoogleAPIError as e:
            st.error(f"API Error: {e}")
        except Exception as e:
            st.error(f"Error: {e}")

# --- PY ASSIST ---


def py_assist_interface(client):
    st.markdown(MODERN_CSS, unsafe_allow_html=True)
    st.markdown(
        f"<h2><img src='{ICONS['py']}' class='icon' style='width:32px;height:32px;'/> Ked.AI Code Assistant</h2>",
        unsafe_allow_html=True
    )

    code = st.text_area("Masukkan kode Python:", height=300)
    question = st.text_input("Masalah atau pertanyaan tentang kode:")

    col1, col2 = st.columns([2, 1])

    with col1:
        if st.button("🚀 Analisis Kode", use_container_width=True):
            if not code and not question:
                st.warning("Masukkan kode atau pertanyaan terlebih dahulu.")
            else:
                prompt = f"Sebagai ahli Python, bantu analisis kode berikut:\n\n{code}\n\n{question}"
                with st.spinner("🔍 Menganalisis..."):
                    try:
                        response = client.models.generate_content(
                            model="gemini-2.0-flash", contents=[prompt]
                        )
                        st.markdown(
                            f"<div class='chat-bubble ai-bubble'>{response.text}</div>",
                            unsafe_allow_html=True,
                        )
                        copy_button(response.text, "py")
                    except Exception as e:
                        st.error(f"Error: {e}")

    with col2:
        if st.button("🧪 Uji Kode di Sandbox", use_container_width=True):
            if not code:
                st.warning("Masukkan kode terlebih dahulu.")
            else:
                st.info("Menjalankan kode di sandbox...")
                try:
                    response = requests.post(
                        "http://127.0.0.1:5001/run",
                        json={"code": code},
                        headers={
                            "Authorization": "Bearer 9da29573101a49f21ec1dccf724430dc7b8cec3ee49e1e67bf8249ef3f80214c"
                        },
                    )
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Hasil eksekusi:")
                        st.code(result.get("output", ""), language="bash")
                    else:
                        st.error(f"❌ Gagal: {response.text}")
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")


# --- MAIN APP ---


def main():
    st.set_page_config(page_title="Py Helper AI",
                       layout="wide", page_icon=ICONS["app_logo"])
    setup_gemini_client()
    client = st.session_state.client

    st.markdown(
        f"<h1><img src='{ICONS['app_logo']}' class='main-logo'/> Ked.AI - Smart Assistant</h1>",
        unsafe_allow_html=True
    )

    menu = st.sidebar.radio("🧭 Navigasi", ["Chatbot", "Py Assist"])

    if "history" not in st.session_state:
        st.session_state.history = load_chat_history()

    if menu == "Chatbot":
        chat_session = get_chatbot_session(client)
        chatbot_interface(client, chat_session)

        if st.sidebar.button("🔄 Obrolan Baru"):
            st.session_state.history = []
            save_chat_history([])
            st.rerun()
    else:
        py_assist_interface(client)


if __name__ == "__main__":
    main()
