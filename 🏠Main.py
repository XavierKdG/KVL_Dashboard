# Om dashboard te runnen --> python -m streamlit run app.py
# dashboard runt op http://localhost:8501/

import streamlit as st
import pandas as pd
import plotly.express as px
from textwrap import shorten
from datetime import datetime, timedelta
from auth import require_login
from api import (
    get_users,
    get_groups,
    get_models,
    get_knowledge,
    get_channels,
    get_chat_usage_summary,
    get_feedback_summary,
    get_all_chats,
    get_feedback,
)

def count_recent(items, keys):
    """Tel hoeveel items in de afgelopen week zijn toegevoegd of bijgewerkt."""
    if not isinstance(keys, (list, tuple)):
        keys = [keys]
    week_ago = pd.Timestamp.now() - pd.Timedelta(days=7)
    count = 0
    for item in items:
        for key in keys:
            ts = pd.to_datetime(item.get(key), errors="coerce")
            if pd.notna(ts):
                if ts >= week_ago:
                    count += 1
                break
    return count

st.set_page_config(page_title="KVL Dashboard", layout="wide", page_icon="static/KVL logo.png")
st.logo('static/KVL logo.png')
require_login()

users = []
groups = []
models = []
knowledge = []
channels = []
all_chats = []
feedback_all = []
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
        all_chats = get_all_chats()
    except Exception:
        st.warning("Kon chats niet ophalen.")
    try:
        feedback_summary = get_feedback_summary()
    except Exception:
        st.warning("Kon feedback niet ophalen.")
    try:
        feedback_all = get_feedback()
    except Exception:
        st.warning("Kon feedback niet ophalen.")

delta_users = count_recent(users, ["Geüpload op", "Bijgewerkt op"])
delta_groups = count_recent(groups, ["created_at", "updated_at"])
delta_knowledge = count_recent(knowledge, ["created_at", "updated_at"])
delta_models = count_recent(models, ["datum aangemaakt", "laatst bijgewerkt"])
delta_channels = count_recent(channels, ["created_at", "laatst bijgewerkt"])
delta_chats = count_recent(all_chats, "created_at")
delta_feedback = count_recent(feedback_all, "datum")

st.markdown(
    "<h1 style='text-align:center;'>📊 KVL Dashboard</h1>", unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center;'>Inzicht in gebruikers, kennisdeling, modellen en interactie</p>",
    unsafe_allow_html=True,
)

row1 = st.columns(4)
row1[0].metric("👥 Gebruikers", len(users), delta_users)
row1[1].metric("👤 Groepen", len(groups), delta_groups)
row1[2].metric("📚 Kennisbanken", len(knowledge), delta_knowledge)
row1[3].metric("💬 Kanalen", len(channels), delta_channels)

total_chats = int(chat_summary["Aantal chats"].sum()) if not chat_summary.empty else 0
feedback_count = 0
delta_rating = None
avg_rating = None
if not feedback_summary.empty:
    rating_cols = [c for c in ["👍", "👎", "⚪️"] if c in feedback_summary.columns]
    if rating_cols:
        feedback_count = int(feedback_summary[rating_cols].sum().sum())
    avg_rating = feedback_summary["Gemiddelde beoordeling"].mean()

if feedback_all and avg_rating is not None:
    week_ago = pd.Timestamp.now() - pd.Timedelta(days=7)
    recent_scores = []
    for fb in feedback_all:
        ts = pd.to_datetime(fb.get("datum"), errors="coerce")
        if pd.notna(ts) and ts >= week_ago:
            score = fb.get("score")
            if score is not None:
                try:
                    recent_scores.append(float(score))
                except Exception:
                    pass
    if recent_scores:
        delta_rating = sum(recent_scores) / len(recent_scores) - avg_rating

row2 = st.columns(4)
row2[0].metric("🧠 Modellen", len(models), delta_models)
row2[1].metric("💡 Chats", total_chats, delta_chats)
row2[2].metric("👍 Feedback", feedback_count, delta_feedback)
if avg_rating is not None:
    row2[3].metric("⭐ Gem. beoordeling", f"{avg_rating:.1f}", f"{delta_rating:.2f}")
else:
    row2[3].metric("⭐ Gem. beoordeling", "-")

st.header("🔄 Recente activiteit")
if models:
    st.subheader("📌 Nieuwste modellen")
    model_df = pd.DataFrame(models)
    column_config = {}
    if "beschrijving" in model_df.columns:
        column_config["beschrijving"] = st.column_config.TextColumn(
            "beschrijving", width="medium"
        )
    if "laatst bijgewerkt" in model_df.columns:
        model_df["laatst bijgewerkt"] = pd.to_datetime(
            model_df["laatst bijgewerkt"], errors="coerce"
        )
        model_df = model_df.sort_values("laatst bijgewerkt", ascending=False)
    cols = [c for c in model_df.columns if c not in ["image", "metadata"]]
    st.dataframe(
        model_df[cols].head(),
        use_container_width=True,
        column_config=column_config,
    )

if channels:
    st.subheader("📢 Nieuwste kanalen")
    channels_df = pd.DataFrame(channels)
    if "laatst bijgewerkt" in channels_df.columns:
        channels_df["laatst bijgewerkt"] = pd.to_datetime(
            channels_df["laatst bijgewerkt"], errors="coerce"
        )
        channels_df = channels_df.sort_values("laatst bijgewerkt", ascending=False)
    st.dataframe(channels_df.head(), use_container_width=True)

if not chat_summary.empty:
    st.subheader("📈 Chatgebruik per model")
    kleuren = ["#EEA400", "#36a9e1", "#3AAA35", "#00A79F"]
    fig = px.bar(chat_summary, x="model", y="Aantal chats", color="model",
                 color_discrete_sequence=kleuren)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
if not feedback_summary.empty:
    st.subheader("📝 Feedbackoverzicht")
    st.dataframe(feedback_summary.head(), use_container_width=True)

st.markdown("""
👈 **Navigeer via de zijbalk:**

- 👥 Gebruikersoverzicht  
- 📂 Bestanden & kennis  
- 🤖 Modellen & LLM-gebruik  
- 💬 Gesprekskanalen & berichten
""")
