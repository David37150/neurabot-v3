import streamlit as st
import requests
import os

# URL de l'API
API_URL = "https://neurabot-v3.onrender.com/trending-products"

# Récupérer la clé API depuis l'environnement Render
SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")

st.title("🔥 Produits Tendance - NeuraMarkets")

# **Liste des catégories**
categories = ["Beauté", "Santé", "Mode", "Électronique", "Informatique", "Enfant / Bébé", "Électroménager", "Sport"]

# **Liste des zones géographiques**
geo_options = ["France", "Europe", "USA"]

# **Interface utilisateur**
selected_category = st.selectbox("Catégorie :", categories)
selected_geo = st.selectbox("Zone géographique :", geo_options)

if st.button("Afficher les produits tendance"):
    params = {
        "category": selected_category,
        "geo": selected_geo,
        "api_key": SCRAPER_API_KEY  # Inclusion sécurisée de la clé API dans les requêtes
    }

    with st.spinner('⏳ Récupération des produits tendances en cours...'):
        try:
            response = requests.get(API_URL, params=params)
            response.raise_for_status()  # Vérifie si la réponse HTTP est valide

            data = response.json()

            if "trending_products" in data and data["trending_products"]:
                trending = data["trending_products"]
                st.subheader(f"🔝 Top Produits - {selected_category} en {selected_geo}")
                for i, product in enumerate(trending, start=1):
                    st.markdown(f"{i}. **[{product['name']}]({product['url']})** – "
                                f"Score : {round(product['trend_score'], 2)}")
            else:
                st.warning("⚠️ Aucun produit tendance trouvé pour cette sélection.")

        except requests.exceptions.RequestException as req_err:
            st.error(f"❌ Erreur de requête HTTP : {req_err}")

        except ValueError as json_err:
            st.error(f"❌ Erreur de décodage JSON : {json_err}")

        except Exception as e:
            st.error(f"❌ Une erreur inattendue s'est produite : {e}")
