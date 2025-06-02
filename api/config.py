import requests
import pandas as pd 
import os
import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')
URL = 'http://localhost:8081/api/v1'
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
JSON_HEADERS = {**HEADERS, "Content-Type": "application/json"}

def timestamp_to_datetime(ts):
    if not ts or ts <= 0:
        return "-"

    if ts > 1e12:
        ts = ts / 1_000_000_000
    try:
        return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "ongeldige datum"