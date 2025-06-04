import requests
import pandas as pd
import os
import datetime
from .config import URL, HEADERS, JSON_HEADERS, timestamp_to_datetime
from .knowledge import get_knowledge

def _extract_kb_names(meta, knowledge_map):
    """Return a list of knowledge base names for a model."""
    if not isinstance(meta, dict):
        return []

    if isinstance(meta.get("knowledge_names"), list):
        return [str(n) for n in meta.get("knowledge_names")]
    if isinstance(meta.get("knowledge_name"), str):
        return [meta.get("knowledge_name")]

    kb_field = meta.get("knowledge")
    if isinstance(kb_field, list):
        names = []
        for item in kb_field:
            if isinstance(item, dict):
                if "name" in item:
                    names.append(str(item["name"]))
                elif "id" in item or "knowledge_id" in item:
                    kid = item.get("id") or item.get("knowledge_id")
                    names.append(knowledge_map.get(kid, str(kid)))
            else:
                names.append(knowledge_map.get(item, str(item)))
        if names:
            return names
    elif isinstance(kb_field, dict):
        if "name" in kb_field:
            return [str(kb_field["name"])]
        kid = kb_field.get("id") or kb_field.get("knowledge_id")
        if kid:
            return [knowledge_map.get(kid, str(kid))]
        
    if isinstance(meta.get("knowledge_ids"), list):
        return [knowledge_map.get(kid, str(kid)) for kid in meta.get("knowledge_ids")]
    kid = meta.get("knowledge_id") or meta.get("knowledge_base_id")
    if kid:
        return [knowledge_map.get(kid, str(kid))]

    return []

def get_models():
    response = requests.get(f"{URL}/models/", headers=HEADERS)
    models = response.json()
    filtered_data = []
    knowledge_map = {k["knowledge_id"]: k["name"] for k in get_knowledge() or []}

    for i in models:
        meta = i.get("meta", {})
        raw_tags = meta.get("tags", [])
        tags = [tag.get("name") for tag in raw_tags if isinstance(tag, dict)]

        kb_names = _extract_kb_names(meta, knowledge_map)
        if isinstance(meta.get("knowledge_names"), list):
            kb_names = [str(n) for n in meta.get("knowledge_names")]
        elif isinstance(meta.get("knowledge_name"), str):
            kb_names = [meta.get("knowledge_name")]
        elif isinstance(meta.get("knowledge_ids"), list):
            kb_names = [knowledge_map.get(kid, str(kid)) for kid in meta.get("knowledge_ids")]
        elif meta.get("knowledge_id"):
            kid = meta.get("knowledge_id")
            kb_names = [knowledge_map.get(kid, str(kid))]

        if i.get('is_active') == True:
            filtered_data.append({
                "model_id": i.get('id'),
                "Chatbot naam": i.get('name'),
                "beschrijving": meta.get('description'),
                "image": meta.get("profile_image_url"),
                "datum aangemaakt": timestamp_to_datetime(i.get('created_at')),
                "laatst bijgewerkt": timestamp_to_datetime(i.get('updated_at')),
                "tags": tags,
                "kennisbanken": kb_names,
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

def get_model_by_id(model_id: str):
    """Haal de volledige modelinfo op via het id."""
    response = requests.get(f"{URL}/models/model?id={model_id}", headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None

def update_model_description(model_id: str, description: str) -> dict:
    """Werk enkel de beschrijving van een model bij."""
    model = get_model_by_id(model_id)
    if not model:
        return {"error": "Model niet gevonden"}

    meta = model.get("meta", {}) or {}
    meta["description"] = description

    model["meta"] = meta
    model["updated_at"] = int(datetime.datetime.utcnow().timestamp() * 1_000_000_000)

    url = f"{URL}/models/model/update?id={model_id}"
    response = requests.post(url, headers=JSON_HEADERS, json=model)

    if response.status_code == 200:
        return {"success": "Beschrijving bijgewerkt"}
    return {"error": f"Updaten mislukt: {response.status_code} - {response.text}"}



def _update_model_tags(model_id: str, tags: list, model: dict | None = None) -> dict:
    """Helper om de tags voor een model bij te werken."""
    if not model:
        model = get_model_by_id(model_id)
    if not model:
        return {"error": "Model niet gevonden"}

    meta = model.get("meta", {}).copy()
    meta["tags"] = [{"name": t} for t in tags]

    payload = model.copy()
    payload.update({
        "id": model_id,
        "meta": meta,
    })

    url = f"{URL}/models/model/update?id={model_id}"
    response = requests.post(url, headers=JSON_HEADERS, json=payload)

    if response.status_code == 200:
        return {"success": "Modeltags bijgewerkt"}
    return {"error": f"Updaten mislukt: {response.status_code} - {response.text}"}

def add_tag_to_model(model_id: str, tag: str) -> dict:
    """Voeg een tag toe aan een model."""
    if not tag:
        return {"error": "Tag mag niet leeg zijn"}

    model = get_model_by_id(model_id)
    if not model:
        return {"error": "Model niet gevonden"}

    meta = model.get("meta", {})
    raw = meta.get("tags", [])
    tags = []
    for t in raw:
        if isinstance(t, dict):
            name = t.get("name")
        else:
            name = str(t)
        if name:
            tags.append(name)

    if tag in tags:
        return {"info": "Tag bestaat al"}

    tags.append(tag)
    return _update_model_tags(model_id, tags, model)


def remove_tag_from_model(model_id: str, tag: str) -> dict:
    """Verwijder een tag van een model."""
    model = get_model_by_id(model_id)
    if not model:
        return {"error": "Model niet gevonden"}

    meta = model.get("meta", {})
    raw = meta.get("tags", [])
    tags = []
    for t in raw:
        if isinstance(t, dict):
            name = t.get("name")
        else:
            name = str(t)
        if name:
            tags.append(name)

    if tag not in tags:
        return {"info": "Tag niet gevonden"}

    tags = [t for t in tags if t != tag]
    return _update_model_tags(model_id, tags, model)


def get_all_tags() -> list:
    """Haal een unieke lijst van alle tags uit basis- en custom modellen."""
    all_tags = set()
    for m in get_models():
        for t in m.get("tags", []):
            all_tags.add(t)
    for b in get_basemodels():
        for t in b.get("tags", []):
            all_tags.add(t)
    return sorted(all_tags)

