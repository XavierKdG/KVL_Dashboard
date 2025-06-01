"""
OpenWebUI API Endpoints verwerkt in een dashboard voor KVL
Voor gebruik installeer bijbehorende requirements (pip install -r requirements.txt)
Zorg dat je een .env bestand hebt met API_KEY=jouw_api_key_hier erin
"""

import requests
import os
import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')
URL = 'http://localhost:8081/api/v1'
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Functie om van timestamp naar datum_tijd om te zetten
def timestamp_to_datetime(timestamp_variabel):
    timestamp_variabel = timestamp_variabel / 1_000_000_000
    datum = datetime.datetime.fromtimestamp(timestamp_variabel).strftime("%Y-%m-%d %H:%M:%S") 
    return datum

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

def get_feedback():
    response = requests.get(f"{URL}/evaluations/feedbacks/all", headers=HEADERS)
    feedback = response.json()
    filtered_data = []

    for i in feedback:
        filtered_data.append({
            "model": i.get('data')
            })
        
    return filtered_data 

if __name__ == "__main__":
#     messages = get_messages("d968f28b-26e4-40c5-aea9-558c964b01d9")
#     channels = get_channels()
    # models = get_models()
    feedback = get_feedback()
#     print(messages)
#     print(channels)
    print(feedback)
    # print(models)
