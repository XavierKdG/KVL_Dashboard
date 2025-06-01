# KVL Dashboard met OpenWebUI API Endpoints
# Voor gebruik installeer bijbehorende requirements (pip install -r requirements.txt)
# in de .env file vermeld ik de API KEY
import requests
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

URL = 'http://localhost:8081/api/v1'
API_KEY = os.getenv('API_KEY')

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
}

# def get_messages(channel_id):
#     response = requests.get(f"{URL}/channels/{channel_id}/messages", headers=HEADERS)
#     return response.json()

def get_channels():
    response = requests.get(f"{URL}/channels/", headers=HEADERS)
    channels = response.json()
    filtered_data = []

    for i in channels:
        updated_at = i.get('updated_at')
        updated_at = updated_at / 1_000_000_000
        updated_at = datetime.datetime.fromtimestamp(updated_at).strftime("%Y-%m-%d %H:%M:%S") 

        filtered_data.append({
            "channel_naam": i.get('name'),
            "laatst_bijgewerkt": updated_at,
            })
        
    return filtered_data 

if __name__ == "__main__":
    # messages = get_messages("d968f28b-26e4-40c5-aea9-558c964b01d9")
    channels = get_channels()
    # print(messages)
    print(channels)
