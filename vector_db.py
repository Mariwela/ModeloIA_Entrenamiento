import pandas as pd
from chromadb import Client, Settings
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction 
import os
import re 

# --- 1. CONFIGURACIÓN ---
# Usamos el modelo local de Sentence Transformers
LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2" 
CHROMA_PATH = "chroma_db_olympics"

def clean_country_name(nation_name: str) -> str:
    """
    Limpia un nombre de país eliminando texto entre paréntesis.
    Ej: 'United States (USA)' -> 'United States'
    """
    cleaned = re.sub(r'\s*\(.*\)', '', nation_name).strip()
    return cleaned


def create_vector_db(df_raw: pd.DataFrame):
    """
    Limpia los datos brutos, crea el contexto de texto y los indexa
    en una base de datos vectorial (ChromaDB) usando Sentence Transformers.
    """
    print(f"\n🧠 Configurando Embeddings: Usando modelo local '{LOCAL_EMBEDDING_MODEL}'...")

    # --- 2. Inicialización de la Función de Embeddings Local ---
    # Chroma se encargará de descargar y usar este modelo localmente.
    try:
        st_ef = SentenceTransformerEmbeddingFunction(model_name=LOCAL_EMBEDDING_MODEL)
    except Exception as e:
        raise RuntimeError(f"❌ Fallo al inicializar SentenceTransformer. Asegúrate de que el paquete 'sentence-transformers' esté instalado. Error: {e}")


    # --- 3. Limpieza de Datos ---
    
    # Asegurar que las columnas son las esperadas del scraper
    df_raw.columns = ['Nation', 'Gold', 'Silver', 'Bronze', 'Total', 'Year']

    df_clean = df_raw.copy() 
    
    # Limpiar nombres de país
    df_clean['Nation'] = df_clean['Nation'].astype(str).apply(clean_country_name).str.strip()
    df_clean['Nation'] = df_clean['Nation'].str.replace(r"[‡*†]", "", regex=True).str.strip()
    
    # Conversión a entero
    df_clean = df_clean.dropna(subset=['Gold', 'Silver', 'Bronze', 'Total'])
    df_clean[['Gold', 'Silver', 'Bronze', 'Total']] = df_clean[['Gold', 'Silver', 'Bronze', 'Total']].astype(int)
    

    # --- 4. Generación de Documentos y Metadata ---
    
    documents = []
    metadata = []
    
    for index, row in df_clean.iterrows():
        # Generar texto descriptivo para el embedding
        doc_text = (
            f"El país {row['Nation']} en los Juegos Olímpicos de {row['Year']} ganó "
            f"{row['Gold']} medallas de oro, {row['Silver']} de plata, y {row['Bronze']} de bronce, "
            f"sumando un total de {row['Total']} medallas."
        )
        documents.append(doc_text)
        
        # Guardar metadata
        metadata.append({
            "nation": row['Nation'],
            "year": str(row['Year']),
            "gold": row['Gold']
        })

    # --- 5. Inicialización e Indexación de ChromaDB ---
    
    client = Client(Settings(persist_directory=CHROMA_PATH))
    collection_name = "olympic_medals_collection"
    
    if collection_name in client.list_collections():
        client.delete_collection(name=collection_name)
    
    print(f"⏳ Indexando {len(documents)} documentos en ChromaDB...")
    
    # Crear la colección usando la función de embeddings local
    collection = client.create_collection(
        name=collection_name, 
        embedding_function=st_ef
    )
    
    collection.add(
        documents=documents,
        metadatas=metadata,
        ids=[f"doc_{i}" for i in range(len(documents))]
    )

    print(f"Base de datos vectorial creada con {len(documents)} documentos históricos.")

    return collection, df_clean

def run_rag(query: str, collection, df_clean: pd.DataFrame):
    """
    Ejecuta el proceso RAG local: clasifica la consulta, recupera el contexto,
    y formatea el resultado.
    """
    query_lower = query.lower()
    
    # Clasificación y Búsqueda determinista (Path 2: Ranking/País Específico)
    
    ranking_keywords = ['ranking', 'rank', 'puesto', 'posición', 'quién ganó', 'quien gano', 'top', 'líder']
    is_ranking_query = any(kw in query_lower for kw in ranking_keywords)
    
    # Usar la función de limpieza para una mejor coincidencia
    is_specific_country = any(clean_country_name(row["Nation"]).lower() in query_lower for _, row in df_clean.iterrows())

    # Devolver un marcador si se detecta una consulta determinista
    if is_ranking_query or is_specific_country:
        print("🧠 Ejecutando RAG Híbrido para: 'Ranking o País detectado'")
        return "Tool Local Detectada: OlympicData" 

    
    # Clasificación y Búsqueda Semántica (Path 1: Pregunta Abierta/Contextual)
    
    print("🧠 Contexto recuperado: Usando BÚSQUEDA VECTORIAL (ChromaDB) para contexto semántico.")
    
    # Búsqueda de los documentos más relevantes
    try:
        results = collection.query(
            query_texts=[query],
            n_results=3,  # Recuperar los 3 documentos más relevantes
            include=['documents', 'metadatas']
        )
    except Exception as e:
        return f"⚠️ Fallo en la búsqueda vectorial: {e}"

    
    # Formatear los resultados
    rag_summary = "📚 Contexto local (rag_summary) para el LLM:\n"
    if results and results['documents'] and results['documents'][0]:
        for doc in results['documents'][0]:
            rag_summary += f"- {doc}\n"
    else:
        rag_summary += "- No se encontró contexto relevante en la base de datos local para esta consulta.\n"

    return rag_summary

if __name__ == '__main__':
    print("Ejecutando prueba de vector_db.py. Este script requiere una llamada externa.")