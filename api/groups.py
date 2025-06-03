import requests
import pandas as pd 
import os
import json
import datetime
from .config import URL, HEADERS, JSON_HEADERS, timestamp_to_datetime

def get_groups():
    """Ophalen van alle groepen."""
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
    url = f"{URL}/groups/id/{group_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def update_group(group_id, updates):
    url = f"{URL}/groups/id/{group_id}/update"
    response = requests.post(url, json=updates, headers=JSON_HEADERS)
    return response.ok

def delete_group(group_id):
    url = f"{URL}/groups/id/{group_id}/delete"
    response = requests.delete(url, headers=HEADERS)
    return response.ok

def add_user_to_group(group_id, user_id):
    url = f"{URL}/groups/id/{group_id}/members/add"
    response = requests.post(url, json={"user_id": user_id}, headers=JSON_HEADERS)
    return response.ok

def remove_user_from_group(group_id, user_id):
    url = f"{URL}/groups/id/{group_id}/members/remove"
    response = requests.post(url, json={"user_id": user_id}, headers=JSON_HEADERS)
    return response.ok
