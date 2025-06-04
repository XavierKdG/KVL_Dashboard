import streamlit as st
import pandas as pd
from api.groups import get_groups, add_model_to_group, remove_model_from_group
from api.models import (
    get_models,
    get_basemodels,
    update_model_description,
    add_tag_to_model,
    remove_tag_from_model,
    get_all_tags,
)
from api.chats import get_chat_usage_summary
from api.evaluations import get_feedback_summary
import plotly.express as px
from collections import defaultdict
import plotly.graph_objects as go
import re
from auth import require_login


def _rerun_app():
    """Rerun Streamlit app compatible across versions."""
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()


require_login()
st.logo("static/KVL logo.png", size="large")
st.title("Modellen & LLM-gebruik")

with st.spinner("Alle data ophalen..."):
    models = get_models()
    basemodels = get_basemodels()
    usage_df = get_chat_usage_summary()
    feedback_df = get_feedback_summary()
    groups = get_groups()


def prettify_model_name(name: str) -> str:
    if not isinstance(name, str):
        return name
    pretty = name.replace("-", " ").replace("_", " ").title()
    pretty = re.sub(r"\bKvl\b", "KVL", pretty)
    return pretty


tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📋 Overzicht",
        "🏷️ Tags",
        "🧠 Basismodellen",
        "📊 Meest gebruikte modellen",
        "📝 Feedback op modellen",
    ]
)

df_models = pd.DataFrame(models)
df_basemodels = pd.DataFrame(basemodels)

df_models["datum aangemaakt"] = pd.to_datetime(df_models["datum aangemaakt"])
df_models["laatst bijgewerkt"] = pd.to_datetime(df_models["laatst bijgewerkt"])

with tab1:
    st.subheader("📋 Beschikbare Custom Modellen")
    st.caption(
        "Een lijst van alle actieve custom modellen, inclusief beschrijving, afbeelding, aanmaakdatum en laatste wijziging."
    )

    if df_models.empty:
        st.info("Er zijn geen actieve modellen gevonden.")
    else:
        sorteer_optie = st.selectbox(
            "Sorteer op:", ["Aangemaakt", "Bijgewerkt"], index=0
        )
        oplopend = st.toggle("Sorteer van oud naar nieuw", value=False)

    if sorteer_optie == "Bijgewerkt":
        df_models_sorted = df_models.sort_values(
            "laatst bijgewerkt", ascending=oplopend
        )
    else:
        df_models_sorted = df_models.sort_values(
            "datum aangemaakt", ascending=oplopend
        )

    group_map = {g["name"]: g["id"] for g in groups} if groups else {}

    def save_desc(model_id, key):
        desc = st.session_state.get(key, "")
        result = update_model_description(model_id, desc)
        if "success" in result:
            st.success(result["success"])
        else:
            st.error(result.get("error", "Onbekende fout"))

    for index, row in df_models_sorted.iterrows():
        with st.container():
            # Maak 2 kolommen: links alles behalve metadata, rechts alleen metadata
            left_col, right_col = st.columns([5, 2])

            with left_col:
                # Logo + titel horizontaal naast elkaar
                logo_col, name_col = st.columns([1, 5])
                with logo_col:
                    if isinstance(row["image"], str) and (
                        row["image"].startswith("http")
                        or row["image"].startswith("data:image")
                    ):
                        st.image(row["image"], width=60)
                    else:
                        st.markdown("❓")
                with name_col:
                    st.markdown(f"### {row['Chatbot naam']}")

                # Daarna direct de expander
                with st.expander("🔧 Meer details"):
                    st.text_area(
                        "Beschrijving",
                        value=row["beschrijving"] or "",
                        key=f"desc_{index}",
                        on_change=save_desc,
                        args=(row["model_id"], f"desc_{index}"),
                    )

                    model_groups = []
                    for g in groups:
                        perms = g.get("model_permissions", {})
                        if str(row["model_id"]) in perms:
                            mode = (
                                "Schrijven" if perms[str(row["model_id"])] == "write" else "Lezen"
                            )
                            model_groups.append(f"{g['name']} ({mode})")
                    st.markdown(
                        f"**Groepen:** {', '.join(model_groups) if model_groups else '-'}"
                    )

                    if group_map:
                        selected_group = st.selectbox(
                            "Selecteer groep",
                            options=list(group_map.keys()),
                            key=f"group_sel_{index}",
                        )
                        perm_choice = st.radio(
                            "Rechten",
                            ["Alleen lezen", "Schrijven"],
                            horizontal=True,
                            key=f"perm_sel_{index}",
                        )
                        add_col, rem_col = st.columns(2)
                        with add_col:
                            if st.button("➕ Toevoegen", key=f"add_grp_{index}"):
                                write = perm_choice == "Schrijven"
                                res = add_model_to_group(
                                    group_map[selected_group],
                                    str(row["model_id"]),
                                    write=write,
                                )
                                if "success" in res:
                                    st.success(res["success"])
                                    _rerun_app()
                                elif "info" in res:
                                    st.info(res["info"])
                                else:
                                    st.error(res.get("error", "Onbekende fout bij toevoegen."))
                        with rem_col:
                            if st.button("➖ Verwijderen", key=f"rem_grp_{index}"):
                                res = remove_model_from_group(
                                    group_map[selected_group], str(row["model_id"])
                                )
                                if "success" in res:
                                    st.success(res["success"])
                                    _rerun_app()
                                elif "info" in res:
                                    st.info(res["info"])
                                else:
                                    st.error(res.get("error", "Onbekende fout bij verwijderen."))

            with right_col:
                st.markdown(f"🕓 **Aangemaakt:** {row['datum aangemaakt'].strftime('%Y-%m-%d')}")
                st.markdown(f"🔄 **Laatste update:** {row['laatst bijgewerkt'].strftime('%Y-%m-%d')}")
                if row.get("kennisbanken"):
                    kb_list = row["kennisbanken"]
                    names = ", ".join(kb_list) if isinstance(kb_list, list) else str(kb_list)
                    st.markdown(f"📚 **Kennisbanken:** {names}")

            st.divider()

