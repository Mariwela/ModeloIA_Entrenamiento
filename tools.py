import os
import requests
from typing import Dict, Any
from datetime import datetime, timedelta

# --- 1. Herramienta OpenWeatherMap ---

def openweather_current(api_key: str, city_name: str, lang: str = 'es') -> Dict[str, Any]:
    """
    Obtiene los datos meteorológicos actuales para una ciudad.
    El idioma por defecto es el español (es).
    """
    if not api_key:
        return {"success": False, "error": "No se proporcionó la clave API de OpenWeatherMap."}
    
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "appid": api_key,
        "q": city_name,
        "units": "metric",
        "lang": lang
    }
    
    try:
        r = requests.get(BASE_URL, params=params, timeout=5)
        r.raise_for_status() # Lanza una excepción para errores 4xx/5xx
        data = r.json()
        
        # Extracción y formateo de datos clave
        description = data['weather'][0]['description']
        temp = data['main']['temp']
        
        result = (
            f"El clima actual en {city_name} es: {description}, "
            f"con una temperatura de {temp:.1f}°C."
        )
        return {"success": True, "result": result}
        
    except requests.exceptions.HTTPError as errh:
        return {"success": False, "error": f"Error HTTP: {errh}"}
    except requests.exceptions.RequestException as err:
        return {"success": False, "error": f"Error de conexión: {err}"}
    except Exception as e:
        return {"success": False, "error": f"Error desconocido: {e}"}


# --- 2. Herramienta NewsAPI ---

def newsapi_top_headlines(api_key: str, query: str = None):
    """
    Llama a NewsAPI usando el endpoint /v2/everything y amplía la búsqueda a los últimos 7 días.
    """
    if not api_key:
        return {"success": False, "error": "No se proporcionó la clave API para NewsAPI"}
    
    try:
        # Calcular la fecha de hace 7 días en formato YYYY-MM-DD (para la ventana de búsqueda)
        days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Parámetros base para la búsqueda 'everything'
        params = {
            "apiKey": api_key, 
            "pageSize": 5, # Máximo 5 artículos
            "sortBy": "relevancy",
            "from": days_ago,       # <-- Amplía la ventana de búsqueda a 7 días
            "language": "es"        # Buscar solo noticias en español
        }
        
        if query:
            params["q"] = query
            
        BASE_URL = "https://newsapi.org/v2/everything"
        r = requests.get(BASE_URL, params=params, timeout=6)
        r.raise_for_status()
        data = r.json()
        
        articles = []
        if data.get("articles"):
            # Formatear el título y la fuente
            articles = [
                f"'{a.get('title')}' (Fuente: {a.get('source', {}).get('name')})" 
                for a in data.get("articles", [])
            ]
        
        if not articles:
            return {"success": True, "result": "(No se encontraron artículos relevantes en español en los últimos 7 días.)"}
            
        summary = "Se encontraron los siguientes titulares:\n" + "\n".join(articles)
        return {"success": True, "result": summary}
        
    except requests.exceptions.HTTPError as errh:
        # Este error puede ser un 401 (API Key inválida) o 429 (Límite de peticiones)
        return {"success": False, "error": f"Error HTTP: {errh}"}
    except Exception as e:
        return {"success": False, "error": f"Error al acceder a NewsAPI: {e}"}