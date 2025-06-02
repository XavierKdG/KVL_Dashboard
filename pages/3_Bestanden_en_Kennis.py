import streamlit as st
import datetime
import time
from api.openwebui import get_knowledge, upload_and_add_to_knowledgebase

st.title("Bestanden en Kennis")
st.markdown('---')
st.subheader("Upload bestanden en voeg toe aan kennisbank")

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

            result = upload_and_add_to_knowledgebase(bestand, knowledge_id=None, only_upload=True)
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
            for f in st.session_state.uploaded_files:
                result = upload_and_add_to_knowledgebase(None, kennisbank_id, file_id=f["file_id"])
                # if "success" in result:
                #     st.success(f"{f['name']} toegevoegd aan {kennisbank_dropdown}")
                # else:
                #     st.error(f"{f['name']}: {result['error']}")

        st.session_state.uploaded_files = []
        st.session_state.recent_uploaded_names = []
        st.session_state.file_uploader_key = f"uploader_{int(datetime.datetime.now().timestamp())}"

        st.success(f"Alle bestanden zijn toegevoegd aan {kennisbank_dropdown}. Nieuwe uploadronde start zo...")
        time.sleep(7)

        st.rerun()


st.markdown('---')
kennisbank_dropdown = st.selectbox("Selecteer een kennisbank", namen_knowledge)
