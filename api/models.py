import requests
import pandas as pd 
import os
import datetime
from .config import URL, HEADERS, JSON_HEADERS, timestamp_to_datetime

def get_models():
    response = requests.get(f"{URL}/models/", headers=HEADERS)
    models = response.json()
    filtered_data = []

    for i in models:
        updated_at = i.get('updated_at')
        created_at = i.get('created_at')
        updated_at = timestamp_to_datetime(updated_at)
        created_at = timestamp_to_datetime(created_at)

        filtered_data.append({
            "Chatbot naam": i.get('name'),
            "datum aangemaakt": created_at,
            "laatst bijgewerkt": updated_at,
            })

    return filtered_data

def get_basemodels():
    response = requests.get(f"{URL}/models/base", headers=HEADERS)
    basemodels = response.json()
    filtered_data = []

    for item in basemodels:
        updated_at = timestamp_to_datetime(item.get("updated_at"))
        created_at = timestamp_to_datetime(item.get("created_at"))
        meta = item.get("meta", {})
        tags = item.get('tags', {})

        if item.get("is_active"):
            filtered_data.append({
                "Chatbot naam": item.get("name"),
                "datum aangemaakt": created_at,
                "laatst bijgewerkt": updated_at,
                "image": meta.get("profile_image_url"),
                "tags": tags,
                "metadata": meta,
            })

    return filtered_data



