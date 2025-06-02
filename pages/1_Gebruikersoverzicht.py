import streamlit as st
import pandas as pd
from api.models import get_models
from auth import require_login

require_login()

st.logo("assets/KVL logo.png", size='large')