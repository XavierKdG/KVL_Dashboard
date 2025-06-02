# Om dashboard te runnen --> python -m streamlit run app.py
# dashboard runt op http://localhost:8501/

import streamlit as st
from auth import require_login

st.set_page_config(page_title="KVL Dashboard", layout="wide", page_icon="assets/KVL logo.png")

require_login()

st.image('assets/KVL logo.png', width=150)
st.title("Welkom op het KVL Dashboard van OpenWebUI")
st.logo("assets/KVL logo.png", size='large')

st.markdown("""
👈 Gebruik de zijbalk om te navigeren naar

- Gebruikersoverzicht
- Gesprekskanalen & berichten  
- Modellen & LLM-gebruik (Ollama / OpenAI)  
- Bestanden & kennis  
- Dashboardcomponenten (metrics & logging)  

""")


