from fastapi import FastAPI
import openai
import os
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Bienvenue sur NeuraBot !"}

@app.get("/ask")
def ask(question: str):
    """Pose une question à NeuraBot"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": question}]
        )
        return {"question": question, "response": response["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"error": str(e)}
