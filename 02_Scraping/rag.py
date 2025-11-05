import os
import re
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import google.generativeai as genai

# =============================
# 🔧 CONFIGURACIÓN INICIAL
# =============================

load_dotenv()  # Carga GOOGLE_API_KEY desde .env
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("❌ Falta la variable de entorno GOOGLE_API_KEY.")

# Configurar Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# =============================
# 📦 CLASE PRINCIPAL DEL RAG
# =============================

class RAG:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_collection("olympic_medals")
        self.df = pd.read_csv("./olympic_medals_2000_2024.csv")
        self.model = "models/gemini-2.5-flash"

        # ==============================
        # 🌍 Diccionario de alias de países
        # ==============================
        self.country_aliases = {
            "eeuu": "United States",
            "estados unidos": "United States",
            "usa": "United States",
            "canadá": "Canada",
            "méxico": "Mexico",
            "mexico": "Mexico",
            "brasil": "Brazil",
            "argentina": "Argentina",
            "chile": "Chile",
            "colombia": "Colombia",
            "perú": "Peru",
            "venezuela": "Venezuela",
            "uruguay": "Uruguay",
            "paraguay": "Paraguay",
            "ecuador": "Ecuador",
            "bolivia": "Bolivia",
            "cuba": "Cuba",
            "puerto rico": "Puerto Rico",
            "república dominicana": "Dominican Republic",
            "dominicana": "Dominican Republic",
            "panamá": "Panama",
            "panama": "Panama",
            "costa rica": "Costa Rica",
            "costarica": "Costa Rica",
            "españa": "Spain",
            "francia": "France",
            "alemania": "Germany",
            "reino unido": "Great Britain",
            "gran bretaña": "Great Britain",
            "inglaterra": "Great Britain",
            "irlanda": "Ireland",
            "portugal": "Portugal",
            "italia": "Italy",
            "suiza": "Switzerland",
            "bélgica": "Belgium",
            "belgica": "Belgium",
            "países bajos": "Netherlands",
            "holanda": "Netherlands",
            "luxemburgo": "Luxembourg",
            "mónaco": "Monaco",
            "monaco": "Monaco",
            "rusia": "ROC",
            "federación rusa": "ROC",
            "russian olympic committee": "ROC",
            "ucrania": "Ukraine",
            "polonia": "Poland",
            "chequia": "Czech Republic",
            "república checa": "Czech Republic",
            "eslovaquia": "Slovakia",
            "hungría": "Hungary",
            "rumanía": "Romania",
            "rumania": "Romania",
            "bulgaria": "Bulgaria",
            "serbia": "Serbia",
            "croacia": "Croatia",
            "eslovenia": "Slovenia",
            "bosnia": "Bosnia and Herzegovina",
            "albania": "Albania",
            "grecia": "Greece",
            "turquía": "Turkey",
            "turquia": "Turkey",
            "sudáfrica": "South Africa",
            "sudafrica": "South Africa",
            "nigeria": "Nigeria",
            "kenia": "Kenya",
            "etiopía": "Ethiopia",
            "etiopia": "Ethiopia",
            "egipto": "Egypt",
            "marruecos": "Morocco",
            "túnez": "Tunisia",
            "argelia": "Algeria",
            "ghana": "Ghana",
            "camerún": "Cameroon",
            "senegal": "Senegal",
            "uganda": "Uganda",
            "zimbabue": "Zimbabwe",
            "china": "China",
            "japón": "Japan",
            "corea del sur": "South Korea",
            "corea del norte": "North Korea",
            "india": "India",
            "indonesia": "Indonesia",
            "malasia": "Malaysia",
            "filipinas": "Philippines",
            "singapur": "Singapore",
            "vietnam": "Vietnam",
            "tailandia": "Thailand",
            "qatar": "Qatar",
            "arabia saudita": "Saudi Arabia",
            "emiratos árabes unidos": "United Arab Emirates",
            "israel": "Israel",
            "kazajistán": "Kazakhstan",
            "uzbekistán": "Uzbekistan",
            "irán": "Iran",
            "iraq": "Iraq",
            "siria": "Syria",
            "taiwán": "Chinese Taipei",
            "hong kong": "Hong Kong",
            "mongolia": "Mongolia",
            "pakistán": "Pakistan",
            "australia": "Australia",
            "nueva zelanda": "New Zealand",
            "fiyi": "Fiji",
            "samoa": "Samoa",
            "papúa nueva guinea": "Papua New Guinea",
            "roc": "ROC",
            "urss": "ROC",
            "china taipei": "Chinese Taipei",
            "hong-kong": "Hong Kong",
            "kosovo": "Kosovo",
            "macedonia del norte": "North Macedonia",
            "palestina": "Palestine",
        }

    # -------------------------
    # 🔍 Preguntas numéricas simples
    # -------------------------
    def detect_top_country_question(self, query: str):
        q = query.lower()

        # --- EXTRAER AÑO ---
        year_match = re.search(r"20\d{2}", q)
        year = int(year_match.group()) if year_match else self.df["year"].max()

        subset = self.df[self.df["year"] == year]
        if subset.empty:
            return f"No hay datos disponibles del año {year}.", []

        # --- PREGUNTAS SOBRE MEDALLAS ---
        if "más medallas" in q:
            if "oro" in q:
                metric = "gold"
            elif "plata" in q:
                metric = "silver"
            elif "bronce" in q:
                metric = "bronze"
            else:
                metric = "total"

            top = subset.sort_values(by=metric, ascending=False).iloc[0]
            return (
                f"En {year}, **{top['country']}** fue el país con más medallas de {metric}, con **{top[metric]} medallas**.",
                [f"Year: {year} | Country: {top['country']} | Rank: {top['rank']} | Gold: {top['gold']}, Silver: {top['silver']}, Bronze: {top['bronze']}, Total: {top['total']}"]
            )

        # --- PREGUNTAS SOBRE RANKING / POSICIÓN ---
        if any(x in q for x in ["ranking", "posición", "puesto", "quedó", "primer", "segundo", "tercer", "último", "peor"]):
            # Determinar posición buscada
            if "primer" in q or "primero" in q:
                pos = 1
            elif "segundo" in q:
                pos = 2
            elif "tercer" in q or "tercero" in q:
                pos = 3
            elif "último" in q or "peor" in q:
                pos = len(subset)
            else:
                pos = 1  # por defecto, el primero

            subset_sorted = subset.sort_values(by="rank", ascending=True)
            if pos > len(subset_sorted):
                return f"No hay suficientes países registrados para mostrar la posición {pos}.", []

            country = subset_sorted.iloc[pos - 1]
            position_text = (
                "primer" if pos == 1 else
                "segundo" if pos == 2 else
                "tercer" if pos == 3 else
                "último"
            )

            return (
                f"En {year}, **{country['country']}** ocupó el {position_text} lugar en el ranking olímpico (posición {country['rank']}).",
                [f"Year: {year} | Country: {country['country']} | Rank: {country['rank']} | Gold: {country['gold']}, Silver: {country['silver']}, Bronze: {country['bronze']}, Total: {country['total']}"]
            )

        # --- Ningún patrón detectado ---
        return None, None

    # -------------------------
    # 🔎 Recuperación semántica
    # -------------------------
    def retrieve_context(self, query: str, year_filter=None):
        query_text = query
        if year_filter:
            query_text += f" año {year_filter}"

        results = self.collection.query(query_texts=[query_text], n_results=10)
        documents = results.get("documents", [[]])[0]
        return documents

    # -------------------------
    # 💬 Generación con Gemini
    # -------------------------
    def generate_answer(self, query: str, context: str):
        try:
            model = genai.GenerativeModel(self.model)
            prompt = (
                f"Usa la siguiente información del medallero olímpico para responder de forma breve y precisa.\n\n"
                f"Contexto:\n{context}\n\n"
                f"Pregunta: {query}"
            )
            response = model.generate_content(prompt)
            return response.text if hasattr(response, "text") else str(response)
        except Exception as e:
            return f"⚠️ Error al usar Google GenAI: {e}"

    # -------------------------
    # 🧠 Lógica principal del RAG
    # -------------------------
    def answer_question(self, query: str):
        q_lower = query.lower()
        for alias, real_name in self.country_aliases.items():
            if alias in q_lower:
                query = query.replace(alias, real_name)
                break        
        # Paso 1: respuesta estructurada
        direct_answer, direct_docs = self.detect_top_country_question(query)
        if direct_answer:
            return direct_answer, direct_docs

        # Paso 2: detectar año
        year_match = re.search(r"20\d{2}", query)
        year_filter = int(year_match.group()) if year_match else None

        # Paso 3: recuperar contexto
        documents = self.retrieve_context(query, year_filter)
        context = "\n".join(documents[:10])

        # Paso 4: generar respuesta con modelo
        answer = self.generate_answer(query, context)

        return answer, documents[:10]
