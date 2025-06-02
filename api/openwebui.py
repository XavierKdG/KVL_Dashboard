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

def timestamp_to_datetime(ts):
    if not ts or ts <= 0:
        return "-"

    if ts > 1e12:
        ts = ts / 1_000_000_000

    try:
        return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "ongeldige datum"

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

def get_knowledge():
    response = requests.get(f"{URL}/knowledge/", headers=HEADERS)
    knowledge = response.json()
    filtered_data = []

    for i in knowledge:
        filtered_data.append({
            "name": i.get('name'),
            "knowledge_id": i.get('id'),
            })
        
    return filtered_data

def get_knowledge_by_id(knowledge_id):
    response = requests.get(f"{URL}/knowledge/{knowledge_id}", headers=HEADERS)
    
    if response.status_code != 200:
        return {"error": f"Kan kennisbank niet ophalen: {response.status_code} - {response.text}"}
    
    return response.json()


def upload_and_add_to_knowledgebase(file_object=None, knowledge_id=None, only_upload=False, file_id=None):
    if only_upload and file_object:
        upload_url = f"{URL}/files/"
        files = {"file": (file_object.name, file_object, file_object.type)}
        response = requests.post(upload_url, headers=HEADERS, files=files)

        if response.status_code != 200:
            return {"error": f"Upload mislukt: {response.status_code} - {response.text}"}

        return {"file_id": response.json().get("id")}

    elif file_id and knowledge_id:
        add_url = f"{URL}/knowledge/{knowledge_id}/file/add"
        payload = {"file_id": file_id}
        response = requests.post(add_url, headers={**HEADERS, "Content-Type": "application/json"}, json=payload)

        if response.status_code == 200:
            return {"success": f"Bestand gekoppeld aan kennisbank"}
        else:
            return {"error": f"Koppelen mislukt: {response.status_code} - {response.text}"}

    return {"error": "Ongeldige parameters"}



if __name__ == "__main__":
#     messages = get_messages("d968f28b-26e4-40c5-aea9-558c964b01d9")
#     channels = get_channels()
    # models = get_models()
    knowledge = get_knowledge()
    # feedback = get_feedback()
#     print(messages)
#     print(channels)
    print(knowledge)
    # print(feedback)
    # print(models)
