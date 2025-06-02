import requests
import pandas as pd 
import os
import datetime
from .config import URL, HEADERS, JSON_HEADERS, timestamp_to_datetime

def get_channels():
    response = requests.get(f"{URL}/channels/", headers=HEADERS)
    channels = response.json()
    filtered_data = []

    for i in channels:
        updated_at = i.get('updated_at')
        updated_at = timestamp_to_datetime(updated_at) 

        filtered_data.append({
            "channel naam": i.get('name'),
            "laatst bijgewerkt": updated_at,
            })
        
    return filtered_data 

def get_messages(channel_id):
    response = requests.get(f"{URL}/channels/{channel_id}/messages", headers=HEADERS)
    messages = response.json()
    filtered_data = []

    for i in messages:
        updated_at = i.get('updated_at')
        updated_at = timestamp_to_datetime(updated_at) 

        filtered_data.append({
            "content": i.get('content'),
            "laatst bijgewerkt": updated_at,
            })

    return filtered_data
