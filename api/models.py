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
        meta = i.get("meta", {})
        raw_tags = meta.get("tags", [])
        tags = [tag.get("name") for tag in raw_tags if isinstance(tag, dict)]

        if i.get('is_active') == True:
            filtered_data.append({
                "Chatbot naam": i.get('name'),
                "beschrijving": meta.get('description'),
                "image": meta.get("profile_image_url"),
                "datum aangemaakt": timestamp_to_datetime(i.get('created_at')),
                "laatst bijgewerkt": timestamp_to_datetime(i.get('updated_at')),
                "tags": tags,
                "metadata": meta
            })

    return filtered_data


def get_basemodels():
    response = requests.get(f"{URL}/models/base", headers=HEADERS)
    basemodels = response.json()
    filtered_data = []

    for item in basemodels:
        meta = item.get("meta", {})
        raw_tags = meta.get("tags", [])
        tags = [tag.get("name") for tag in raw_tags if isinstance(tag, dict)]

        if item.get("is_active"):
            filtered_data.append({
                "Chatbot naam": item.get("name"),
                "datum aangemaakt": timestamp_to_datetime(item.get("created_at")),
                "laatst bijgewerkt": timestamp_to_datetime(item.get("updated_at")),
                "image": meta.get("profile_image_url"),
                "tags": tags,
                "metadata": meta
            })

    return filtered_data



