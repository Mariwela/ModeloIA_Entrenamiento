import sys
import os
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import asyncio

# Añadir la carpeta raíz del proyecto al path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
from tools.external_mcp import send_report_to_external_mcp

# Configurar rutas para importar tus tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.medals_api import get_olympic_medals
from tools.llm_analysis import analyze_country_performance

load_dotenv()

# 1. Definimos el Estado del Agente
class AgentState(TypedDict):
    target_country: str
    target_year: int
    data_results: str
    analysis_results: str
    final_answer: str

# 2. Definimos los Nodos (Las acciones del agente)

def tool_fetcher_node(state: AgentState):
    """Primer paso: Consulta la base de datos local (CSV) a través de la Tool."""
    print("\n🔍 [PASO 1]: CONSULTANDO HERRAMIENTAS MCP (DATOS)...")
    medals = get_olympic_medals(state["target_country"], state["target_year"])
    
    if "error" in medals:
        res = f"No se encontraron datos: {medals['error']}"
    else:
        res = (f"Oros: {medals['gold']}, Platas: {medals['silver']}, "
               f"Bronces: {medals['bronze']}, Total: {medals['total']}")
    
    print(f"✅ Datos recuperados: {res}")
    return {"data_results": res}

def analyst_node(state: AgentState):
    """Segundo paso: Usa un LLM para obtener contexto histórico sobre el país."""
    print("\n🧠 [PASO 2]: GENERANDO ANÁLISIS CUALITATIVO...")
    context = analyze_country_performance(state["target_country"])
    print("✅ Análisis de contexto completado.")
    return {"analysis_results": context}

def final_expert_node(state: AgentState):
    print("\n✍️  [PASO 3]: REDACTANDO INFORME FINAL...")
    llm = ChatGroq(model="llama-3.1-8b-instant")
    
    # Añadimos instrucciones de "Grounding" (anclaje a datos reales)
    prompt = f"""
    Eres un experto historiador olímpico. Tienes estos datos reales sobre la mesa:
    
    - AÑO DE LA CONSULTA: {state['target_year']}
    - PAÍS: {state['target_country']}
    - RESULTADOS OBTENIDOS: {state['data_results']}
    - CONTEXTO HISTÓRICO: {state['analysis_results']}

    TU TAREA:
    Analiza si el año {state['target_year']} fue exitoso para {state['target_country']}.
    
    REGLA DE ORO: 
    Confirma que los 'RESULTADOS OBTENIDOS' corresponden exactamente al año {state['target_year']}. 
    Compara esos datos con el contexto histórico para dar un veredicto final.
    """
    
    response = llm.invoke(prompt)
    return {"final_answer": response.content}

def external_mcp_node(state: AgentState):
    """
    Paso 4: Envía el informe final a un MCP de terceros
    """
    print("\n🌐 [PASO 4]: ENVIANDO INFORME A MCP EXTERNO...")

    try:
        asyncio.run(
            send_report_to_external_mcp(state["final_answer"])
        )
        print("✅ Informe enviado correctamente al MCP externo.")
    except Exception as e:
        print(f"⚠️ Error enviando a MCP externo: {e}")

    return {}

# 3. Construcción del Grafo de LangGraph
workflow = StateGraph(AgentState)

# Añadimos los nodos al tablero
workflow.add_node("get_data", tool_fetcher_node)
workflow.add_node("get_analysis", analyst_node)
workflow.add_node("write_report", final_expert_node)
workflow.add_node("external_mcp", external_mcp_node)

# Definimos las flechas (el flujo)
workflow.set_entry_point("get_data")
workflow.add_edge("get_data", "get_analysis")
workflow.add_edge("get_analysis", "write_report")
workflow.add_edge("write_report", "external_mcp")
workflow.add_edge("external_mcp", END)

# Compilamos el sistema
app = workflow.compile()

# 4. Ejecución de prueba
if __name__ == "__main__":
    # Puedes cambiar estos valores para probar otros países/años
    test_inputs = {
        "target_country": "Spain", 
        "target_year": 2000
    }
    
    print("🚀 INICIANDO AGENTE LANGGRAPH...")
    print("-" * 30)
    
    # Imprimir el grafo en texto plano
    try:
        print("\n ESTRUCTURA DEL GRAFO:")
        app.get_graph().print_ascii()
    except Exception as e:
        print(f"No se pudo imprimir el grafo: {e}")

    # Ejecutamos el flujo en streaming para ver los pasos
    config = {"configurable": {"thread_id": "1"}}
    
    for output in app.stream(test_inputs, config):
        for key, value in output.items():
            # Asegurarnos de que value es un diccionario
            if isinstance(value, dict) and "final_answer" in value:
                print("\n" + "="*50)
                print("🏆 CONCLUSIÓN FINAL DEL EXPERTO:")
                print("="*50)
                print(value['final_answer'])
                print("="*50)