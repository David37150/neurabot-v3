import os
import json
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

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

# Configurer le client OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialiser FastAPI
app = FastAPI()

# Activer CORS pour autoriser les requêtes de ton site
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://neurainvests.com"],  # Autoriser uniquement ton site
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ✅ Charger les réponses enregistrées dans `reponses.json`
def load_responses():
    """Charge `reponses.json` depuis ton site."""
    url_reponses = "https://neurainvests.com/neurabot/reponses.json"  # 🔗 URL de ton fichier
    try:
        response = requests.get(url_reponses)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ Erreur de chargement de `reponses.json` : {response.status_code}")
            return {}
    except Exception as e:
        print(f"❌ Impossible de charger `reponses.json` : {e}")
        return {}

responses = load_responses()

def get_local_response(question):
    """Cherche une réponse locale dans `reponses.json` et la reformule via OpenAI."""
    for key, value in responses.items():
        if key.lower() in question.lower():
            # ✅ Reformuler la réponse avec OpenAI
            prompt = f"Reformule cette réponse de manière plus naturelle et engageante : {value}"
            try:
                response = client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"❌ Erreur lors de la reformulation OpenAI : {e}")
                return value  # Si OpenAI échoue, on retourne la réponse brute

    return None  # Si aucune réponse trouvée

def search_neurainvests(question):
    """Effectue une recherche sur NeuraInvests en dernier recours."""
    try:
        url = f"https://neurainvests.com/search?q={question}"
        response = requests.get(url)
        if response.status_code == 200:
            return f"Consultez cette page pour plus d’informations : {url}"
        else:
            return None
    except Exception as e:
        print(f"❌ Erreur lors de la recherche sur NeuraInvests : {e}")
        return None

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
        # Vérifier si la question concerne NeuraInvests
        keywords = ["neurainvests", "neuraInvests", "neurabot", "neura bot"]
        if any(word in question.lower() for word in keywords):
            local_response = get_local_response(question)
            if local_response:
                return {"question": question, "response": local_response}
            
            # Si pas de réponse locale, chercher sur le site officiel
            neurainvests_response = search_neurainvests(question)
            if neurainvests_response:
                return {"question": question, "response": neurainvests_response}

        # Sinon, effectuer une recherche sur le web
        web_results = search_web(question)
        context = " ".join(web_results) if web_results else "Je n'ai rien trouvé."

        prompt = f"Réponds à cette question en te basant sur les informations suivantes : {context}\nQuestion : {question}\nRéponse :"
        
        # Nouvelle syntaxe OpenAI
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        return {"question": question, "response": response.choices[0].message.content}
    except Exception as e:
        return {"error": f"❌ Erreur : {str(e)}"}
