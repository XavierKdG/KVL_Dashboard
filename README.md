# 📊 KVL Dashboard

Een Streamlit-dashboard ontwikkeld bij KVL voor het beheren van AI-bestanden, kennisbanken en chatdata via diverse API-integraties (OpenWebUI, Ollama, interne kennisbank-API).

## 🚀 Functionaliteiten

- ✅ Uploaden van bestanden en koppelen aan kennisbanken  
- ✅ Automatisch updaten van bestanden bij duplicaten (versiebeheer)  
- ✅ Inzien van kennisbankinhoud met metadata
- ✅ Detailweergave van bestanden inclusief content type en collectie
- ✅ Chatkanaalbeheer via OpenWebUI  
- ✅ Weergave van berichten per kanaal  
- ✅ Overzicht van beschikbare AI-modellen  
- ✅ Google OAuth-login (via Streamlit-auth)  
- 🔒 API-key en authenticatieconfiguratie via `.env` en `secrets.toml`  

## 🛠️ Installatie

1. **Clone de repository**

```bash
git clone https://github.com/XavierKdG/KVL_Dashboard.git
cd KVL_Dashboard
```

2. **Installeer dependencies**

Bij voorkeur in een virtuele omgeving:

```bash
pip install -r requirements.txt
```

3. **Voeg `.env` toe**

Plaats in de root van het project een `.env` bestand met daarin:

```env
API_KEY=jouw_api_key
```

4. **Configureer Google OAuth (optioneel maar aanbevolen)**

Maak `.streamlit/secrets.toml` aan met de volgende inhoud:

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "geheime_waarde"

[auth.google]
client_id = "jouw_client_id.apps.googleusercontent.com"
client_secret = "jouw_client_secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

5. **Start het dashboard**

```bash
streamlit run 🏠Main.py
```

Indien `streamlit` niet wordt herkend:

```bash
python -m streamlit run 🏠Main.py
```

6. **Met Docker**

```bash
docker-compose up --build
```

## ✅ Vereisten

* Python 3.9 of hoger
* Streamlit >= 1.30
* Authlib geïnstalleerd (voor login):

```bash
pip install Authlib
```

* OpenWebUI draait lokaal op poort `8080`
* (Optioneel) Lokale Ollama-service voor modeloverzicht

## 🔒 Beveiliging & Authenticatie

* OAuth-authenticatie via Google (OpenID Connect)
* API-key vereist voor toegang tot backend
* CORS & cookiebeheer automatisch geregeld via Streamlit-auth


