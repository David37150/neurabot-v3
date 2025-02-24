import os
import json
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pytrends.request import TrendReq  # 🔹 Import pour Google Trends
from shopping_insights import get_shopping_insights  # ✅ Import ajouté

# ✅ Charger les variables d'environnement (depuis Render)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_PASSWORD = os.getenv("SHOPIFY_PASSWORD")
SHOPIFY_STORE_NAME = os.getenv("SHOPIFY_STORE_NAME")

# ✅ Vérification des clés API (évite le crash complet)
missing_keys = []
if not OPENAI_API_KEY:
    missing_keys.append("OPENAI_API_KEY")
if not SERPAPI_KEY:
    missing_keys.append("SERPAPI_KEY")
if not SHOPIFY_API_KEY:
    missing_keys.append("SHOPIFY_API_KEY")
if not SHOPIFY_PASSWORD:
    missing_keys.append("SHOPIFY_PASSWORD")
if not SHOPIFY_STORE_NAME:
    missing_keys.append("SHOPIFY_STORE_NAME")

if missing_keys:
    print(f"⚠️ Erreur : Clés API manquantes {', '.join(missing_keys)}")

# ✅ Configurer le client OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ Initialiser FastAPI
app = FastAPI()

# ✅ Activer CORS pour autoriser les requêtes de ton site
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
    url_reponses = "https://neurainvests.com/neurabot/reponses.json"
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
        return [res["snippet"] for res in data.get("organic_results", [])[:3]]
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
        keywords = ["neurainvests", "neuraInvests", "neurabot", "neura bot"]
        if any(word in question.lower() for word in keywords):
            local_response = get_local_response(question)
            if local_response:
                return {"question": question, "response": local_response}
            
            # Si pas de réponse locale, chercher sur le site officiel
            neurainvests_response = search_neurainvests(question)
            if neurainvests_response:
                return {"question": question, "response": neurainvests_response}

        # Recherche web si aucune réponse locale trouvée
        web_results = search_web(question)
        context = " ".join(web_results) if web_results else "Je n'ai rien trouvé."

        prompt = f"Réponds à cette question en te basant sur les informations suivantes : {context}\nQuestion : {question}\nRéponse :"
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        return {"question": question, "response": response.choices[0].message.content}
    except Exception as e:
        return {"error": f"❌ Erreur : {str(e)}"}

# ✅ ROUTE PRODUITS TENDANCE

# ✅ ROUTE PRODUITS TENDANCE (SHOPIFY + GOOGLE TRENDS + SHOPPING INSIGHTS)

def get_shopify_products():
    """Récupère les produits depuis Shopify"""
    try:
        shopify_url = f"https://{SHOPIFY_STORE_NAME}.myshopify.com/admin/api/2023-01/products.json"
        
        headers = {
            "X-Shopify-Access-Token": SHOPIFY_PASSWORD  # Utilisation du token au lieu du password
        }

        response = requests.get(shopify_url, headers=headers, verify=False)  # ⚠️ Désactiver SSL temporairement

        if response.status_code == 200:
            return [product["title"] for product in response.json().get("products", [])]
        else:
            print(f"⚠️ Erreur Shopify : {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des produits Shopify : {e}")
        return []

def get_trending_score(product_name):
    """Analyse la popularité avec Google Trends"""
    try:
        pytrends = TrendReq(hl='fr-FR', tz=360)
        pytrends.build_payload([product_name], timeframe='today 3-m', geo='FR')
        trends_data = pytrends.interest_over_time()
        return trends_data[product_name].mean() if not trends_data.empty else 0
    except Exception as e:
        print(f"❌ Erreur Google Trends : {e}")
        return 0

@app.get("/trending-products")
def trending_products():
    products = get_shopify_products()
    trending = sorted(
        [{"nom": p, "score_tendance": get_trending_score(p)} for p in products],
        key=lambda x: x["score_tendance"], reverse=True
    )[:10]
    return {"trending_products": trending}

@app.get("/shopping-insights")
def shopping_insights(keyword: str, geo: str = "FR"):
    insights = get_shopping_insights(keyword, geo)
    return insights if insights else {"error": "❌ Erreur Shopping Insights"}
