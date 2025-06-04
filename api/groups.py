import requests
import pandas as pd
import os
import json
import datetime
from .config import URL, HEADERS, JSON_HEADERS, timestamp_to_datetime


def _format_group(group: dict) -> dict:
    """Zet een ruwe groepsdict om naar een eenduidige representatie."""
    access_map = {}
    perm_map = group.get("model_permissions")
    if isinstance(perm_map, dict):
        for mid, mode in perm_map.items():
            access_map[str(mid)] = str(mode) if mode else "read"

    raw_models = group.get("model_ids")
    if not raw_models:
        raw_models = group.get("models", [])
    if isinstance(raw_models, list):
        for m in raw_models:
            if isinstance(m, dict):
                mid = m.get("id") or m.get("model_id") or m.get("name")
                if mid is not None:
                    perm = m.get("access") or m.get("permission")
                    if perm is None:
                        perm = "write" if m.get("write") else "read"
                    access_map.setdefault(str(mid), perm)
            else:
                access_map.setdefault(str(m), access_map.get(str(m), "read"))
    elif isinstance(raw_models, dict):
        for mid, val in raw_models.items():
            if isinstance(val, str):
                access_map[str(mid)] = val
            elif isinstance(val, bool):
                access_map[str(mid)] = "write" if val else "read"

    return {
        "id": group.get("id"),
        "name": group.get("name"),
        "description": group.get("description", ""),
        "user_ids": group.get("user_ids") or group.get("users", []),
        "model_ids": list(access_map.keys()),
        "model_permissions": access_map,
        "permissions": group.get("permissions", {}),
        "created_at": timestamp_to_datetime(
            group.get("created_at") or group.get("created")
        ),
        "updated_at": timestamp_to_datetime(
            group.get("updated_at") or group.get("updated")
        ),
    }


def get_groups():
    """Haalt alle groepen op inclusief hun modellen."""
    response = requests.get(f"{URL}/groups/", headers=HEADERS)
    if response.status_code != 200:
        return []

    try:
        data = response.json()
    except ValueError:
        return []

    if isinstance(data, dict):
        maybe_groups = data.get("groups", data)
        if isinstance(maybe_groups, dict):
            groups = list(maybe_groups.values())
        else:
            groups = maybe_groups
    else:
        groups = data

    detailed = []
    for g in groups:
        group_id = g.get("id")
        if group_id:
            detail = get_group_by_id(group_id)
            if isinstance(detail, dict) and "error" not in detail:
                g.update(detail)

        detailed.append(_format_group(g))

    return detailed


def create_group(name, description="", permissions=None):
    url = f"{URL}/groups/create"
    payload = {
        "name": name,
        "description": description,
        "permissions": permissions or {},
    }
    response = requests.post(url, json=payload, headers=JSON_HEADERS)
    return response.ok


def get_group_by_id(group_id):
    """Haalt één groep op en geeft het groepsobject terug.

    Sommige API versies sturen het resultaat verpakt in een "group" key. Deze
    functie ontdoet zich daarvan zodat de rest van de code altijd een enkel
    groepsdict ontvangt.
    """
    response = requests.get(f"{URL}/groups/id/{group_id}", headers=HEADERS)
    if response.status_code != 200:
        return {
            "error": f"Kon groep niet ophalen: {response.status_code} - {response.text}"
        }

    try:
        data = response.json()
    except ValueError:
        return {"error": "Ongeldig antwoord van server"}

    if (
        isinstance(data, dict)
        and "group" in data
        and isinstance(data["group"], dict)
    ):
        return data["group"]

    return data


