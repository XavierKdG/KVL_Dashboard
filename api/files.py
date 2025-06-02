import requests
import pandas as pd 
import os
import datetime
from .config import URL, HEADERS, JSON_HEADERS, timestamp_to_datetime

def upload_file(file_object):

    upload_url = f"{URL}/files/"
    files = {"file": (file_object.name, file_object, file_object.type)}
    response = requests.post(upload_url, headers=HEADERS, files=files)

    if response.status_code != 200:
        return {"error": f"Upload mislukt: {response.status_code} - {response.text}"}

    return {"file_id": response.json().get("id")}
