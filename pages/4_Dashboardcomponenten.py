import streamlit as st
import pandas as pd
import plotly.express as px

from auth import require_login
from api.users import get_users
from api.groups import get_groups
from api.models import get_models
from api.chats import get_all_chats
from api.channels import get_channels
from api.knowledge import get_knowledge

require_login()

st.logo("assets/KVL logo.png", size="large")
st.title("Dashboardcomponenten")

with st.spinner("Gegevens laden..."):
    users = get_users()
    groups = get_groups()
    models = get_models()
    chats = get_all_chats()
    channels = get_channels()
    knowledge = get_knowledge()
    
tab_overview, tab_users, tab_activity = st.tabs([
    "📊 Overzicht",
    "👥 Gebruikers",
    "💬 Chatactiviteit",
])

with tab_overview:
    st.subheader("Algemeen overzicht")
    col1, col2, col3 = st.columns(3)
    col1.metric("Gebruikers", len(users))
    col2.metric("Groepen", len(groups))
    col3.metric("Modellen", len(models))

    col4, col5, col6 = st.columns(3)
    col4.metric("Chats", len(chats))
    col5.metric("Kanalen", len(channels))
    col6.metric("Kennisbanken", len(knowledge))

with tab_users:
    st.subheader("Verdeling van rollen")
    if users:
        df_users = pd.DataFrame(users)
        role_counts = df_users["Rol"].value_counts().reset_index()
        role_counts.columns = ["Rol", "Aantal"]
        fig = px.pie(role_counts, names="Rol", values="Aantal", title="Gebruikersrollen")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(role_counts, use_container_width=True)
    else:
        st.info("Geen gebruikers gevonden.")

with tab_activity:
    st.subheader("Chatactiviteit per dag")
    if chats:
        df_chats = pd.DataFrame(chats)
        df_chats["datum"] = pd.to_datetime(df_chats["created_at"], errors="coerce").dt.date
        counts = df_chats.groupby("datum").size().reset_index(name="Aantal chats")
        fig = px.line(counts, x="datum", y="Aantal chats", markers=True)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(counts, use_container_width=True)
    else:
        st.info("Geen chatdata beschikbaar.")