import time
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pytrends.request import TrendReq  

# Initialiser FastAPI
app = FastAPI()

# Activer CORS pour permettre les requêtes depuis ton site
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://neuramarkets.com", "https://neurainvests.com"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Liste des catégories Google Trends
CATEGORIES = {
    "Beauté": 44,
    "Santé": 45,
    "Mode": 185,
    "Électronique": 78,
    "Informatique": 31,
    "Enfant / Bébé": 137,
    "Électroménager": 141,
    "Sport": 20
}

# Pays disponibles
GEO_LOCATIONS = {
    "France": "FR",
    "Europe": "",
    "USA": "US"
}

# Fonction pour récupérer les produits de NeuraMarkets
def fetch_products():
    try:
        url = "https://neuramarkets.com/api/products"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ Erreur récupération produits: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return []

# Fonction pour obtenir la tendance d'un produit via Google Trends avec gestion des pauses
def get_trend_score(product_name, category=0, geo='FR'):
    try:
        pytrends = TrendReq(hl="fr-FR", tz=360)
        pytrends.build_payload([product_name], cat=category, timeframe="today 3-m", geo=geo, gprop="")
        trend_data = pytrends.interest_over_time()
        time.sleep(2)  # pause de sécurité de 2 secondes
        if not trend_data.empty:
            return trend_data[product_name].mean()
        return 0
    except Exception as e:
        print(f"❌ Erreur Google Trends pour '{product_name}': {e}")
        return 0

# Endpoint API optimisé pour éviter l'erreur 429
@app.get("/trending-products")
def trending_products(category: str = "Beauté", geo: str = "France"):
    if category not in CATEGORIES or geo not in GEO_LOCATIONS:
        return {"error": "❌ Catégorie ou pays invalide."}

    products = fetch_products()
    if not products:
        return {"error": "❌ Aucune donnée produit récupérée."}

    # Limiter à 5 produits pour éviter les erreurs 429
    ranked_products = []
    for product in products[:5]:
        name = product.get("name")
        url = product.get("url")
        trend_score = get_trend_score(name, CATEGORIES[category], GEO_LOCATIONS[geo])
        ranked_products.append({
            "name": name,
            "trend_score": trend_score,
            "url": url
        })

    ranked_products.sort(key=lambda x: x["trend_score"], reverse=True)

    return {"trending_products": ranked_products}