with tab2:
    st.subheader("🔖 Overzicht van alle tags met bijbehorende modellen")
    st.caption(
        "Alle gebruikte tags bij basismodellen en custom modellen. Klik per tag door naar de gekoppelde modellen."
    )
    combined = []

    for _, row in df_basemodels.iterrows():
        for tag in row.get("tags", []):
            combined.append(
                {
                    "tag": tag,
                    "model": row["Chatbot naam"],
                    "image": row.get("image"),
                }
            )

    for _, row in df_models.iterrows():
        for tag in row.get("tags", []):
            combined.append(
                {
                    "tag": tag,
                    "model": row["Chatbot naam"],
                    "image": row.get("image"),
                }
            )

    if combined:
        tag_to_models = defaultdict(list)
        tag_to_images = {}

        for entry in combined:
            tag = entry["tag"]
            tag_to_models[tag].append(entry["model"])
            if tag not in tag_to_images and isinstance(
                entry.get("image"), str
            ):
                tag_to_images[tag] = entry["image"]

        sorted_tags = sorted(
            tag_to_models.items(),
            key=lambda x: (-1 if x[0] == "KVL" else 0, -len(x[1])),
        )

        for tag, models in sorted_tags:
            with st.expander(f"{tag} ({len(models)} modellen)"):
                cols = st.columns([1, 5])
                with cols[0]:
                    image_url = tag_to_images.get(tag)
                    if image_url and (
                        image_url.startswith("http")
                        or image_url.startswith("data:image")
                    ):
                        st.image(image_url, width=60, caption=tag)
                    else:
                        st.markdown("📁")

                with cols[1]:
                    for m in models:
                        st.markdown(f"- {m}")
    else:
        st.info("Geen tags gevonden in basismodellen of modellen.")

    st.divider()
    st.subheader("✏️ Tags beheren")
    if df_models.empty:
        st.info("Geen modellen beschikbaar om tags te beheren.")
    else:
        model_map = {
            row["Chatbot naam"]: row["model_id"]
            for _, row in df_models.iterrows()
        }
        selected_model = st.selectbox(
            "Selecteer model", options=list(model_map.keys())
        )
        model_id = model_map[selected_model]
        current_tags = df_models.loc[
            df_models["Chatbot naam"] == selected_model, "tags"
        ].iloc[0]
        if not isinstance(current_tags, list):
            current_tags = []
        st.markdown(
            f"**Huidige tags:** {', '.join(current_tags) if current_tags else '-'}"
        )

        available_tags = get_all_tags()
        existing_tag = st.selectbox(
            "Kies een bestaande tag", options=[""] + available_tags, index=0
        )
        new_tag = st.text_input("Of typ een nieuwe tag")

        col_add, col_del = st.columns(2)
        with col_add:
            if st.button("➕ Tag toevoegen"):
                tag_to_add = (
                    new_tag.strip() if new_tag.strip() else existing_tag
                )
                if not tag_to_add:
                    st.warning("Geen tag opgegeven")
                else:
                    result = add_tag_to_model(model_id, tag_to_add)
                    if "success" in result:
                        st.success(result["success"])
                        _rerun_app()
                    elif "info" in result:
                        st.info(result["info"])
                    else:
                        st.error(result.get("error", "Onbekende fout"))

        with col_del:
            if current_tags:
                tag_to_remove = st.selectbox(
                    "Tag verwijderen", options=current_tags, key="tag_remove"
                )
                if st.button("➖ Verwijder tag"):
                    result = remove_tag_from_model(model_id, tag_to_remove)
                    if "success" in result:
                        st.success(result["success"])
                        _rerun_app()
                    elif "info" in result:
                        st.info(result["info"])
                    else:
                        st.error(result.get("error", "Onbekende fout"))
