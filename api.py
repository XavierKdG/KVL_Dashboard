# KVL Dashboard met OpenWebUI API Endpoints
# Voor gebruik installeer bijbehorende requirements
# in de .env file vermeld ik de API KEY
import requests
import os
from dotenv import load_dotenv

load_dotenv()

URL = 'http://localhost:8081/api/v1'
API_KEY = os.getenv('API_KEY')

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
}

def get_messages(channel_id):
    response = requests.get(f"{URL}/channels/{channel_id}/messages", headers=HEADERS)
    return response.json()

if __name__ == "__main__":
    messages = get_messages("d968f28b-26e4-40c5-aea9-558c964b01d9")
    print(messages)
