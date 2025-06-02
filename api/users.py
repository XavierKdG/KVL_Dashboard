import requests
import pandas as pd 
import os
import datetime
from .config import URL, HEADERS, JSON_HEADERS, timestamp_to_datetime

def get_users():
    url = f"{URL}/users/all"
    response = requests.get(url, headers=HEADERS)
    gebruikers = response.json()
    gebruiker_data  = []

    # for i in gebruikers:
    #     gebruiker_data.append({
    #             "Naam": i.get("name"),
    #             "Email": i.get("email"),
    #             "Geüpload op": timestamp_to_datetime(i.get("created_at")),
    #             "Bijgewerkt op": timestamp_to_datetime(i.get("updated_at")),
    #             "Laatst actief": timestamp_to_datetime(i.get("last_active"))
    #         })

    return response.json()


    


