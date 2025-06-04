import requests
import pandas as pd 
import os
import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')
URL = 'http://localhost:8080/api/v1' # verander zodra openwebui op domein gehost is
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
JSON_HEADERS = {**HEADERS, "Content-Type": "application/json"}

def timestamp_to_datetime(ts):
    """Converteer diverse timestamp-formaten naar een leesbare datum."""
    if ts is None:
        return "-"

    try:
        ts_val = float(ts)
    except Exception:
        return "ongeldige datum"

    if ts_val <= 0:
        return "-"
    if ts_val > 1e18: 
        ts_val /= 1_000_000_000
    elif ts_val > 1e15:  
        ts_val /= 1_000_000
    elif ts_val > 1e12:  
        ts_val /= 1_000

    try:
        return datetime.datetime.fromtimestamp(ts_val).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "ongeldige datum"

def tijd_verschil_als_tekst(dt_string):
    try:
        dt = pd.to_datetime(dt_string)
    except Exception:
        return dt_string or "-" 

    delta = datetime.datetime.now() - dt
    sec = delta.total_seconds()

    if sec < 60:
        return f"{int(sec)} sec geleden"
    elif sec < 3600:
        return f"{int(sec // 60)} min geleden"
    elif sec < 86400:
        return f"{int(sec // 3600)} uur geleden"
    elif sec < 604800:
        return f"{int(sec // 86400)} dagen geleden"
    else:
        return dt.strftime("%Y-%m-%d")  
