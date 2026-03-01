import streamlit as st
import requests
import io
from pypdf import PdfReader

# -----------------------------------------
# PAGE CONFIG
# -----------------------------------------
st.set_page_config(
    page_title="Tamil Astrology AI 🔮",
    page_icon="🔮",
    layout="centered"
)

st.title("🔮 Tamil Astrology AI Chatbot")
st.caption("Ask your astrology questions in Tamil or English")

# -----------------------------------------
# LOAD HF TOKEN
# -----------------------------------------
if "HF_TOKEN" not in st.secrets:
    st.error("HF_TOKEN not found in Streamlit Secrets.")
    st.stop()

HF_TOKEN = st.secrets["HF_TOKEN"]

API_URL = "https://api-inference.huggingface.co/models/google/gemma-2b-it"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

# -----------------------------------------
# YOUR GOOGLE DRIVE FILE IDs
# -----------------------------------------
PDF_FILE_IDS = [
    # Paste your IDs here
]

# -----------------------------------------
# SAFE PDF LOADER
# -----------------------------------------
@st.cache_resource(show_spinner=True)
def load_drive_pdfs():
    full_text = ""

    for file_id in PDF_FILE_IDS:
        try:
            download_url = f"https://drive.google.com/uc?id={file_id}&export=download"
            response = requests.get(download_url, timeout=60)

            # Check if correct PDF content
            if response.status_code == 200 and "application/pdf" in response.headers.get("Content-Type", ""):
                pdf_file = io.BytesIO(response.content)
                reader = PdfReader(pdf_file)

                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"

            else:
                st.warning(f"Skipping file {file_id} (not a valid PDF response)")

        except Exception as e:
            st.warning(f"Error loading file {file_id}, skipping.")

    return full_text


# -----------------------------------------
# LOAD KNOWLEDGE BASE
# -----------------------------------------
with st.spinner("Loading astrology knowledge... 🌟"):
    ASTRO_CONTEXT = load_drive_pdfs()

if not ASTRO_CONTEXT:
    st.error("No astrology knowledge loaded. Check Google Drive permissions.")
    st.stop()

# -----------------------------------------
# CHAT MEMORY
# -----------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------------
# MODEL QUERY FUNCTION
# -----------------------------------------
def query_model(user_question):

    prompt = f"""
You are a professional Tamil astrology expert.

Use the astrology knowledge below to answer accurately and clearly.

Astrology Knowledge:
{ASTRO_CONTEXT[:15000]}

User Question:
{user_question}

Give a detailed astrology-based answer.
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.7,
            "return_full_text": False
        }
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)

        if response.status_code != 200:
            return "Model is loading or unavailable. Please try again."

        result = response.json()
        return result[0]["generated_text"]

    except:
        return "Error communicating with model."


# -----------------------------------------
# DISPLAY CHAT HISTORY
# -----------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------------------
# CHAT INPUT
# -----------------------------------------
if question := st.chat_input("Ask your astrology question..."):

    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        with st.spinner("Consulting the stars... ✨"):
            reply = query_model(question)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
