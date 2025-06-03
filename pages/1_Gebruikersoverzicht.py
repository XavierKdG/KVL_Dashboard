import streamlit as st
import pandas as pd
from api.models import get_models
from api.users import get_users, get_user_by_id
from api.groups import get_groups, create_group, add_user_to_group, update_group, delete_group, remove_user_from_group
from auth import require_login

require_login()
st.logo("assets/KVL logo.png", size='large')

with st.spinner("Gebruikers ophalen..."):
    gebruikers = get_users()

st.title("👥 Gebruikers- en Groepsbeheer")

tab1, tab2, tab3 = st.tabs(["Gebruikers", "Groepen", "Groepsbeheer"])

with tab1:
    st.header("📄 Gebruikersoverzicht")

    with st.spinner("Gebruikers ophalen..."):
        gebruikers = get_users()

    if gebruikers:
        for gebruiker in gebruikers:
            with st.container():
                st.markdown("---")
                cols = st.columns([1, 6])

                with cols[0]:
                    profiel_url = gebruiker.get("Profielafbeelding")
                    if profiel_url and profiel_url.startswith("data:image"):
                        st.image(profiel_url, width=64)
                    else:
                        st.markdown(
                            """
                            <div style='
                                width:64px;
                                height:64px;
                                border-radius:50%;
                                background:#ccc;
                                display:flex;
                                align-items:center;
                                justify-content:center;
                                font-size:28px;
                                color:#fff;
                            '>?</div>
                            """,
                            unsafe_allow_html=True
                        )

                with cols[1]:
                    naam = gebruiker.get("Naam", "Onbekend")
                    st.markdown(f"**Naam:** {naam}")
                    st.markdown(f"**Email:** {gebruiker.get('Email', '-')}")
                    st.markdown(f"**Rol:** {gebruiker.get('Rol', '-')}")
                    st.markdown(f"**ID:** `{gebruiker.get('id', '-')}`")
                    st.markdown(f"**Laatst actief:** {gebruiker.get('Laatst actief', '-')}")

                settings = gebruiker.get("Instellingen", {})
                if settings:
                    with st.expander("⚙️ Instellingen"):
                        st.json(settings)
    else:
        st.warning("Geen gebruikers gevonden.")

with tab2:
    st.header("📂 Groepen")
    with st.spinner("Groepen ophalen..."):
        groepen = get_groups()

    if groepen:
        for groep in groepen:
            with st.expander(f"{groep['name']}"):
                st.markdown(f"**📋 Beschrijving:** {groep.get('description', '-')}")
                st.divider()

                permissions = groep.get("permissions", {})
                if permissions:
                    for hoofdkey, subvalue in permissions.items():
                        st.markdown(f"**🔧 {hoofdkey} permissies:**")
                        
                        if isinstance(subvalue, dict):
                            for subkey, bool_val in subvalue.items():
                                checkbox_key = f"{groep['id']}_{hoofdkey}_{subkey}"
                                st.checkbox(
                                    label=subkey,
                                    value=bool(bool_val),
                                    disabled=True,
                                    key=checkbox_key
                                )
                        else:
                            checkbox_key = f"{groep['id']}_{hoofdkey}"
                            st.checkbox(
                                label=hoofdkey,
                                value=bool(subvalue),
                                disabled=True,
                                key=checkbox_key
                            )
                else:
                    st.info("Geen permissies ingesteld voor deze groep.")
    else:
        st.warning("Geen groepen gevonden.")


with tab3:
    st.header("🔧 Gebruikers aan groepen koppelen")
    gebruikers = get_users()
    groepen = get_groups()

    if not gebruikers or not groepen:
        st.error("Geen gebruikers of groepen beschikbaar.")
    else:
        niet_admins = [u for u in gebruikers if u.get("Rol") != "admin"]
        admins = [u["Naam"] for u in gebruikers if u.get("Rol") == "admin"]

        if not niet_admins:
            st.warning("Er zijn alleen beheerdersaccounts. Geen gebruikers beschikbaar om toe te voegen aan groepen.")
        else:
            user_map = {u["Naam"]: u["id"] for u in niet_admins}
            group_map = {g["name"]: g["id"] for g in groepen}

            selected_user = st.selectbox("Selecteer gebruiker", options=list(user_map.keys()))
            selected_group = st.selectbox("Selecteer groep", options=list(group_map.keys()))

            col1, col2 = st.columns(2)

            with col1:
                if st.button("➕ Toevoegen aan groep"):
                    result = add_user_to_group(group_map[selected_group], user_map[selected_user])
                    if result:
                        st.success("Gebruiker toegevoegd aan groep.")
                    else:
                        st.error("Toevoegen mislukt.")

            with col2:
                if st.button("➖ Verwijderen uit groep"):
                    result = remove_user_from_group(group_map[selected_group], user_map[selected_user])
                    if result:
                        st.success("Gebruiker verwijderd uit groep.")
                    else:
                        st.error("Verwijderen mislukt.")

            if admins:
                with st.expander("ℹ️ Beheerders uitgesloten"):
                    st.info("De volgende beheerders zijn uitgesloten van groepsbeheer:")
                    st.write(", ".join(admins))
