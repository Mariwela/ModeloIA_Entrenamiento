"""
scraping.py — Extracción de medalleros olímpicos (2000–2024) usando Playwright.
Corrige errores de parseo en Tokio/París 2024.
"""

import re
import pandas as pd
from tqdm import tqdm
from playwright.sync_api import sync_playwright
from tools import setup_logging, clean_text

YEARS = [2000, 2004, 2008, 2012, 2016, 2020, 2024]
BASE_URL = "https://en.wikipedia.org/wiki/{}_Summer_Olympics_medal_table"


def _clean_country(name: str) -> str:
    """Limpia texto de país (sin banderas, notas ni paréntesis)."""
    if not isinstance(name, str):
        return ""
    name = re.sub(r"\[.*?\]", "", name)
    name = re.sub(r"\(.*?\)", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def scrape_medal_table_for_year(year: int, page) -> pd.DataFrame:
    """Scrapea el medallero de un año específico usando Playwright."""
    url = BASE_URL.format(year)
    print(f"🌐 Scrapeando {year}: {url}")
    page.goto(url, timeout=60000)
    page.wait_for_selector("table.wikitable", timeout=30000)

    # Obtén todas las tablas y elige la que contenga encabezados típicos
    tables = page.query_selector_all("table.wikitable")
    html_tables = [t.inner_html() for t in tables]

    target_html = None
    for html in html_tables:
        if re.search(r"Gold", html, re.I) and re.search(r"Nation|NOC|Team|Country", html, re.I):
            target_html = html
            break

    if not target_html:
        target_html = html_tables[0]
        print(f"⚠️ Usando primera tabla (no se detectó encabezado típico)")

    # Parsea la tabla HTML con pandas
    df = pd.read_html(f"<table>{target_html}</table>")[0]

    # Normaliza columnas
    df.columns = [str(c).strip().lower() for c in df.columns]
    rename_map = {
        "noc": "country",
        "team/noc": "country",
        "nation": "country",
        "country": "country",
        "rank": "rank",
        "gold": "gold",
        "silver": "silver",
        "bronze": "bronze",
        "total": "total",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # Filtra columnas esperadas
    df = df[[c for c in ["rank", "country", "gold", "silver", "bronze", "total"] if c in df.columns]]

    # Limpieza de filas
    df["country"] = df["country"].apply(_clean_country)
    df = df[df["country"].notna()]
    df = df[~df["country"].str.contains("Totals|Total|Rank", case=False, na=False)]
    df = df[~df["country"].str.match(r"^\d+$")]  # elimina filas numéricas

    # Convierte medallas a números
    for col in ["gold", "silver", "bronze", "total", "rank"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["year"] = year
    return df.reset_index(drop=True)


def scrape_all(years=YEARS) -> pd.DataFrame:
    """Scrapea todos los años con una sola sesión de Playwright."""
    all_dfs = []

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        for year in tqdm(years, desc="Scrapeando medalleros"):
            try:
                df_year = scrape_medal_table_for_year(year, page)
                all_dfs.append(df_year)
            except Exception as e:
                print(f"❌ Error con {year}: {e}")
        browser.close()

    return pd.concat(all_dfs, ignore_index=True)


if __name__ == "__main__":
    setup_logging()
    print("🏗️ Iniciando scraping (2000–2024)...")
    df = scrape_all()
    df.to_csv("olympic_medals_2000_2024.csv", index=False)
    print("✅ Archivo guardado: olympic_medals_2000_2024.csv")
