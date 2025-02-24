import streamlit as st
import requests

# URL de l'API de NeuraBot
API_URL = "https://neurabot-v3.onrender.com/ask"

# Interface utilisateur
st.set_page_config(page_title="NeuraBot", page_icon="🤖", layout="centered")

st.title("🤖 NeuraBot - Chat / ADS  IA Assistance")
st.write("Pose-moi une question et je vais chercher la réponse pour toi ! 🔍")

# Champ de saisie pour poser des questions
user_input = st.text_input("Votre question :", "")

if st.button("Poser la question"):
    if user_input:
        try:
            # Envoi de la requête à l'API
            response = requests.get(API_URL, params={"question": user_input})
            data = response.json()
            st.subheader("Réponse :")
            st.write(data.get("response", "❌ Erreur : Aucune réponse reçue."))
        except Exception as e:
            st.error(f"❌ Erreur lors de la requête : {e}")
    else:
        st.warning("Veuillez entrer une question avant d'envoyer !")






        
