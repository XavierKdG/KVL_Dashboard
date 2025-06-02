import streamlit as st
import datetime
import time
import pandas as pd
import os

from api.config import timestamp_to_datetime
from api.knowledge import get_knowledge, get_knowledge_by_id, update_file_in_knowledgebase, add_file_to_knowledgebase, list_files_in_knowledgebase

from api.files import upload_file

st.title("Bestanden en Kennis")

tab1, tab2 = st.tabs(["📤 Upload bestanden", "📂 Bekijk kennisbank"])

with tab1:
    st.subheader("Upload bestanden naar een kennisbank")

    if "file_uploader_key" not in st.session_state:
        st.session_state.file_uploader_key = "uploader_1"

    bestanden = st.file_uploader("Stap 1: Kies een of meerdere bestanden", type=None, accept_multiple_files=True, key=st.session_state.file_uploader_key)

    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []  

    if bestanden and not st.session_state.get("recent_uploaded_names"):
        st.session_state.recent_uploaded_names = []

        with st.spinner("Bezig met uploaden..."):
            for bestand in bestanden:
                if bestand.name in st.session_state.recent_uploaded_names:
                    continue  

                result = upload_file(bestand)
                if "error" in result:
                    st.error(f"{bestand.name}: {result['error']}")
                else:
                    st.session_state.uploaded_files.append({
                        "name": bestand.name,
                        "file_id": result["file_id"]
                    })
                    st.session_state.recent_uploaded_names.append(bestand.name)
                    st.success(f"Bestand '{bestand.name}' geüpload")

    if st.session_state.uploaded_files:
        kennisbanken = get_knowledge()
        namen_knowledge = [k["name"] for k in kennisbanken]
        kennisbank_dropdown = st.selectbox("Stap 2: Selecteer een kennisbank", namen_knowledge)

        if st.button("Voeg toe aan geselecteerde kennisbank"):
            kennisbank_id = next(k["knowledge_id"] for k in kennisbanken if k["name"] == kennisbank_dropdown)

            with st.spinner("Bezig met koppelen aan kennisbank..."):
                bestaande_bestanden = get_knowledge_by_id(kennisbank_id)
                bestaande_namen = {b.get("meta", {}).get("name") for b in bestaande_bestanden.get("files", [])}

                for f in st.session_state.uploaded_files:
                    file_id = f["file_id"]
                    bestand_naam = f["name"]

                    if bestand_naam in bestaande_namen:
                        result = update_file_in_knowledgebase(kennisbank_id, file_id)
                        status = "geüpdatet"
                    else:
                        result = add_file_to_knowledgebase(kennisbank_id, file_id)
                        status = "toegevoegd"

                    if "success" in result:
                        st.success(f"✅ Bestand '{bestand_naam}' is {status} aan {kennisbank_dropdown}")
                    elif "Duplicate content detected" in result.get("error", ""):
                        st.info(f"ℹ️ Bestand '{bestand_naam}' is al identiek aanwezig in {kennisbank_dropdown} - geen wijzigingen nodig.")
                    else:
                        st.error(f"❌ Bestand '{bestand_naam}': {result['error']}")

            st.session_state.uploaded_files = []
            st.session_state.recent_uploaded_names = []
            st.session_state.file_uploader_key = f"uploader_{int(datetime.datetime.now().timestamp())}"

            st.success(f"Alle bestanden zijn toegevoegd aan {kennisbank_dropdown}. Nieuwe uploadronde start zo...")
            time.sleep(7)

            st.rerun()

with tab2:
    st.subheader("Inhoud van kennisbank bekijken")

    kennisbanken = get_knowledge()
    namen_knowledge = [k["name"] for k in kennisbanken]
    kennisbank_dropdown = st.selectbox("Selecteer een kennisbank", namen_knowledge, key="viewer")

    kennisbank_id = next(k["knowledge_id"] for k in kennisbanken if k["name"] == kennisbank_dropdown)
    result = list_files_in_knowledgebase(kennisbank_id)

    if "error" in result:
        st.error(result["error"])
    elif "empty" in result:
        st.info("📂 Deze kennisbank bevat nog geen bestanden.")
    else:
        st.dataframe(result["data"], use_container_width=True)

