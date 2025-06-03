import requests
import pandas as pd 
import os
import json
import datetime
from .config import URL, HEADERS, JSON_HEADERS, timestamp_to_datetime

def get_groups():
    url = f"{URL}/groups/"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def create_group(name, description="", permissions=None):
    url = f"{URL}/groups/create"
    payload = {
        "name": name,
        "description": description,
        "permissions": permissions or {}
    }
    response = requests.post(url, json=payload, headers=JSON_HEADERS)
    return response.ok

def get_group_by_id(group_id):
    response = requests.get(f"{URL}/groups/id/{group_id}", headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return {"error": f"Kon groep niet ophalen: {response.status_code} - {response.text}"}

def update_group(group):
    group_id = group.get("id")
    payload = {
        "name": group.get("name", ""),
        "description": group.get("description", ""),
        "user_ids": group.get("user_ids", [])  
    }
    response = requests.post(f"{URL}/groups/id/{group_id}/update", headers=HEADERS, json=payload)
    if response.status_code == 200:
        return {"success": "Groep bijgewerkt"}
    return {"error": f"Update mislukt: {response.status_code} - {response.text}"}

def delete_group(group_id):
    url = f"{URL}/groups/id/{group_id}/delete"
    response = requests.delete(url, headers=HEADERS)
    return response.ok

def add_user_to_group(group_id: str, user_id: str) -> dict:
    group = get_group_by_id(group_id)
    if "error" in group:
        return group

    user_ids = group.get("user_ids", [])
    if user_id in user_ids:
        return {"info": "Gebruiker zit al in deze groep."}

    user_ids.append(user_id)
    payload = {
        "name": group.get("name", ""),
        "description": group.get("description", ""),
        "user_ids": user_ids
    }

    response = requests.post(f"{URL}/groups/id/{group_id}/update", headers=HEADERS, json=payload)
    if response.status_code == 200:
        return {"success": "Gebruiker toegevoegd aan groep."}
    return {"error": f"Toevoegen mislukt: {response.status_code} - {response.text}"}

def remove_user_from_group(group_id: str, user_id: str) -> dict:
    group = get_group_by_id(group_id)
    if "error" in group:
        return group

    user_ids = group.get("user_ids", [])
    if user_id not in user_ids:
        return {"info": "Gebruiker zit niet in deze groep."}

    user_ids.remove(user_id)
    payload = {
        "name": group.get("name", ""),
        "description": group.get("description", ""),
        "user_ids": user_ids
    }

    response = requests.post(f"{URL}/groups/id/{group_id}/update", headers=HEADERS, json=payload)
    if response.status_code == 200:
        return {"success": "Gebruiker verwijderd uit groep."}
    return {"error": f"Verwijderen mislukt: {response.status_code} - {response.text}"}