def update_group(group):
    group_id = group.get("id")
    raw_permissions = group.get("model_permissions")
    model_permissions = {}
    if isinstance(raw_permissions, dict):
        for mid, perm in raw_permissions.items():
            model_permissions[str(mid)] = perm or "read"

    raw_models = group.get("model_ids")
    if not raw_models:
        raw_models = group.get("models", [])
    if isinstance(raw_models, list):
        for m in raw_models:
            if isinstance(m, dict):
                mid = m.get("id") or m.get("model_id") or m.get("name")
                if mid is not None and str(mid) not in model_permissions:
                    model_permissions[str(mid)] = (
                        "write" if m.get("write") else "read"
                    )
            else:
                if str(m) not in model_permissions:
                    model_permissions[str(m)] = "read"
    elif isinstance(raw_models, dict):
        for mid, val in raw_models.items():
            if str(mid) not in model_permissions:
                if isinstance(val, str):
                    model_permissions[str(mid)] = val
                elif isinstance(val, bool):
                    model_permissions[str(mid)] = "write" if val else "read"
    payload = {
        "name": group.get("name", ""),
        "description": group.get("description", ""),
        "user_ids": group.get("user_ids", []),
        "model_permissions": model_permissions,
    }
    response = requests.post(
        f"{URL}/groups/id/{group_id}/update", headers=HEADERS, json=payload
    )
    if response.status_code == 200:
        return {"success": "Groep bijgewerkt"}
    return {
        "error": f"Update mislukt: {response.status_code} - {response.text}"
    }


def delete_group(group_id):
    url = f"{URL}/groups/id/{group_id}/delete"
    response = requests.delete(url, headers=HEADERS)
    return response.ok


def add_user_to_group(group_id: str, user_id: str) -> dict:
    group = get_group_by_id(group_id)
    if "error" in group:
        return group

    user_ids = group.get("user_ids", [])
    if user_id in user_ids:
        return {"info": "Gebruiker zit al in deze groep."}

    user_ids.append(user_id)
    payload = {
        "name": group.get("name", ""),
        "description": group.get("description", ""),
        "user_ids": user_ids,
    }

    response = requests.post(
        f"{URL}/groups/id/{group_id}/update", headers=HEADERS, json=payload
    )
    if response.status_code == 200:
        return {"success": "Gebruiker toegevoegd aan groep."}
    return {
        "error": f"Toevoegen mislukt: {response.status_code} - {response.text}"
    }


def remove_user_from_group(group_id: str, user_id: str) -> dict:
    group = get_group_by_id(group_id)
    if "error" in group:
        return group

    user_ids = group.get("user_ids", [])
    if user_id not in user_ids:
        return {"info": "Gebruiker zit niet in deze groep."}

    user_ids.remove(user_id)
    payload = {
        "name": group.get("name", ""),
        "description": group.get("description", ""),
        "user_ids": user_ids,
    }

    response = requests.post(
        f"{URL}/groups/id/{group_id}/update", headers=HEADERS, json=payload
    )
    if response.status_code == 200:
        return {"success": "Gebruiker verwijderd uit groep."}
    return {
        "error": f"Verwijderen mislukt: {response.status_code} - {response.text}"
    }


def add_model_to_group(
    group_id: str, model_id: str, write: bool = False
) -> dict:
    group = get_group_by_id(group_id)
    if "error" in group:
        return group

    perms = group.get("model_permissions")
    if not isinstance(perms, dict):
        perms = {}
    current = perms.get(str(model_id))
    new_perm = "write" if write else "read"
    if current == new_perm:
        return {"info": "Model zit al in deze groep met dezelfde rechten."}

    perms[str(model_id)] = new_perm
    payload = {
        "name": group.get("name", ""),
        "description": group.get("description", ""),
        "user_ids": group.get("user_ids", []),
        "model_permissions": perms,
    }

    response = requests.post(
        f"{URL}/groups/id/{group_id}/update", headers=HEADERS, json=payload
    )
    if response.status_code == 200:
        return {"success": "Model toegevoegd aan groep."}
    return {
        "error": f"Toevoegen mislukt: {response.status_code} - {response.text}"
    }


def remove_model_from_group(group_id: str, model_id: str) -> dict:
    group = get_group_by_id(group_id)
    if "error" in group:
        return group

    perms = group.get("model_permissions")
    if not isinstance(perms, dict) or str(model_id) not in perms:
        return {"info": "Model zit niet in deze groep."}

    perms.pop(str(model_id))
    payload = {
        "name": group.get("name", ""),
        "description": group.get("description", ""),
        "user_ids": group.get("user_ids", []),
        "model_permissions": perms,
    }

    response = requests.post(
        f"{URL}/groups/id/{group_id}/update", headers=HEADERS, json=payload
    )
    if response.status_code == 200:
        return {"success": "Model verwijderd uit groep."}
    return {
        "error": f"Verwijderen mislukt: {response.status_code} - {response.text}"
    }