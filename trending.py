import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pytrends.request import TrendReq  
from time import sleep

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

# Configuration de Google Trends
pytrends = TrendReq(hl="fr-FR", tz=360, retries=5, backoff_factor=0.2)

# Catégories Google Trends
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

# Récupération des produits depuis NeuraMarkets
def fetch_products():
    try:
        url = "https://neuramarkets.com/api/products"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Erreur récupération produits: {e}")
        return []

# Obtenir la tendance d'un produit via Google Trends
def get_trend_score(product_name, category=0, geo='FR'):
    try:
        pytrends.build_payload([product_name], cat=category, timeframe="today 3-m", geo=geo, gprop="")
        trend_data = pytrends.interest_over_time()
        if not trend_data.empty:
            return trend_data[product_name].mean()
        return 0
    except Exception as e:
        print(f"❌ Erreur Google Trends pour {product_name}: {e}")
        return 0

# Endpoint API pour récupérer les produits tendances filtrés
@app.get("/trending-products")
def trending_products(category: str = "Beauté", geo: str = "France"):
    if category not in CATEGORIES or geo not in GEO_LOCATIONS:
        return {"error": "❌ Catégorie ou pays invalide."}

    products = fetch_products()
    if not products:
        return {"error": "❌ Aucune donnée produit récupérée."}

    ranked_products = []
    for idx, product in enumerate(products):
        name = product.get("name")
        trend_score = get_trend_score(name, CATEGORIES[category], GEO_LOCATIONS[geo])
        ranked_products.append({
            "name": name,
            "trend_score": trend_score,
            "url": product.get("url")
        })

        # 🕒 Pause de 3 secondes entre chaque requête
        sleep(3)

    ranked_products.sort(key=lambda x: x["trend_score"], reverse=True)

    return {"trending_products": ranked_products[:10]}
