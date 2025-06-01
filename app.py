# KVL Dashboard met OpenWebUI API Endpoints
# Voor gebruik installeer bijbehorende requirements
# in de .env file vermeld ik de API KEY
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')

print(API_KEY)
