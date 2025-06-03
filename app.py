# Om dashboard te runnen --> python -m streamlit run app.py
# dashboard runt op http://localhost:8501/

import streamlit as st
import pandas as pd
import plotly.express as px
from auth import require_login
from api import (
    get_users,
    get_groups,
    get_models,
    get_knowledge,
    get_channels,
    get_chat_usage_summary,
    get_feedback_summary,
)

st.set_page_config(page_title="KVL Dashboard", layout="wide", page_icon="assets/KVL logo.png")

require_login()

# Probeer de basisgegevens op te halen. Bij fouten blijft de pagina werken.
users = []
groups = []
models = []
knowledge = []
channels = []
chat_summary = pd.DataFrame()
feedback_summary = pd.DataFrame()

with st.spinner("Data ophalen..."):
    try:
        users = get_users()
    except Exception:
        st.warning("Kon gebruikers niet ophalen.")
    try:
        groups = get_groups()
    except Exception:
        st.warning("Kon groepen niet ophalen.")
    try:
        models = get_models()
    except Exception:
        st.warning("Kon modellen niet ophalen.")
    try:
        knowledge = get_knowledge()
    except Exception:
        st.warning("Kon kennisbanken niet ophalen.")
    try:
        channels = get_channels()
    except Exception:
        st.warning("Kon kanalen niet ophalen.")
    try:
        chat_summary = get_chat_usage_summary()
    except Exception:
        st.warning("Kon chat-statistieken niet ophalen.")
    try:
        feedback_summary = get_feedback_summary()
    except Exception:
        st.warning("Kon feedback niet ophalen.")

st.image('assets/KVL logo.png', width=150)
st.title("Welkom op het KVL Dashboard van OpenWebUI")
st.logo("assets/KVL logo.png", size='large')

# Toon kerncijfers
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Gebruikers", len(users))
col2.metric("Groepen", len(groups))
col3.metric("Kennisbanken", len(knowledge))
col4.metric("Modellen", len(models))
col5.metric("Kanalen", len(channels))

# Extra metrics
total_chats = int(chat_summary["Aantal chats"].sum()) if not chat_summary.empty else 0
feedback_count = 0
avg_rating = None
if not feedback_summary.empty:
    rating_cols = [c for c in ["👍", "👎", "⚪️"] if c in feedback_summary.columns]
    if rating_cols:
        feedback_count = int(feedback_summary[rating_cols].sum().sum())
    avg_rating = feedback_summary["Gemiddelde beoordeling"].mean()

col6, col7, col8 = st.columns(3)
col6.metric("Chats", total_chats)
col7.metric("Feedback", feedback_count)
if avg_rating is not None:
    col8.metric("Gemiddelde rating", f"{avg_rating:.1f}")
else:
    col8.metric("Gemiddelde rating", "-")

# Optioneel overzicht van recente updates en inzichten
with st.expander("Recente updates en inzichten"):
    if models:
        st.subheader("Laatste modellen")
        model_df = pd.DataFrame(models)
        cols = [c for c in model_df.columns if c not in ["image", "metadata"]]
        st.table(model_df[cols].head())
    if channels:
        st.subheader("Laatste kanalen")
        st.table(pd.DataFrame(channels).head())
    if not chat_summary.empty:
        st.subheader("Chat gebruik per model")
        fig = px.bar(chat_summary, x="model", y="Aantal chats")
        st.plotly_chart(fig, use_container_width=True)
    if not feedback_summary.empty:
        st.subheader("Feedback overzicht")
        st.table(feedback_summary.head())

st.markdown("""
👈 Gebruik de zijbalk om te navigeren naar

- Gebruikersoverzicht
- Gesprekskanalen & berichten  
- Modellen & LLM-gebruik (Ollama / OpenAI)  
- Bestanden & kennis  
- Dashboardcomponenten (metrics & logging)  

""")
