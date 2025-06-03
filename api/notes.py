import requests
import pandas as pd 
import os
import datetime
from .config import URL, HEADERS, JSON_HEADERS, timestamp_to_datetime

def get_notes():
    """Haalt alle notities op."""
    response = requests.get(f"{URL}/notes/", headers=HEADERS)
    if response.status_code != 200:
        return []
    try:
        notes = response.json()
    except ValueError:
        return []

    data = []
    for n in notes:
        data.append({
            "id": n.get("id"),
            "titel": n.get("title") or n.get("name"),
            "user_id": n.get("user_id"),
            "created_at": timestamp_to_datetime(n.get("created_at")),
            "updated_at": timestamp_to_datetime(n.get("updated_at")),
        })
    return data


def get_note_counts_by_user():
    """Geeft het aantal notities per gebruiker terug als DataFrame."""
    notes = get_notes()
    df = pd.DataFrame(notes)
    if df.empty or "user_id" not in df:
        return pd.DataFrame()

    counts = (
        df.groupby("user_id")
        .size()
        .reset_index(name="Aantal notities")
        .sort_values("Aantal notities", ascending=False)
    )
    return counts