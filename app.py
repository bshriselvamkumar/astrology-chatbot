import streamlit as st
import requests
from pypdf import PdfReader
import io

# --------------------------------
# HuggingFace Setup
# --------------------------------
HF_TOKEN = st.secrets["HF_TOKEN"]
API_URL = "https://api-inference.huggingface.co/models/google/gemma-2b-it"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

# --------------------------------
# Google Drive PDF Links
# --------------------------------
PDF_FILE_IDS = [
    "1LZkVjL6ghdvuYQYv7CM5X6C8fZAf5mmh"
    "1yMoHx6VxFBDr35CddAwLwO-OwqxZ9XYL",
    "1CajuOnAU84Bmux3WwxOzglgPjHCS2mPz",
    "1sBZh-MnKdfAGfkslKzQhtFhnvqFj13Ql",
    "1ozbS3fSPE0YKt8TBFMFt8_VS7KSuaZY3",
    "1RblLhcnrBQMqViO4HBk3LiJwqwlLMBM0",
    "1EISFdqJ9IHfwzpd3TpV0PrWNa1_xoCI4",
    "1BgA-Ri3XbJq8aHFf_WtNiwXLdLxbdk3u",
    "1-jdxtHtehK0dJc9oRkLiGTHjCImRqM_9",
    "1Gr9urGIor2PvkT181el9DD1GcxcU9SWd",
    "16K6uGdWni7FnFaNp2QGiLxZptv2E7spS",
    "1hgD-ZwnK9GsZV8HrBRUHswSWakX7exsa",
    "1U-l-xZ91cd5bRQWBgSiBlhdhUDmeGurh",
    "1nDGaqxHYe-za-ac0ekrISl8dYv4h1KtE",
    "18JGELKlqhzvvYvZ7sr18grpMjPpibOY0",
    "1g3vExomZsgmRwrjMzUZTBvhbQ3mCvlRZ",
    "1IvI_yJxlLRIB6Ngz10Zc5ByUWqN6VX-P",
    "1czLZwwP5VvathPJI__F_BpoBiK-XiTT8",
    "14BGnmEqUIr_3spRfuNau-yIWA3LXsEBt",
    "1l9LXrJcle9n6PMCpbx2hcg4G_aO0cfid",
    "1I8voiZLCSOWgT-YaQ-6AIGJq1gak5cJy"


]

@st.cache_resource
def load_drive_pdfs():
    full_text = ""

    for file_id in PDF_FILE_IDS:
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(download_url)

        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)

        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    return full_text


ASTRO_CONTEXT = load_drive_pdfs()

# --------------------------------
# Chat UI
# --------------------------------
st.title("🔮 Tamil Astrology AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

def query_model(question):
    prompt = f"""
You are a Tamil astrology expert.

Use this knowledge:
{ASTRO_CONTEXT}

Question:
{question}
"""

    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 400}
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.json()[0]["generated_text"]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Ask astrology question..."):
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        with st.spinner("Consulting stars..."):
            reply = query_model(question)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})