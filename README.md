# KVL Dashboard

Een Streamlit-dashboard voor het visualiseren van data uit OpenWebUI API's, gebouwd als onderdeel van een stageproject bij KVL. Het dashboard toont informatie over chatkanalen, berichten en beschikbare modellen binnen een lokale OpenWebUI-instantie.

## 🔧 Functionaliteiten

- ✅ Overzicht van alle chatkanalen met laatste activiteit
- ✅ Weergave van berichten in een geselecteerd kanaal
- ✅ Lijst van beschikbare AI-modellen (via Ollama of OpenWebUI API)
- 🔜 Upload en verwerking van bestanden (in ontwikkeling)
- 🔒 Autorisatie via API-key (.env)

## 📦 Installatie

1. **Clone deze repository**

```bash
git clone https://github.com/XavierKdG/KVL_Dashboard.git
cd kvl-dashboard
````

2. **Installeer dependencies**

Zorg dat je een virtuele omgeving gebruikt (aanbevolen), en installeer vervolgens:

```bash
pip install -r requirements.txt
```

3. **Voeg een `.env` bestand toe**

Maak een `.env` bestand aan in de root van je project en voeg hierin je API-key toe:

```env
API_KEY=jouw_api_key_hier
```

4. **Start het dashboard**

```bash
streamlit run app.py
```

*Als `streamlit` niet herkend wordt, probeer dan:*

```bash
python -m streamlit run app.py
```

## 📡 API Endpoints (OpenWebUI)

De data wordt opgehaald uit de [OpenWebUI API](http://localhost:8081/api/v1), onder andere via:

* `GET /channels/` — lijst van kanalen
* `GET /channels/{id}/messages` — berichten in een kanaal
* `GET /models/` — beschikbare AI-modellen

## 📌 Vereisten

* Python 3.8 of hoger
* OpenWebUI lokaal draaiend op port `8081`
* API-key in `.env` bestand

