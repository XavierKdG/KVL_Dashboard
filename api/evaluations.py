import requests
import pandas as pd 
import os
import datetime
from .config import URL, HEADERS, JSON_HEADERS, timestamp_to_datetime

def get_feedback():
    response = requests.get(f"{URL}/evaluations/feedbacks/all", headers=HEADERS)
    feedback = response.json()
    filtered_data = []

    for i in feedback:
        filtered_data.append({
            "model": i.get('data')
            })
        
    return filtered_data 