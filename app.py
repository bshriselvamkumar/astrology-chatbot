import streamlit as st
import os
import requests

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="Tamil Astrology AI 🔮",
    page_icon="🔮",
    layout="centered"
)

st.title("🔮 Tamil Astrology AI Chatbot")

# ----------------------------------
# LOAD HF TOKEN
# ----------------------------------
if "HF_TOKEN" not in st.secrets:
    st.error("HF_TOKEN not found in Streamlit Secrets.")
    st.stop()

HF_TOKEN = st.secrets["HF_TOKEN"]

API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

# ----------------------------------
# LOAD TAMIL TXT FILES
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

if not ASTRO_CONTEXT:
    st.warning("No astrology data found in data/ folder.")

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
நீங்கள் ஒரு அனுபவம் வாய்ந்த தமிழ் ஜோதிட நிபுணர்.

கீழே கொடுக்கப்பட்டுள்ள ஜோதிட அறிவைப் பயன்படுத்தி பதிலளிக்கவும்.

ஜோதிட அறிவு:
{ASTRO_CONTEXT[:12000]}

பயனர் கேள்வி:
{user_question}

பதில் தமிழில் மட்டும் இருக்க வேண்டும்.
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.7
        }
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)

    # Show real error if something fails
    if response.status_code != 200:
        return f"API Error {response.status_code}: {response.text}"

    result = response.json()

    if isinstance(result, list) and "generated_text" in result[0]:
        return result[0]["generated_text"]
    else:
        return str(result)

# ----------------------------------
# DISPLAY CHAT HISTORY
# ----------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------------------------
# CHAT INPUT
# ----------------------------------
if question := st.chat_input("ஜோதிட கேள்வியை கேளுங்கள்..."):

    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        with st.spinner("ஜோதிடத்தை பார்க்கிறேன்... 🔮"):
            reply = query_model(question)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})