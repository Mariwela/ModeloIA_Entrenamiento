from playwright.sync_api import sync_playwright # para controlar un navegador en modo síncrono
import pandas as pd # para convertir tablas HTML en DataFrame
from io import StringIO # para entregar a pd.read_html un objeto parecido a un archivo a partir de la cadena html

def scrape_medal_table():
    """Hace scraping de la tabla de medallas de Wikipedia (Juegos Olímpicos 2024)"""
    url = "https://en.wikipedia.org/wiki/2024_Summer_Olympics_medal_table"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # Abre Playwright y lanza Chromium en modo headless
        page = browser.new_page() # Crea una nueva página y navega a la URL
        page.goto(url) # 
        page.wait_for_load_state("networkidle") # espera hasta que no haya tráfico de red activo
        html = page.content() # obtiene el HTML final
        browser.close() # cierra el navegado

    # Leer todas las tablas, devuelve una lista de DataFrames
    tables = pd.read_html(StringIO(html))
    df = None

    # Buscar la tabla que tenga 'Gold' o 'Silver'
    for t in tables:
        cols = [str(c).strip() for c in t.columns]
        if any("Gold" in c for c in cols) and any("Silver" in c for c in cols):
            df = t
            break

    if df is None:
        raise ValueError("❌ No se encontró una tabla válida de medallas.")

    # Mostrar columnas detectadas
    print("📊 Columnas detectadas:", df.columns.tolist())

    # Normalizar nombres
    df.columns = [str(c).strip() for c in df.columns]

    # Buscar el nombre real de la columna que representa el país/nación
    nation_col = None
    for possible in ["Nation", "NOC", "Team / NOC", "Country", "Team"]:
        if possible in df.columns:
            nation_col = possible
            break

    if not nation_col:
        raise KeyError(f"❌ No se encontró ninguna columna de nación en: {df.columns.tolist()}")

    # Renombrar a formato estándar
    rename_map = {nation_col: "Nation"}
    for col in df.columns:
        if "Gold" in col: rename_map[col] = "Gold"
        elif "Silver" in col: rename_map[col] = "Silver"
        elif "Bronze" in col: rename_map[col] = "Bronze"
        elif "Total" in col: rename_map[col] = "Total"
        elif "Rank" in col: rename_map[col] = "Rank"

    df = df.rename(columns=rename_map)

    # Eliminar filas vacías o totales
    df = df.dropna(subset=["Nation"])
    df = df[~df["Nation"].astype(str).str.contains("Total", case=False)]
    df = df.reset_index(drop=True)

    return df
