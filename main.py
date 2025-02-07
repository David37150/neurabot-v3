import os
import json
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI  # Nouvelle importation pour openai>=1.0.0

# Charger les variables d'environnement
dotenv_loaded = load_dotenv()
if not dotenv_loaded:
    print("⚠️ Erreur : Impossible de charger le fichier .env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

if not OPENAI_API_KEY:
    print("⚠️ Erreur : Clé OpenAI introuvable. Vérifie ton fichier .env !")
    exit()

if not SERPAPI_KEY:
    print("⚠️ Erreur : Clé SerpAPI introuvable. Vérifie ton fichier .env !")
    exit()

# Configurer le client OpenAI (nouvelle syntaxe)
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialiser FastAPI
app = FastAPI()

# ✅ Ajout du middleware CORS pour autoriser les requêtes depuis ton site
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://neurainvests.com"],  # Autoriser uniquement ton site
    allow_credentials=True,
    allow_methods=["GET"],  # Autoriser seulement les requêtes GET
    allow_headers=["*"],  # Autoriser tous les headers
)

# Charger les réponses stockées
def load_responses():
    if os.path.exists("reponses.json"):
        with open("reponses.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

responses = load_responses()

def search_web(query):
    """Recherche Google via SerpAPI"""
    try:
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "hl": "fr",
            "gl": "fr",
            "api_key": SERPAPI_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()
        return [res["snippet"] for res in data.get("organic_results", [])[:3]]  # Récupérer les 3 premiers résultats
    except Exception as e:
        print(f"❌ Erreur SerpAPI : {e}")
        return ["Je n'ai pas pu récupérer d'informations."]

@app.get("/")
def home():
    return {"message": "Bienvenue sur NeuraBot !"}

@app.get("/ask")
def ask(question: str):
    """Pose une question à NeuraBot"""
    try:
        # 1️⃣ Vérifier si la question a une réponse enregistrée
        if question in responses:
            prepared_response = responses[question]

            # Reformuler la réponse avec OpenAI
            reformulated_response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "Reformule cette réponse de manière plus naturelle et engageante."},
                    {"role": "user", "content": prepared_response}
                ]
            )
            return {"question": question, "response": reformulated_response.choices[0].message.content}

        # 2️⃣ Sinon, on cherche une réponse avec SerpAPI + OpenAI
        web_results = search_web(question)
        context = " ".join(web_results) if web_results else "Je n'ai rien trouvé."

        prompt = f"Réponds à cette question en te basant sur les informations suivantes : {context}\nQuestion : {question}\nRéponse :"
        
        # Réponse via OpenAI
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        return {"question": question, "response": response.choices[0].message.content}
    
    except Exception as e:
        return {"error": f"❌ Erreur : {str(e)}"}
