import streamlit as st
import pandas as pd
from api.models import get_models
from api.users import get_users
from auth import require_login

require_login()
st.logo("assets/KVL logo.png", size='large')
st.title("Gebruikersoverzicht")

with st.spinner("Gebruikers ophalen..."):
    gebruikers = get_users()

st.subheader("Bestaande gebruikers: ")
st.dataframe(pd.DataFrame(gebruikers))