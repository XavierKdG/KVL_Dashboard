# 📊 KVL Dashboard

Een Streamlit-dashboard ontwikkeld bij KVL voor het beheren van AI-bestanden, kennisbanken en chatdata via diverse API-integraties (OpenWebUI, Ollama, interne kennisbank-API).

## 🚀 Functionaliteiten

- ✅ Uploaden van bestanden en koppelen aan kennisbanken
- ✅ Automatisch updaten van bestanden bij duplicaten (versiebeheer)
- ✅ Inzien van kennisbankinhoud met metadata
- ✅ Chatkanaalbeheer via OpenWebUI
- ✅ Weergave van berichten per kanaal
- ✅ Overzicht van beschikbare AI-modellen (via Ollama of OpenWebUI)
- ✅ Google OAuth-login (via Streamlit-auth)
- 🔒 API-key en authenticatieconfiguratie via `.env` en `secrets.toml`

## 🛠️ Installatie

1. **Clone de repository**

```bash
git clone https://github.com/XavierKdG/KVL_Dashboard.git
cd KVL_Dashboard

    Installeer dependencies

Bij voorkeur in een virtuele omgeving:

pip install -r requirements.txt

    Voeg .env toe

Plaats in de root van het project een .env met:

API_KEY=jouw_api_key

    Configureer Google OAuth (optioneel maar aanbevolen)

Maak .streamlit/secrets.toml aan met OIDC-configuratie voor login:

[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "geheime_waarde"

[auth.google]
client_id = "jouw_client_id.apps.googleusercontent.com"
client_secret = "jouw_client_secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

    Start het dashboard

streamlit run app.py

Indien streamlit niet herkend wordt:

python -m streamlit run app.py

✅ Vereisten

    Python 3.9 of hoger

    Streamlit >= 1.30

    Authlib geïnstalleerd (voor login):

    pip install Authlib

    OpenWebUI draait lokaal op poort 8081

    Eventueel: lokale Ollama-service voor modeloverzicht

🔒 Beveiliging & Authenticatie

    OAuth-authenticatie via Google (OpenID Connect)

    API-key vereist voor toegang tot backend

    CORS & cookiebeheer via Streamlit-auth handled automatisch
