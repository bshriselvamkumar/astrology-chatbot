import streamlit as st
import os
import requests

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(page_title="Tamil Astrology AI 🔮", page_icon="🔮")

st.title("🔮 Tamil Astrology AI Chatbot")

# ----------------------------------
# LOAD HF TOKEN
# ----------------------------------
if "HF_TOKEN" not in st.secrets:
    st.error("HF_TOKEN not found in Streamlit Secrets.")
    st.stop()

HF_TOKEN = st.secrets["HF_TOKEN"]

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

# ----------------------------------
# LOAD TXT KNOWLEDGE
# ----------------------------------
@st.cache_resource
def load_txt_files():
    full_text = ""
    folder = "data"

    for file in os.listdir(folder):
        if file.endswith(".txt"):
            with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
                full_text += f.read() + "\n"

    return full_text

ASTRO_CONTEXT = load_txt_files()

# ----------------------------------
# CHAT MEMORY
# ----------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------------
# MODEL FUNCTION
# ----------------------------------
def query_model(user_question):

    prompt = f"""
You are a professional Tamil astrology expert.

Use the astrology knowledge below to answer clearly.

Knowledge:
{ASTRO_CONTEXT[:15000]}

Question:
{user_question}
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.7,
            "return_full_text": False
        }
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code != 200:
        return "Model unavailable. Try again."

    return response.json()[0]["generated_text"]

# ----------------------------------
# DISPLAY CHAT
# ----------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Ask astrology question..."):

    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        with st.spinner("Consulting the stars ✨"):
            reply = query_model(question)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})