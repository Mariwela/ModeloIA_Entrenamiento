import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_country_performance(country: str):

    prompt = f"""
    Eres un analista experto en Juegos Olímpicos.

    Analiza el rendimiento histórico de {country} en los Juegos Olímpicos.
    Responde en máximo 3 párrafos.
    Sé claro, conciso y estructurado.
    No excedas 200 palabras.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Eres un analista deportivo experto en Juegos Olímpicos."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content