import requests
import pandas as pd 
import os
import json
import datetime
from .config import URL, HEADERS, JSON_HEADERS, timestamp_to_datetime
from .users import get_users

def get_all_chats():
    response = requests.get(f"{URL}/chats/all/db", headers=HEADERS)
    response.raise_for_status()
    chats = response.json()

    filtered_data = []
    for chat in chats:
        filtered_data.append({
            "chat_id": chat.get("id"),
            "model": extract_model_name(chat),
            "titel": chat.get("title"),
            "user_id": chat.get("user_id"),
            "created_at": timestamp_to_datetime(chat.get("created_at")),
            "updated_at": timestamp_to_datetime(chat.get("updated_at"))
        })

    return filtered_data

def extract_model_name(chat):
    history = chat.get("chat", {}).get("history", {}).get("messages", {})
    for message in history.values():
        model_name = message.get("modelName")
        if model_name:
            return model_name.strip()
    models = chat.get("chat", {}).get("models", [])
    return models[0] if models else None

def get_chat_usage_summary():
    data = get_all_chats()
    df = pd.DataFrame(data)

    if df.empty or "model" not in df:
        return pd.DataFrame()

    summary = (
        df.groupby("model")
        .size()
        .reset_index(name="Aantal chats")
        .sort_values("Aantal chats", ascending=False)
    )

    return summary

def get_chat_counts_by_user():
    """Geeft het aantal chats per gebruiker terug als DataFrame met gebruikersnamen."""
    data = get_all_chats()
    df = pd.DataFrame(data)
    if df.empty or "user_id" not in df:
        return pd.DataFrame()

    counts = (
        df.groupby("user_id")
        .size()
        .reset_index(name="Aantal chats")
        .sort_values("Aantal chats", ascending=False)
    )
    users = pd.DataFrame(get_users())
    if not users.empty:
        counts = counts.merge(users[["id", "Naam"]], left_on="user_id", right_on="id", how="left")
        counts.drop(columns=["id"], inplace=True)
        counts["Naam"].fillna(counts["user_id"], inplace=True)
        counts.drop(columns=["user_id"], inplace=True)
        
    return counts


###### debug gedeelte voor /chats/all/db
# debug_folder = "debug"
# os.makedirs(debug_folder, exist_ok=True)
# debug_file_path = os.path.join(debug_folder, "debug_chats_db.json")
# chats = get_all_chats()
# with open(debug_file_path, "w", encoding="utf-8") as f:
#     json.dump(chats, f, ensure_ascii=False, indent=2)
# print(f"Chats opgeslagen in {debug_file_path}")
