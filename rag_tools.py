import pandas as pd
import re
from typing import Dict, Any, List

SPANISH_TO_ENGLISH_MAP = {
    # ----------------------------------------
    # I. Américas (Norte, Centro y Sur)
    # ----------------------------------------
    "estados unidos": "United States",
    "eeuu": "United States",
    "canada": "Canada",
    "canadá": "Canada",
    "mexico": "Mexico",
    "méxico": "Mexico",
    "cuba": "Cuba",
    "puerto rico": "Puerto Rico",
    "haiti": "Haiti",
    "haití": "Haiti",
    "jamaica": "Jamaica",
    "dominicana": "Dominican Republic",
    "republica dominicana": "Dominican Republic",
    "argentina": "Argentina",
    "brasil": "Brazil",
    "chile": "Chile",
    "colombia": "Colombia",
    "ecuador": "Ecuador",
    "paraguay": "Paraguay",
    "peru": "Peru",
    "perú": "Peru",
    "uruguay": "Uruguay",
    "venezuela": "Venezuela",
    
    # ----------------------------------------
    # II. Europa
    # ----------------------------------------
    "alemania": "Germany",
    "austria": "Austria",
    "belgica": "Belgium",
    "bélgica": "Belgium",
    "croacia": "Croatia",
    "dinamarca": "Denmark",
    "españa": "Spain",
    "finlandia": "Finland",
    "francia": "France",
    "grecia": "Greece",
    "holanda": "Netherlands",
    "paises bajos": "Netherlands",
    "países bajos": "Netherlands",
    "hungria": "Hungary",
    "hungría": "Hungary",
    "irlanda": "Ireland",
    "italia": "Italy",
    "noruega": "Norway",
    "polonia": "Poland",
    "portugal": "Portugal",
    "reino unido": "Great Britain", 
    "gran bretaña": "Great Britain",
    "rusia": "ROC",
    "serbia": "Serbia",
    "suecia": "Sweden",
    "suiza": "Switzerland",
    "ucrania": "Ukraine",
    
    # ----------------------------------------
    # III. Asia y Oceanía
    # ----------------------------------------
    "australia": "Australia",
    "china": "China",
    "corea del sur": "South Korea",
    "corea": "South Korea",
    "filipinas": "Philippines",
    "india": "India",
    "indonesia": "Indonesia",
    "iran": "Iran",
    "irak": "Iraq",
    "israel": "Israel",
    "japon": "Japan",
    "japón": "Japan",
    "nueva zelanda": "New Zealand",
    "pakistan": "Pakistan",
    "pakistán": "Pakistan",
    "tailandia": "Thailand",
    "turquia": "Turkey",
    "turquía": "Turkey",
    
    # ----------------------------------------
    # IV. África
    # ----------------------------------------
    "argelia": "Algeria",
    "egipto": "Egypt",
    "etiopia": "Ethiopia",
    "etiopía": "Ethiopia",
    "kenia": "Kenya",
    "marruecos": "Morocco",
    "nigeria": "Nigeria",
    "sudafrica": "South Africa"
}

# --- Funciones Auxiliares ---

def extract_medal_type(query: str):
    """Detecta el tipo de medalla: Gold, Silver, Bronze o Total."""
    query = query.lower()
    if "oro" in query: return "Gold"
    elif "plata" in query: return "Silver"
    elif "bronce" in query: return "Bronze"
    else: return "Total"

def get_nation_from_query(query: str, df: pd.DataFrame):
    """Intenta encontrar un nombre de país válido en la consulta."""
    query_lower = query.lower()

    # 1. Intentar coincidencia directa con los nombres limpios del DF (en inglés)
    nation_list_lower = df['Nation'].str.lower().unique().tolist()
    
    for nation in sorted(nation_list_lower, key=len, reverse=True):
        if nation in query_lower:
            # Devuelve el nombre en el idioma del DataFrame (e.g., 'France')
            return df[df['Nation'].str.lower() == nation].iloc[0]['Nation'] 
    
    # 2. Intentar coincidencia con el MAPEO Español -> Inglés
    for spanish_name, english_name in SPANISH_TO_ENGLISH_MAP.items():
        if spanish_name in query_lower:
            # Devuelve el nombre en inglés mapeado (e.g., 'France')
            return english_name

    return None

def get_year_from_query(query: str) -> int | None:
    """Busca un año de 4 dígitos relevante para JJOO en la consulta."""
    match = re.search(r'\b(20[0-9]{2})\b|\b(19[0-9]{2})\b', query) # Busca años en 19xx y 20xx
    if match:
        year = int(match.group(1))
        # Validación opcional para años comunes de JJOO de verano
        if year in [2024, 2020, 2016, 2012, 2008, 2004, 2000, 1996, 1992, 1988, 1984, 1980]: 
             return year
    return None

# --- Herramienta Principal ---

def OlympicData(df_clean: pd.DataFrame, query: str) -> Dict[str, Any]:
    """
    TOOL UNIFICADA: Responde a preguntas de ranking, clasificación o datos de países,
    filtrando por el año si se especifica en la consulta.
    """
    query_lower = query.lower()
    
    # 1. DETECCIÓN DE AÑO Y FILTRADO INICIAL
    target_year = get_year_from_query(query)
    
    df_filtered = df_clean.copy()
    year_context = "todos los años disponibles"
    
    if target_year:
        df_filtered = df_clean[df_clean['Year'] == target_year]
        year_context = str(target_year)
        
        if df_filtered.empty:
            return {"success": False, "error": f"No se encontraron datos de medallas para el año {target_year} en la base de datos."}

    # ----------------------------------------------------
    # PATH 1: DETECCIÓN DE CLASIFICACIÓN (RANKING)
    # ----------------------------------------------------
    if any(keyword in query_lower for keyword in ["más", "mayor", "lider", "líder", "quién", "top"]):
        medal_type = extract_medal_type(query)
        
        # Obtener el Top 5 exacto del DataFrame filtrado
        top_df = df_filtered.sort_values(by=medal_type, ascending=False).head(5)
        
        result = [
            f"{i+1}. {row['Nation']} con {row[medal_type]} medallas de {medal_type.lower()}."
            for i, row in top_df.reset_index().iterrows()
        ]
        
        summary = f"Ranking de medallas de {medal_type} para el año {year_context} (Top 5):\n" + "\n".join(result)
        return {"success": True, "result": summary}

    # ----------------------------------------------------
    # PATH 2: DETECCIÓN DE DATOS ESPECÍFICOS DE PAÍS
    # ----------------------------------------------------
    
    nation_name_found = get_nation_from_query(query, df_clean) # Usar df_clean para buscar el país sin filtrar por año
    
    if nation_name_found:
        # Filtrar por país Y por año (si se especificó)
        match = df_filtered[df_filtered['Nation'].str.lower() == nation_name_found.lower()]
        
        if not match.empty:
            row = match.iloc[0]
            g, s, b, t = [int(row.get(m, 0)) for m in ["Gold", "Silver", "Bronze", "Total"]]
            
            info = (
                f"Datos de {row['Nation']} en {row['Year']}: "
                f"Ganó {g} oros, {s} platas, y {b} bronces (Total: {t} medallas)."
            )
            return {"success": True, "result": info}

    # ----------------------------------------------------
    # PATH 3: FALLBACK
    # ----------------------------------------------------
    
    return {"success": False, "error": f"La consulta no es de ranking ni de datos de país. El LLM debe usar el Contexto RAG o Tools externas (News/Weather)."}