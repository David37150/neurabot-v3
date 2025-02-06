import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
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
