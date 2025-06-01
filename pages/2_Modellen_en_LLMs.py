import streamlit as st
import pandas as pd
from api.openwebui import get_models

st.title("Modellen & LLM-gebruik")

with st.spinner("Modellen ophalen..."):
    models = get_models()

st.subheader("Beschikbare Modellen")
st.dataframe(pd.DataFrame(models))
