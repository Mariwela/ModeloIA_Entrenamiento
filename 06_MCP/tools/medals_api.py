import pandas as pd
import os
import re

# 1. Ubicación de este archivo (server/tools/medals_api.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Subimos un nivel para llegar a 'server/'
SERVER_DIR = os.path.dirname(current_dir)

# 3. Entramos en 'data/'
ATHLETE_PATH = os.path.join(SERVER_DIR, "data", "athlete_events.csv")
NOC_PATH = os.path.join(SERVER_DIR, "data", "noc_regions.csv")

# --- DEBUG: Esto te ayudará a ver en la consola si los encuentra ---
if not os.path.exists(ATHLETE_PATH):
    print(f"ERROR: No encuentro el CSV en: {ATHLETE_PATH}")
else:
    print(f"CSV detectado en: {ATHLETE_PATH}")

def normalize(text):
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return text

def get_olympic_medals(country: str, year: int):

    """
    Consulta dataset olímpico de Kaggle.
    """

    df = pd.read_csv(ATHLETE_PATH)
    noc_df = pd.read_csv(NOC_PATH)

    country_clean = normalize(country)

    # Si coincide con un código NOC
    noc_match = noc_df[noc_df["NOC"].str.lower() == country_clean]

    if not noc_match.empty:
        noc_codes = noc_match["NOC"].tolist()
    else:
        # Buscar por nombre del país
        noc_df["region"] = noc_df["region"].fillna("")
        noc_df["notes"] = noc_df["notes"].fillna("")

        noc_df["region_clean"] = noc_df["region"].apply(normalize)
        noc_df["notes_clean"] = noc_df["notes"].apply(normalize)

        matches = noc_df[
            (noc_df["region_clean"] == country_clean) |
            (noc_df["notes_clean"] == country_clean)
    ]

        if matches.empty:
            return {"error": f"No se encontró el país '{country}'"}

        noc_codes = matches["NOC"].tolist()

    # Filtrar dataset
    filtered = df[
        (df["NOC"].isin(noc_codes)) &
        (df["Year"] == year) &
        (df["Medal"].notna())
    ]

    # Eliminamos duplicados por Evento y Medalla
    # Esto hace que el Oro en 'Football Men's Football' cuente como 1, no como 22.
    medals_deduplicated = filtered.drop_duplicates(subset=["Event", "Medal"])

    # Contamos sobre el dataframe limpio
    gold = len(medals_deduplicated[medals_deduplicated["Medal"] == "Gold"])
    silver = len(medals_deduplicated[medals_deduplicated["Medal"] == "Silver"])
    bronze = len(medals_deduplicated[medals_deduplicated["Medal"] == "Bronze"])

    return {
        "input_country": country,
        "nocs_used": noc_codes,
        "year": year,
        "gold": gold,
        "silver": silver,
        "bronze": bronze,
        "total": gold + silver + bronze,
        "source": "Kaggle athlete_events.csv + noc_regions.csv (robust matching)"
    }