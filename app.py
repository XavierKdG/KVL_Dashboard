# Om dashboard te runnen --> python -m streamlit run app.py
# dashboard runt op http://localhost:8501/

import streamlit as st
st.set_page_config(page_title="KVL Dashboard", layout="wide", page_icon="assets/KVL logo.png")

st.title("🔐 Secure App with Google Login")

if not st.user.is_logged_in:
    st.info("Je bent nog niet ingelogd.")
    if st.button("Log in met Google"):
        st.login()  
else:
    st.success(f"Welkom {st.user.name} ({st.user.email})!")
    if st.button("Log uit"):
        st.logout()

st.image('assets/KVL logo.png', width=150)
st.title("Welkom op het KVL Dashboard van OpenWebUI")

st.logo("assets/KVL logo.png", size='large')

st.markdown("""
👈 Gebruik de zijbalk om te navigeren naar:

- Gesprekskanalen & berichten  
- Modellen & LLM-gebruik (Ollama / OpenAI)  
- Bestanden & kennis  
- Dashboardcomponenten (metrics & logging)  
- Gebruikersoverzicht
""")


