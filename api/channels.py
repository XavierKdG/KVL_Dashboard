import requests
import pandas as pd 
import os
import datetime
from .config import URL, HEADERS, JSON_HEADERS, timestamp_to_datetime

def get_channels():
    """Haalt een lijst van kanalen op.

    Geeft een lege lijst terug bij fouten of een ongeldig antwoord.
    """
    response = requests.get(f"{URL}/channels/", headers=HEADERS)
    if response.status_code != 200:
        return []

    try:
        channels = response.json()
    except ValueError:
        return []
    filtered_data = []

    for i in channels:
        updated_at = i.get("updated_at")
        updated_at = timestamp_to_datetime(updated_at)

        filtered_data.append(
            {
                "id": i.get("id"),
                "channel naam": i.get("name"),
                "laatst bijgewerkt": updated_at,
            }
        )
        
    return filtered_data 

def get_messages(channel_id):
    """Haalt berichten op voor een specifiek kanaal."""
    response = requests.get(f"{URL}/channels/{channel_id}/messages", headers=HEADERS)

    if response.status_code != 200:
        return []

    try:
        messages = response.json()
    except ValueError:
        return []
    filtered_data = []

    for i in messages:
        updated_at = i.get('updated_at')
        updated_at = timestamp_to_datetime(updated_at) 

        filtered_data.append({
            "content": i.get('content'),
            "laatst bijgewerkt": updated_at,
            })

    return filtered_data

def get_message_counts_by_channel():
    """Geeft een lijst met het aantal berichten per kanaal."""
    channels = get_channels()
    stats = []
    for ch in channels:
        channel_id = ch.get("id")
        if channel_id is None:
            continue
        messages = get_messages(channel_id)
        stats.append({
            "kanaal": ch.get("channel naam"),
            "aantal": len(messages),
        })
    return stats