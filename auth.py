import streamlit as st

def require_login():
    with st.sidebar:
        if st.user.get("is_logged_in", False):
            st.write(f"👤 Ingelogd als: `{st.user.get('email', 'Onbekend')}`")
            if st.button("🔓 Uitloggen"):
                st.logout()
        else:
            st.info("🔐 Je bent nog niet ingelogd.")

    if not st.user.get("is_logged_in", False):
        st.title("🔐 Secure App with Google Login")
        if st.button("Inloggen met Google"):
            st.login("google")
        st.stop()
        