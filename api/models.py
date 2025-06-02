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

