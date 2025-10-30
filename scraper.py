import pandas as pd
from io import StringIO
from playwright.sync_api import sync_playwright
import re
import time 

# Lista de años de los Juegos Olímpicos de Verano (de 1996 en adelante)
# Esta lista se pasa por defecto si no se especifica 'years'
DEFAULT_YEARS = [2024, 2020, 2016, 2012, 2008, 2004, 2000, 1996]

def scrape_medal_table(years: list = None):
    """
    Usa Playwright para raspar los medalleros de múltiples años (usando la Wiki en inglés
    por su estructura de tabla más estable), los consolida en un solo DataFrame, 
    y añade la columna 'Year'.
    """
    if years is None:
        years = DEFAULT_YEARS
        
    all_data = []
    
    # URL base de Wikipedia en INGLÉS (más estable para el formato de tabla)
    BASE_URL = "https://en.wikipedia.org/wiki/{}_Summer_Olympics_medal_table" 

    print("--- Inicializando Playwright para Scraping Multi-Año ---")
    print(f"Años a raspar: {years}")
    
    with sync_playwright() as p:
        try:
            # Usar 'headless=True' para evitar abrir una ventana de navegador
            browser = p.chromium.launch(headless=True) 
            page = browser.new_page()
        except Exception as e:
            # Lanza un error de tiempo de ejecución para ser capturado en gradio_app.py
            raise RuntimeError(f"Error al iniciar Playwright: {e}")

        for year in years:
            print(f"Scraping datos del año: {year}...")
            url = BASE_URL.format(year)
            
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(1.5) # Dar tiempo para renderizar
                html_content = page.content()
                
                # 1. Extraer todas las tablas con Pandas
                # Usamos StringIO para evitar errores de codificación
                tables = pd.read_html(StringIO(html_content))
                
                # 2. Lógica para encontrar y estandarizar la tabla de medallero
                df = None
                
                # Criterios flexibles de columnas (más comunes en la Wiki en inglés)
                medal_keywords = ['gold', 'silver', 'bronze']
                nation_keywords = ['nation', 'country', 'team', 'n.o.c.', 'rank'] 
                
                possible_tables = [] 
                
                for table in tables:
                    # Normalizar los nombres de columna de la tabla actual
                    cols = [str(col).strip().lower() for col in table.columns.to_flat_index()]
                    
                    medal_score = sum(1 for kw in medal_keywords if kw in cols)
                    nation_score = sum(1 for kw in nation_keywords if kw in cols)

                    is_large_enough = table.shape[0] > 10
                    
                    # Seleccionar tablas que parecen ser el medallero principal
                    if (medal_score + nation_score) >= 3 and is_large_enough:
                        table.columns = table.columns.to_flat_index()
                        possible_tables.append({'score': medal_score + nation_score, 'df': table.copy()})
                
                # Elegir la tabla con la puntuación más alta
                if possible_tables:
                    best_match = max(possible_tables, key=lambda x: x['score'])
                    df = best_match['df']
                    
                    # 3. Estandarizar las columnas (LÓGICA MEJORADA)
                    df.columns = [str(col).strip().capitalize() for col in df.columns]
                    
                    col_map = {}
                    nation_col_found = False

                    for col in df.columns:
                        col_lower = col.lower()
                        
                        # Mapeo de Medallas
                        if col_lower in ['gold', 'silver', 'bronze', 'total']:
                            col_map[col] = col.capitalize()
                        
                        # Mapeo de Nation
                        elif not nation_col_found and any(kw in col_lower for kw in ['nation', 'country', 'team', 'n.o.c.']):
                            col_map[col] = 'Nation'
                            nation_col_found = True
                        
                        # Mapeo de Rank
                        elif 'rank' in col_lower and 'Rank' not in col_map.values():
                            col_map[col] = 'Rank'


                    # LÓGICA DE FALLBACK CRÍTICA: Detectar la columna de Nación si el nombre falla
                    if not nation_col_found:
                        for col in df.columns:
                            if (df[col].dtype == 'object' and 
                                df[col].astype(str).str.contains(r'[a-zA-Z]', regex=True).sum() > df.shape[0] * 0.5):
                                
                                if col.lower() not in ['rank'] and col not in col_map.keys():
                                    col_map[col] = 'Nation'
                                    nation_col_found = True
                                    break
                    
                    
                    df = df.rename(columns=col_map)
                    
                    # Verificación final
                    if all(c in df.columns for c in ['Nation', 'Gold', 'Silver', 'Bronze']):
                        print(f"✅ Tabla de medallas identificada correctamente para el año {year}.")
                    else:
                        # Si falta alguna columna clave después del mapeo, descartar
                        print(f"⚠️ Advertencia: Columnas clave faltantes después del mapeo para el año {year}. Descartando.")
                        df = None 
                        
                
                if df is None:
                    print(f"⚠️ Advertencia: No se pudo identificar la tabla principal para el año {year}.")
                    continue
                
                # 4. Limpieza y Consolidación
                # Eliminar filas de totales si existen
                df = df[~df['Nation'].astype(str).str.contains('Total|–', case=False, na=False)]
                
                df['Year'] = year
                all_data.append(df)
                
            except Exception as e:
                print(f"⚠️ Error al procesar el año {year} ({url}). Error: {e}")
                continue

        browser.close()

    if not all_data:
        raise RuntimeError("No se pudo obtener datos de medallas para ningún año.")
        
    final_df = pd.concat(all_data, ignore_index=True)
    
    # Seleccionar y reordenar las columnas finales necesarias
    final_cols = [c for c in ['Nation', 'Gold', 'Silver', 'Bronze', 'Total', 'Year'] if c in final_df.columns]
    final_df = final_df[final_cols]

    return final_df

if __name__ == '__main__':
    # Ejemplo de uso si ejecutas scraper.py directamente
    try:
        # Pasa todos los años por defecto si no se especifican
        medals_df = scrape_medal_table() 
        print("\n--- DataFrame Final de Medallas ---")
        print(medals_df.head(10))
    except RuntimeError as e:
        print(f"Falló la ejecución del scraping: {e}")