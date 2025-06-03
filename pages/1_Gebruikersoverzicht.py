import streamlit as st
import pandas as pd
import datetime
from api.config import tijd_verschil_als_tekst
from api.models import get_models
from api.users import get_users, get_user_by_id
from api.groups import get_groups, create_group, add_user_to_group, update_group, delete_group, remove_user_from_group, get_group_by_id
from auth import require_login

require_login()
st.logo("assets/KVL logo.png", size='large')

with st.spinner("Data ophalen..."):
    gebruikers = get_users()
    groepen = get_groups()

st.title("👥 Gebruikers- en Groepsbeheer")

tab1, tab2, tab3 = st.tabs(["Gebruikers", "Groepen", "Groepsbeheer"])

with tab1:
    st.header("📄 Gebruikersoverzicht")

    if gebruikers:
        alle_rollen = sorted(set(g.get("Rol", "Onbekend") for g in gebruikers))
        gekozen_rol = st.multiselect("Filter op rol", options=alle_rollen, default=alle_rollen)

        zoekterm = st.text_input("🔍 Zoek op naam of e-mailadres")

        gefilterde_gebruikers = []
        for g in gebruikers:
            rol_ok = g.get("Rol", "Onbekend") in gekozen_rol

            zoekveld = f"{g.get('Naam', '')} {g.get('Email', '')}".lower()
            if zoekterm.lower() not in zoekveld:
                continue

            if rol_ok:
                gefilterde_gebruikers.append(g)

        if gefilterde_gebruikers:
            st.markdown(f"**Aantal resultaten:** {len(gefilterde_gebruikers)}")
            for gebruiker in gefilterde_gebruikers:
                with st.container():
                    st.divider()
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

                    laatst_actief = gebruiker.get("Laatst actief")
                    with cols[1]:
                        st.markdown(f"**Naam:** {gebruiker.get('Naam', 'Onbekend')}")
                        st.markdown(f"**Email:** {gebruiker.get('Email', '-')}")
                        st.markdown(f"**Rol:** {gebruiker.get('Rol', '-')}")
                        st.markdown(f"**ID:** `{gebruiker.get('id', '-')}`")
                        st.markdown(f"**Laatst actief:** {tijd_verschil_als_tekst(laatst_actief)}")

                    instellingen = gebruiker.get("Instellingen", {})
                    if instellingen:
                        with st.expander("⚙️ Instellingen"):
                            st.json(instellingen)
        else:
            st.info("Geen gebruikers gevonden met deze filters.")
    else:
        st.warning("Geen gebruikers opgehaald.")

with tab2:
    st.header("📂 Groepen")
    gebruikers_map = {u['id']: u for u in gebruikers}  

    if groepen:
        for groep in groepen:
            with st.expander(f"{groep['name']}"):
                leden_ids = groep.get("user_ids", []) or groep.get("users", [])
                leden_namen = []

                for lid in leden_ids:
                    gebruiker = gebruikers_map.get(lid if isinstance(lid, str) else lid.get("id"))
                    if gebruiker:
                        naam = gebruiker.get("Naam", "Onbekend")
                        email = gebruiker.get("Email", "-")
                        leden_namen.append(f"• **{naam}** – _{email}_")

                if leden_namen:
                    st.markdown("**👥 Groepsleden:**")
                    st.markdown("\n".join(leden_namen))  
                else:
                    st.markdown("**👥 Groepsleden:** _Geen leden in deze groep._")
                
                
                st.divider()

                st.markdown(f"**📋 Beschrijving:** {groep.get('description', '-')}")

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
                    if "success" in result:
                        st.success(result["success"])
                    elif "info" in result:
                        st.info(result["info"])
                    else:
                        st.error(result.get("error", "Onbekende fout bij toevoegen."))

            with col2:
                if st.button("➖ Verwijderen uit groep"):
                    result = remove_user_from_group(group_map[selected_group], user_map[selected_user])
                    if "success" in result:
                        st.success(result["success"])
                    elif "info" in result:
                        st.info(result["info"])
                    else:
                        st.error(result.get("error", "Onbekende fout bij verwijderen."))

            if admins:
                st.markdown("### Beheerders uitgesloten van groepsbeheer")
                st.markdown(
                    f"""
                    <div style="
                        background-color: rgba(255, 176, 0, 0.1);
                        border-left: 4px solid #FFB000;
                        padding: 1rem;
                        border-radius: 8px;
                        margin-top: 1rem;
                        color: inherit;
                    ">
                        <p style="margin-bottom: 0.5rem;"><strong>De volgende beheerders zijn uitgesloten van groepsbeheer:</strong></p>
                        <ul style="margin: 0; padding-left: 1.2rem;">
                            {''.join(f"<li>{naam}</li>" for naam in admins)}
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


