import os
from dotenv import load_dotenv
load_dotenv() 
from scraper import scrape_medal_table
import gradio as gr
import pandas as pd
from vector_db import create_vector_db
from rag import run_rag
from agent import answer_with_agent

# Verificar la clave de Gemini
gemini_key_set = bool(os.getenv("GOOGLE_API_KEY"))

# 2. Inicialización del Sistema (Scraping, Limpieza e Indexación)
print("--- 🚀 INICIALIZANDO SISTEMA RAG HÍBRIDO ---")

try:
    # 2a. Scraping (solo una vez al inicio)
    # Pasa la lista de años al scraper
    df_raw = scrape_medal_table() 
    
    # 2b. Creación de la DB y obtención del DataFrame limpio
    collection, df_clean = create_vector_db(df_raw)
    
    print("--- ✅ SISTEMA LISTO ---")

except Exception as e:
    print(f"--- ❌ ERROR FATAL DE INICIALIZACIÓN ---")
    print(f"Asegúrate de que Playwright esté instalado y que la URL de scraping sea accesible. Error: {e}")
    # Usar valores de fallback para que la interfaz al menos cargue
    collection = None
    df_clean = pd.DataFrame()


# --- Función del Servidor (Llamada por Gradio) ---

def answer_query(query: str):
    """
    Función principal que dirige la consulta al Agente Gemini o al RAG local.
    """
    if not collection:
        return "El sistema RAG no se pudo inicializar correctamente. Revisa la consola.", "(Error de Inicialización)"

    # Ejecutar el RAG Híbrido local para obtener el contexto semántico/determinista
    rag_summary = run_rag(query, collection, df_clean)

    if gemini_key_set:
        # 1. Ruta del AGENTE (con Tools)
        final_answer, tool_history = answer_with_agent(query, rag_summary, df_clean)
        
    else:
        # 2. Ruta de FALLBACK (solo RAG local)
        # Si no hay clave API, el agente no puede ejecutar tools ni razonar, 
        # así que la respuesta se basa solo en el rag_summary.
        
        # En un sistema real, aquí llamarías a un LLM local.
        # Para simular, devolvemos el resumen y una nota de advertencia.
        final_answer = f"FALLBACK RAG (Sin Gemini/Tools):\n{rag_summary}"
        tool_history = "(No GOOGLE_API_KEY set; Agente/Tools no disponibles)"

    return final_answer, tool_history


# --- Interfaz de Gradio ---

with gr.Blocks(theme=gr.themes.Soft(), title="Agente RAG Híbrido JJOO") as demo:
    gr.Markdown(
        """
        # 🤖 Agente RAG Híbrido de los Juegos Olímpicos 🏅
        Este Agente utiliza un RAG local (DataFrame de Pandas y ChromaDB) y Tools externas (News/Weather) 
        orquestadas por Gemini para responder.
        
        Estado del Agente: **{}**
        """.format(
            "✅ AGENTE COMPLETO (con Tools y RAG)" if gemini_key_set else "⚠️ MODO RAG/FALLBACK (Falta GOOGLE_API_KEY)"
        )
    )
    
    # Columna de entrada y botón
    with gr.Row():
        query_input = gr.Textbox(
            label="Tu Consulta (ej: ¿Quién ganó más oros en 2016?)",
            lines=2,
            placeholder="Escribe tu pregunta aquí..."
        )
        submit_btn = gr.Button("Enviar Consulta", variant="primary", scale=0)
    
    # Salidas (usando Markdown para la respuesta principal)
    with gr.Row():
        with gr.Column(scale=2):
            out_rag = gr.Markdown(label="Respuesta Final del Agente")
        with gr.Column(scale=1):
            out_tool = gr.Textbox(
                label="Historial de Tools / Log", 
                lines=10, 
                interactive=False, 
                value="Log de la ejecución del Agente..."
            )

    # Conectar la función al botón
    submit_btn.click(
        fn=answer_query,
        inputs=[query_input],
        outputs=[out_rag, out_tool]
    )

# Lanzar la aplicación
if __name__ == "__main__":
    demo.launch()