with tab3:
    st.subheader("🤖 Basismodellen")
    st.caption(
        "Een overzicht van alle beschikbare basismodellen waarop de custom modellen zijn gebouwd. Hier zie je per model de naam, het aanmaakmoment en indien beschikbaar een visuele representatie."
    )

    for _, row in df_basemodels.iterrows():
        col1, col2 = st.columns([1, 6])

        with col1:
            image_url = row.get("image")
            if isinstance(image_url, str) and (
                image_url.startswith("http")
                or image_url.startswith("data:image")
            ):
                st.image(image_url, width=60)
            else:
                st.markdown("❓")

        with col2:
            clean_name = str(row["Chatbot naam"]).replace("*", "")
            st.markdown(f"**{clean_name}**")
            st.caption(f"Aangemaakt op: {row['datum aangemaakt']}")


with tab4:
    st.subheader("📊 Meest gebruikte modellen op basis van chats")
    st.caption(
        "Analyse van het daadwerkelijke gebruik per model op basis van het aantal chatinteracties."
    )

    if usage_df.empty:
        st.info("Geen chatgegevens gevonden.")
    else:
        usage_df_sorted = usage_df.sort_values("Aantal chats", ascending=True)

        fig = px.bar(
            usage_df_sorted,
            x="Aantal chats",
            y="model",
            orientation="h",
            title="🔝 Meest gebruikte modellen",
            labels={"model": "Model", "Aantal chats": "Aantal chats"},
            color="Aantal chats",
            color_continuous_scale=[
                (0.0, "#e0f7f8"),
                (0.5, "#66c7ca"),
                (1.0, "#00888E"),
            ],
            hover_name="model",
        )
        fig.update_layout(
            yaxis_title=None, xaxis_title="Aantal chats", height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(usage_df_sorted[::-1], use_container_width=True)

with tab5:
    st.subheader("📝 Gebruikersfeedback per model")
    st.caption(
        "Inzicht in likes, dislikes, gemiddelde beoordeling en meest genoemde tag per model."
    )

    if feedback_df.empty:
        st.info("Geen feedback gevonden.")
    else:
        feedback_df_sorted = feedback_df.sort_values(
            "Gemiddelde beoordeling", ascending=True
        )
        feedback_df_sorted["Model naam"] = feedback_df_sorted["model"].apply(
            prettify_model_name
        )

        for col in ["👍", "👎"]:
            if col not in feedback_df_sorted.columns:
                feedback_df_sorted[col] = 0

        st.dataframe(
            feedback_df_sorted.set_index("Model naam")[
                ["Gemiddelde beoordeling", "👍", "👎", "Top tag"]
            ],
            use_container_width=True,
        )

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=feedback_df_sorted["Model naam"],
                y=feedback_df_sorted["👍"],
                name="👍 Likes",
                marker_color="#3AAA35",
            )
        )
        fig.add_trace(
            go.Bar(
                x=feedback_df_sorted["Model naam"],
                y=feedback_df_sorted["👎"],
                name="👎 Dislikes",
                marker_color="#E2725B",
            )
        )
        fig.update_layout(
            barmode="group",
            title="Aantal likes en dislikes per model",
            xaxis_title="Model",
            yaxis_title="Aantal",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        fig_score = px.bar(
            feedback_df_sorted,
            x="Gemiddelde beoordeling",
            y="Model naam",
            orientation="h",
            text="Gemiddelde beoordeling",
            title="Gemiddelde gebruikersbeoordeling per model",
            color="Gemiddelde beoordeling",
            color_continuous_scale=[
                (0.0, "#E2725B"),
                (0.5, "#EEA400"),
                (1.0, "#3AAA35"),
            ],
            range_color=(0, 10),
        )
        fig_score.update_layout(
            xaxis_title="Gemiddelde beoordeling",
            yaxis_title="Model",
            height=400,
            coloraxis_showscale=False,
        )
        fig_score.update_traces(
            textfont=dict(size=13, color="black"), textposition="inside"
        )
        st.plotly_chart(fig_score, use_container_width=True)