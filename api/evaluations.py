import requests
import pandas as pd 
import os
import json
import datetime
from .config import URL, HEADERS, JSON_HEADERS, timestamp_to_datetime

def get_feedback():
    response = requests.get(f"{URL}/evaluations/feedbacks/all", headers=HEADERS)
    feedback = response.json()
    processed = []

    for fb in feedback:
        data = fb.get("data", {})
        model_id = data.get("model_id") or fb.get("meta", {}).get("model_id")
        processed.append({
            "model": model_id,
            "rating_raw": data.get("rating"),
            "score": data.get("details", {}).get("rating"),
            "type": "like" if data.get("rating") == 1 else ("dislike" if data.get("rating") == -1 else "neutral"),
            "reason": data.get("reason"),
            "comment": data.get("comment"),
            "tags": ", ".join(data.get("tags", [])) if data.get("tags") else None,
            "datum": timestamp_to_datetime(fb.get("created_at")),
            "user": fb.get("user", {}).get("email")
        })

    return processed

def get_feedback_summary():
    feedback = get_feedback()
    df = pd.DataFrame(feedback)

    if df.empty:
        return pd.DataFrame()

    avg_scores = df.groupby("model")["score"].mean().reset_index(name="Gemiddelde beoordeling")

    counts = df.groupby(["model", "type"]).size().unstack(fill_value=0).reset_index()

    tag_counts = df.dropna(subset=["tags"]).copy()
    tag_counts["tags"] = tag_counts["tags"].str.split(", ")
    tag_counts = tag_counts.explode("tags")
    top_tags = tag_counts.groupby("model")["tags"].agg(lambda x: x.value_counts().index[0] if len(x) > 0 else None).reset_index(name="Top tag")

    summary = avg_scores.merge(counts, on="model", how="left").merge(top_tags, on="model", how="left")
    summary = summary.rename(columns={"like": "👍", "dislike": "👎", "neutral": "⚪️"})

    return summary.sort_values("Gemiddelde beoordeling", ascending=False)


###### debug gedeelte
# debug_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "debug"))
# os.makedirs(debug_dir, exist_ok=True)
# debug_file = os.path.join(debug_dir, "debug_feedback.json")
# feedback = get_feedback()
# with open(debug_file, "w", encoding="utf-8") as f:
#     json.dump(feedback, f, ensure_ascii=False, indent=2)
# print(f"Feedback opgeslagen in {debug_file}")