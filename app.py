import streamlit as st
import os
import requests

# ----------------------------------
# PAGE SETTINGS
# ----------------------------------
st.set_page_config(
    page_title="Tamil Astrology AI 🔮",
    page_icon="🔮",
    layout="centered"
)

st.title("🔮 Tamil Astrology AI Chatbot")

# ----------------------------------
# LOAD GROQ API KEY
# ----------------------------------
if "GROQ_API_KEY" not in st.secrets:
    st.error("GROQ_API_KEY not found in Secrets.")
    st.stop()

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

API_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

# ----------------------------------
# LOAD TAMIL TEXT FILES
# ----------------------------------
@st.cache_resource
def load_txt_files():
    full_text = ""
    folder = "data"

    if not os.path.exists(folder):
        return ""

    for file in os.listdir(folder):
        if file.endswith(".txt"):
            with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
                full_text += f.read() + "\n"

    return full_text

ASTRO_CONTEXT = load_txt_files()

# ----------------------------------
# SESSION MEMORY
# ----------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------------
# QUERY MODEL FUNCTION
# ----------------------------------
def query_model(user_question):

    messages = [
        {
            "role": "system",
            "content": f"""
நீங்கள் ஒரு அனுபவமுள்ள தமிழ் ஜோதிட நிபுணர்.

கீழே கொடுக்கப்பட்டுள்ள ஜோதிட தகவலை பயன்படுத்தி பதிலளிக்கவும்.
பதில் தமிழில் மட்டும் இருக்க வேண்டும்.

ஜோதிட தகவல்:
{ASTRO_CONTEXT[:8000]}
"""
        },
        {
            "role": "user",
            "content": user_question
        }
    ]

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.7
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code != 200:
        return f"API Error {response.status_code}: {response.text}"

    return response.json()["choices"][0]["message"]["content"]

# ----------------------------------
# DISPLAY CHAT HISTORY
# ----------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------------------------
# USER INPUT
# ----------------------------------
if question := st.chat_input("ஜோதிட கேள்வியை கேளுங்கள்..."):

    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        with st.spinner("ஜோதிடத்தை பார்க்கிறேன்... 🔮"):
            reply = query_model(question)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})