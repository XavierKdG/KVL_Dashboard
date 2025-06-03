import streamlit as st
import pandas as pd
from api.models import get_models, get_basemodels
import plotly.express as px
from collections import defaultdict
import plotly.graph_objects as go
from auth import require_login

require_login()
st.logo("assets/KVL logo.png", size='large')
st.title("Modellen & LLM-gebruik")

with st.spinner("Modellen ophalen..."):
    models = get_models()
    basemodels = get_basemodels()

df_models = pd.DataFrame(get_models())
df_basemodels = pd.DataFrame(basemodels)

df_models["datum aangemaakt"] = pd.to_datetime(df_models["datum aangemaakt"])
df_models["laatst bijgewerkt"] = pd.to_datetime(df_models["laatst bijgewerkt"])

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Overzicht", "📈 Tijdlijn", "🏷 Tags", "🧠 Basismodellen", "⚙️ Capabilities"])

with tab1:
    st.subheader("Beschikbare Custom Modellen")
    
    if df_models.empty:
        st.info("Er zijn geen actieve modellen gevonden.")
    else:
        for index, row in df_models.iterrows():
            with st.container():
                cols = st.columns([1, 4, 2]) 
                with cols[0]:
                    if isinstance(row["image"], str) and (row["image"].startswith("http") or row["image"].startswith("data:image")):
                        st.image(row["image"], width=60)
                    else:
                        st.markdown("❓")

                with cols[1]:
                    st.markdown(f"### {row['Chatbot naam']}")
                    st.markdown(f"{row['beschrijving'] or '_Geen beschrijving beschikbaar_'}")

                with cols[2]:
                    st.markdown(f"🕓 Aangemaakt: {row['datum aangemaakt'].strftime('%Y-%m-%d')}")
                    st.markdown(f"🔄 Laatste update: {row['laatst bijgewerkt'].strftime('%Y-%m-%d')}")
            
                st.markdown("---")

with tab2:
    st.subheader("Modelactiviteit over tijd")
    fig = px.scatter(
        df_models,
        x="datum aangemaakt",
        y="laatst bijgewerkt",
        text="Chatbot naam",
        title="Wanneer zijn modellen voor het laatst bijgewerkt?"
    )

    fig.update_traces(marker=dict(size=15), textposition='top right')

    st.plotly_chart(fig)

with tab3:
    st.subheader("Overzicht van alle tags met bijbehorende modellen")

    combined = []

    for _, row in df_basemodels.iterrows():
        for tag in row.get("tags", []):
            combined.append({
                "tag": tag,
                "model": row["Chatbot naam"],
                "image": row.get("image")
            })

    for _, row in df_models.iterrows():
        for tag in row.get("tags", []):
            combined.append({
                "tag": tag,
                "model": row["Chatbot naam"],
                "image": row.get("image")
            })

    if combined:
        tag_to_models = defaultdict(list)
        tag_to_images = {}

        for entry in combined:
            tag = entry["tag"]
            tag_to_models[tag].append(entry["model"])
            if tag not in tag_to_images and isinstance(entry.get("image"), str):
                tag_to_images[tag] = entry["image"]

        # Zet 'KVL' bovenaan, daarna rest gesorteerd op aantal modellen
        sorted_tags = sorted(tag_to_models.items(), key=lambda x: (-1 if x[0] == "KVL" else 0, -len(x[1])))


        for tag, models in sorted_tags:
            st.divider()
            cols = st.columns([1, 5])
            with cols[0]:
                image_url = tag_to_images.get(tag)
                if image_url and (image_url.startswith("http") or image_url.startswith("data:image")):
                    st.image(image_url, width=60, caption=tag)
                else:
                    st.markdown(f"### {tag}")

            with cols[1]:
                st.markdown(f"### {tag} ({len(models)} modellen)")
                for m in models:
                    st.markdown(f"- {m}")
    else:
        st.info("Geen tags gevonden in basismodellen of modellen.")


with tab4:
    st.subheader("🤖 Basismodellen")
    st.divider()
    for _, row in df_basemodels.iterrows():
        col1, col2 = st.columns([1, 6])

        with col1:
            image_url = row.get("image")
            if isinstance(image_url, str) and (image_url.startswith("http") or image_url.startswith("data:image")):
                st.image(image_url, width=60)
            else:
                st.markdown("❓")

        with col2:
            clean_name = str(row['Chatbot naam']).replace("*", "")
            st.markdown(f"**{clean_name}**")
            st.caption(f"Aangemaakt op: {row['datum aangemaakt']}")


with tab5:
    st.subheader("🧪 Capabilities per model")
    if "capabilities" in df_basemodels.columns:
        capabilities_df = df_basemodels["capabilities"].apply(pd.Series)
        cap_table = pd.concat([df_basemodels["Chatbot naam"], capabilities_df], axis=1)
        st.dataframe(cap_table)
    else:
        st.info("Geen capabilities beschikbaar.")
