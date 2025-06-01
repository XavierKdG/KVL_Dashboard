# Om dashboard te runnen --> python -m streamlit run dashboard.py
# dashboard runt op http://localhost:8501/

import streamlit as st
from api import get_channels, get_messages, get_models
import pandas as pd

st.set_page_config(page_title="KVL Dashboard", layout="wide", page_icon="images_dashboard/KVL logo.png")
st.image('images_dashboard/KVL logo.png', width=150)
st.title("KVL Dashboard test")

with st.spinner("Data ophalen van API"):
    channels = get_channels()
    channel_messages = get_messages("d968f28b-26e4-40c5-aea9-558c964b01d9")
    models = get_models()

# channels
st.subheader("channels")
df = pd.DataFrame(channels)
st.dataframe(df)

# channel_messages
st.subheader("channel_messages")
df = pd.DataFrame(channel_messages)
st.dataframe(df)

# models
st.subheader("get_models")
df = pd.DataFrame(models)
st.dataframe(df)