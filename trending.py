import os
import requests
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pytrends.request import TrendReq  # 📌 Pour interagir avec Google Trends
from shopping_insights import get_shopping_insights  # 📌 Ajout import Shopping Insights

# Initialiser FastAPI
app = FastAPI()

# Activer CORS pour NeuraMarkets
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://neuramarkets.com"],  # Autoriser seulement ce site
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Configuration de Google Trends
pytrends = TrendReq(hl="fr-FR", tz=360)

# 🔍 Fonction pour récupérer les produits de NeuraMarkets (API ou Scraping)
def fetch_products():
    try:
        url = "https://neuramarkets.com/api/products"  # 📌 Adapter selon ton site
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ Erreur lors de la récupération des produits : {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Impossible d'obtenir les produits : {e}")
        return []

# 🔥 Fonction pour analyser la tendance d'un produit sur Google Trends
def get_trend_score(product_name):
    try:
        pytrends.build_payload([product_name], cat=0, timeframe="now 7-d", geo="FR", gprop="")
        trend_data = pytrends.interest_over_time()

        if not trend_data.empty:
            return trend_data[product_name].mean()  # 📌 Score moyen sur 7 jours
        return 0
    except Exception as e:
        print(f"❌ Erreur Google Trends pour {product_name}: {e}")
        return 0

# 🔝 Route API pour récupérer les produits tendances
@app.get("/trending-products")
def trending_products():
    products = fetch_products()
    if not products:
        return {"error": "❌ Aucune donnée produit récupérée."}

    # 🔎 Analyse des tendances
    ranked_products = []
    for product in products:
        name = product.get("name")
        trend_score = get_trend_score(name)
        ranked_products.append({"name": name, "trend_score": trend_score, "url": product.get("url")})

    # 🔢 Trier par popularité décroissante
    ranked_products.sort(key=lambda x: x["trend_score"], reverse=True)

    return {"trending_products": ranked_products}

# 📌 Nouvelle route API pour Google Shopping Insights
@app.get("/shopping-insights")
def shopping_insights(keyword: str, geo: str = "FR"):
    insights = get_shopping_insights(keyword, geo)
    if insights:
        return insights
    else:
        return {"error": "Impossible de récupérer les données Shopping Insights"}
