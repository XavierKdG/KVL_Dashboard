import streamlit as st
import pandas as pd
from api.models import get_models, get_basemodels
from auth import require_login

require_login()
st.logo("assets/KVL logo.png", size='large')
st.title("Modellen & LLM-gebruik")

with st.spinner("Modellen ophalen..."):
    models = get_models()
    basemodels = get_basemodels()

st.subheader("Beschikbare Modellen")
st.dataframe(pd.DataFrame(models))

st.subheader("Beschikbare Basemodellen")
st.dataframe(pd.DataFrame(basemodels))
