import requests
import pandas as pd 
import os
import json
import datetime
import base64
import logging
from .config import URL, HEADERS, JSON_HEADERS, timestamp_to_datetime

def get_users():
    url = f"{URL}/users/"
    response = requests.get(url, headers=HEADERS)
    data = response.json()

    if isinstance(data, dict) and "users" in data:
        gebruikers = data["users"]
    elif isinstance(data, list):
        gebruikers = data
    else:
        raise ValueError("Onverwacht formaat van gebruikersresponse")

    gebruiker_data = []
    for gebruiker in gebruikers:
        gebruiker_data.append({
            "id": gebruiker.get("id"),
            "Naam": gebruiker.get("name"),
            "Email": gebruiker.get("email"),
            "Rol": gebruiker.get("role"),
            "Geüpload op": timestamp_to_datetime(gebruiker.get("created_at")),
            "Bijgewerkt op": timestamp_to_datetime(gebruiker.get("updated_at")),
            "Laatst actief": timestamp_to_datetime(gebruiker.get("last_active_at")),
            "Profielafbeelding": gebruiker.get("profile_image_url"),
            "Instellingen": gebruiker.get("settings", {})
        })
    return gebruiker_data

def get_user_by_id(user_id):
    url = f"{URL}/users/{user_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def update_user_role(user_id, new_role):
    url = f"{URL}/users/update/role"
    payload = {
        "user_id": user_id,
        "role": new_role
    }
    response = requests.post(url, json=payload, headers=JSON_HEADERS)
    return response.ok

def delete_user(user_id):
    url = f"{URL}/users/{user_id}"
    response = requests.delete(url, headers=HEADERS)
    return response.ok

# Debug: sla gebruikers op als JSON in de map 'debug'
# gebruikers = get_users()
# debug_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "debug"))
# os.makedirs(debug_folder, exist_ok=True)
# debug_file_path = os.path.join(debug_folder, "debug_users.json")

# with open(debug_file_path, "w", encoding="utf-8") as f:
#     json.dump(gebruikers, f, ensure_ascii=False, indent=2)

# print(f"✅ Gebruikers opgeslagen in {debug_file_path}")


