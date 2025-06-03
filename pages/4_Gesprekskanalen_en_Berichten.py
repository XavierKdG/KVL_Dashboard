import streamlit as st
import pandas as pd
import plotly.express as px

from auth import require_login
from api.channels import get_channels, get_messages
from api.chats import get_all_chats

require_login()

st.logo("static/KVL logo.png", size="large")
st.title("Gesprekskanalen & Berichten")

with st.spinner("Data ophalen..."):
    channels = get_channels()
    chats = get_all_chats()

if not channels:
    st.warning("Geen kanalen gevonden.")
    st.stop()

channels_df = pd.DataFrame(channels)

if "id" not in channels_df.columns:
    st.error("Kanaal-ID ontbreekt in de opgehaalde data")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs([
    "📂 Kanalen",
    "💬 Berichten",
    "📈 Berichtenactiviteit",
    "💬 Chatactiviteit",
])

with tab1:
    st.subheader("Overzicht van kanalen")
    st.dataframe(channels_df[["id", "channel naam", "laatst bijgewerkt"]], use_container_width=True)

with tab2:
    st.subheader("Berichten per kanaal")
    channel_names = channels_df["channel naam"].tolist()
    selected = st.selectbox("Kies een kanaal", channel_names)
    row = channels_df.loc[channels_df["channel naam"] == selected]
    if row.empty:
        st.info("Kanaal niet gevonden.")
        msgs = []
    else:
        channel_id = row["id"].iloc[0]
        st.write(f"Kanaal-ID: {channel_id}")
        with st.spinner("Berichten laden..."):
            msgs = get_messages(channel_id)
    if msgs:
        df_msgs = pd.DataFrame(msgs)
        df_msgs["datum"] = pd.to_datetime(df_msgs["laatst bijgewerkt"], errors="coerce")
        st.dataframe(df_msgs[["datum", "content"]], use_container_width=True)
    else:
        st.info("Geen berichten gevonden voor dit kanaal.")

with tab3:
    st.subheader("Berichtenactiviteit")
    all_counts = []
    with st.spinner("Activiteit berekenen..."):
        for _, row in channels_df.iterrows():
            msgs = get_messages(row["id"])
            df = pd.DataFrame(msgs)
            if df.empty:
                continue
            df["datum"] = pd.to_datetime(df["laatst bijgewerkt"], errors="coerce").dt.date
            counts = df.groupby("datum").size().reset_index(name="aantal")
            counts["kanaal"] = row["channel naam"]
            all_counts.append(counts)
    if all_counts:
        activity_df = pd.concat(all_counts)
        fig = px.line(activity_df, x="datum", y="aantal", color="kanaal", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Geen berichtenactiviteit beschikbaar.")

with tab4:
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