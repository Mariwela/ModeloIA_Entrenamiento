import pandas as pd
import re
from typing import Tuple

# Función auxiliar
def clean_country_name(name):
    """Limpia símbolos como ‡, *, † y asegura tipo string."""
    return re.sub(r"[‡*†]", "", str(name)).strip()

def run_rag(query: str, collection, df_clean: pd.DataFrame) -> Tuple[str, str]:
    """
    Ejecuta un flujo RAG HÍBRIDO.
    1. Detecta si la pregunta es de CLASIFICACIÓN (determinista).
    2. Si no es clasificación, usa ChromaDB para contexto semántico.
    3. Devuelve un resumen del contexto local para el LLM.
    """
    print(f"\n🧠 Ejecutando RAG Híbrido para: '{query}'")

    query_lower = query.lower()
    
    # 1. Detección de Clasificación (Determinista)
    # Esta ruta no necesita el RAG Semántico, así que forzamos al Agente a usar la TOOL.
    is_ranking_query = any(keyword in query_lower for keyword in ["más", "mayor", "lider", "líder", "quién", "top"])
    is_specific_country = any(clean_country_name(row["Nation"]).lower() in query_lower for _, row in df_clean.iterrows())

    if is_ranking_query or is_specific_country:
        print("✅ Contexto recuperado: Pregunta de Ranking o País detectada. FORZANDO USO de OlympicData TOOL.")
        # Devolvemos un contexto mínimo para que el Agente sepa que debe usar la herramienta
        rag_summary = "La consulta parece requerir datos de ranking o conteo exacto de medallas. La información debe ser recuperada usando la herramienta 'OlympicData'."
        
    else:
        # 2. Búsqueda Semántica (Vectorial)
        try:
            # Recuperación de ChromaDB. Utilizamos el metadato 'year' si se detectó.
            results = collection.query(query_texts=[query], n_results=3)
            docs = results.get("documents", [[]])[0]
            
            print("🧠 Contexto recuperado: Usando BÚSQUEDA VECTORIAL (ChromaDB) para contexto semántico.")

            if docs:
                # 3. Generación de resumen para el LLM
                context_texts = "\n".join([f"- {d}" for d in docs])
                rag_summary = f"La base de datos de los JJOO contiene el siguiente contexto relevante:\n{context_texts}"
            else:
                rag_summary = "La base de datos local no encontró información semántica relevante."

        except Exception as e:
            print(f"⚠️ Error en la recuperación vectorial: {e}")
            rag_summary = "Error al acceder a la base de datos local."

    print("\n📚 Contexto local (rag_summary) para el LLM:")
    print(rag_summary)
    
    return rag_summary