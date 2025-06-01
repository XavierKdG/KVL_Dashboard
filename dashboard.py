# Om dashboard te runnen --> streamlit run dashboard.py

import streamlit as st
from api import get_channels
import pandas as pd

st.set_page_config(page_title="KVL Dashboard", layout="wide")
st.title("KVL Dashboard test")

