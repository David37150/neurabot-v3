import requests

def get_shopping_insights(keyword, geo="FR"):
    url = "https://shopping.thinkwithgoogle.com/api/trends/v1/productinsights"
    params = {
        "keyword": keyword,
        "geo": geo,
        "category": "all"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Erreur Shopping Insights : {e}")
        return None
