import requests
import pandas as pd 
import os
import datetime
from .config import URL, HEADERS, JSON_HEADERS, timestamp_to_datetime

def _format_file_size(size):
    """Converts a size in bytes to a human readable string."""
    if size is None:
        return None
    try:
        size = int(size)
    except (TypeError, ValueError):
        return None

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"

def get_knowledge():
    response = requests.get(f"{URL}/knowledge/", headers=HEADERS)
    knowledge = response.json()
    filtered_data = []

    for i in knowledge:
        filtered_data.append(
            {
                "name": i.get("name"),
                "knowledge_id": i.get("id"),
                "created_at": timestamp_to_datetime(i.get("created_at")),
                "updated_at": timestamp_to_datetime(i.get("updated_at")),
            }
        )

    return filtered_data

def get_knowledge_by_id(knowledge_id):
    response = requests.get(f"{URL}/knowledge/{knowledge_id}", headers=HEADERS)
    
    if response.status_code != 200:
        return {"error": f"Kan kennisbank niet ophalen: {response.status_code} - {response.text}"}
    
    return response.json()

def update_file_in_knowledgebase(knowledge_id, file_id):
    url = f"{URL}/knowledge/{knowledge_id}/file/update"
    payload = {"file_id": file_id}
    headers = {**HEADERS, "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return {"success": f"Bestand geüpdatet"}
    else:
        return {"error": f"Updaten mislukt: {response.status_code} - {response.text}"}
    
def add_file_to_knowledgebase(knowledge_id, file_id):
    add_url = f"{URL}/knowledge/{knowledge_id}/file/add"
    payload = {"file_id": file_id}
    response = requests.post(add_url, headers=JSON_HEADERS, json=payload)

    if response.status_code == 200:
        return {"success": "Bestand gekoppeld aan kennisbank"}
    else:
        return {"error": f"Koppelen mislukt: {response.status_code} - {response.text}"}
    
def list_files_in_knowledgebase(knowledge_id):
    url = f"{URL}/knowledge/{knowledge_id}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return {"error": f"Kan kennisbank niet ophalen: {response.status_code} - {response.text}"}

    data = response.json()
    files = data.get("files", [])
    if not files:
        return {"empty": True}

    bestanden_info = []

    for f in files:
        file_meta = f.get("meta", {})
        full_name = file_meta.get("name", f.get("id"))
        name_without_ext, file_ext = os.path.splitext(full_name)
        file_ext = file_ext.replace(".", "").lower()

        bestanden_info.append({
            "Bestandsnaam": name_without_ext,
            "Bestandstype": file_ext,
            "Bestandsgrootte": _format_file_size(file_meta.get("size") or file_meta.get("file_size")),
            "Content type": file_meta.get("content_type"),
            "Collectie": file_meta.get("collection_name"),
            "Geüpload op": timestamp_to_datetime(f.get("created_at")),
            "Bijgewerkt op": timestamp_to_datetime(f.get("updated_at")),
            "file_id": f.get("id"),
            "metadata": file_meta,
        })

    df = pd.DataFrame(bestanden_info)
    return {"data": df}

