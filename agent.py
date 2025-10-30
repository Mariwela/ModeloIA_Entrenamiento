import os
import re
import pandas as pd
from typing import Dict, Any, Tuple
from google import genai
from google.genai.errors import APIError
from google import genai
from google.genai.errors import APIError
from rag_tools import OlympicData 
from tools import newsapi_top_headlines, openweather_current 

# -----------------------------------------------------------------
# 1. INICIALIZACIÓN GLOBAL DEL CLIENTE GEMINI
# Se inicializa a None y se intenta crear el cliente si la clave existe.
# -----------------------------------------------------------------
GEMINI_CLIENT = None 
api_key = os.getenv("GOOGLE_API_KEY")

try:
    if api_key:
        GEMINI_CLIENT = genai.Client(api_key=api_key)
        
        print("✅ Cliente de Gemini inicializado correctamente.")
    else:
        print("Advertencia: GOOGLE_API_KEY no configurada. El Agente operará en modo Fallback.")
        
except APIError as e:
    # Si la API rechaza la clave (ej: 401 Unauthorized), capturamos el error específico.
    print(f"❌ ERROR FATAL DE API: La clave fue leída, pero rechazada por Gemini. Estado: {e.status_code}. Mensaje: {e.message}")
    GEMINI_CLIENT = None # Aseguramos que el cliente es None
    
except Exception as e:
    # Captura otros errores de inicialización
    print(f"❌ ERROR DE INICIALIZACIÓN DE CLIENTE: {e}")
    GEMINI_CLIENT = None # Aseguramos que el cliente es None


# --- 2. Definición de las Herramientas (Tools) para Gemini ---

ALL_TOOLS = [
    newsapi_top_headlines, 
    openweather_current
]


# --- 3. Procesamiento de Tools (Ejecución y Formato) ---

def process_tool_call(tool: str, param: str, df_clean: pd.DataFrame):
    """
    Ejecuta una llamada a una herramienta (OlympicData, NewsAPI, OpenWeather)
    y devuelve el resultado formateado.
    """
    
    # 1. HERRAMIENTA DETERMINISTA UNIFICADA
    if tool.lower() == "olympicdata":
        # Se pasa el DataFrame limpio y la consulta completa
        res = OlympicData(df_clean, param)
        return {"tool": "OlympicData", "param": param, "result": res}

    # 2. NEWS API
    if tool.lower() == "newsapi":
        api_key = os.getenv("NEWSAPI_KEY")
        res = newsapi_top_headlines(api_key, param) 
        return {"tool": "NewsAPI", "param": param, "result": res}

    # 3. OPENWEATHER API
    if tool.lower() == "openweather":
        api_key = os.getenv("OPENWEATHER_KEY")
        res = openweather_current(api_key, param)
        return {"tool": "OpenWeather", "param": param, "result": res}
    
    return {"tool": tool, "param": param, "result": {"success": False, "error": f"Herramienta desconocida: {tool}"}}


# --- 4. Bucle Principal del Agente (Recursividad) ---

def answer_with_agent(user_query: str, rag_summary: str, df_clean: pd.DataFrame, max_steps: int = 3) -> Tuple[str, str]:
    """
    Función recursiva que actúa como el cerebro del Agente Gemini. 
    Llama al modelo, procesa las llamadas a herramientas y genera la respuesta final.
    """
    tool_history = []
    
    # --------------------------------------------------------
    # VALIDACIÓN DE CLIENTE (Maneja el AttributeError)
    # --------------------------------------------------------
    if GEMINI_CLIENT is None:
        error_msg = "El cliente de Gemini no se inicializó correctamente (GOOGLE_API_KEY no encontrada o inválida)."
        return f"⚠️ Error del Agente: {error_msg}. La aplicación está en modo Fallback.", error_msg
    
    # --------------------------------------------------------
    
    for step in range(max_steps):
        
        # DEFINICIÓN DEL PROMPT DEL SISTEMA (System Prompt) usando f-string
        system = f"""
        Eres un asistente experto en análisis de datos de los Juegos Olímpicos.
        Tu tarea principal es responder las preguntas del usuario de forma precisa y concisa.
        
        [REGLAS DE TOOLS]
        Si la pregunta es de CLASIFICACIÓN, RANKING, o un DATO ESPECÍFICO de un país (medallas/posiciones, INCLUYENDO FILTRADO POR AÑO), DEBES usar la herramienta 'OlympicData'.
        Si la pregunta es de NOTICIAS, usa 'NewsAPI'. Si la pregunta es de CLIMA, usa 'OpenWeather'.
        
        FORMATO DE SALIDA:
        - Si necesitas usar una herramienta: TOOL_CALL: NombreDeLaTool|ParámetroDeBúsqueda
        - Si no necesitas usar una herramienta o ya tienes la respuesta: [Respuesta final aquí]
        
        Ejemplo 1 (Ranking): TOOL_CALL: OlympicData|Qué país tiene más medallas de oro en 2024?
        
        [CONTEXTO RAG]
        {rag_summary} 
        
        Usa el contexto RAG proporcionado si es relevante. Si no lo es, omítelo.
        """

        # PREPARACIÓN Y LLAMADA AL MODELO
        if tool_history:
            # Si hay resultados de herramientas, se formatean para el siguiente paso de razonamiento
            history_text = "\n\n--- HISTORIAL DE HERRAMIENTAS ---\n" + "\n".join([
                f"TOOL_CALL_RESULT ({h['tool']}): {h['result'].get('result', h['result'].get('error', 'Error desconocido'))}"
                for h in tool_history
            ])
            prompt_with_history = user_query + history_text
        else:
            prompt_with_history = user_query
            
        print(f"\n📢 Paso {step+1}: Enviando a Gemini. Prompt: {prompt_with_history}")

        try:
            response = GEMINI_CLIENT.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_with_history,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system,
                    tools=ALL_TOOLS
                )
            )
        except APIError as e:
             error_msg = f"Error en la API de Gemini (Código: {e.status_code}). Verifica tu clave o cuota."
             return f"⚠️ {error_msg}", error_msg


        # ANÁLISIS DE RESPUESTA
        match = re.search(r"TOOL_CALL:\s*([^|]+)\|(.+)", response.text, re.IGNORECASE)
        
        if match:
            tool_name = match.group(1).strip()
            tool_param = match.group(2).strip()
            
            print(f"🛠️ Llamada a Tool detectada: {tool_name} con parámetro: '{tool_param}'")
            
            # Procesar la llamada y obtener el resultado
            tool_result = process_tool_call(tool_name, tool_param, df_clean)
            
            # Guardar el resultado en el historial
            tool_history.append(tool_result)
            
            # Si la herramienta es OlympicData y tuvo éxito, actualizamos el RAG Summary
            if tool_result['result'].get('success') and tool_result['tool'] == "OlympicData":
                 rag_summary = f"Resultado exacto de la base de datos: {tool_result['result']['result']}"
            
            # Continuar el bucle para permitir a Gemini razonar con el resultado
            continue 

        # Si no hay llamada a herramienta, es la respuesta final
        else:
            final_answer = response.text.strip()
            
            tool_log = "\n".join([
                f"({h['tool']}) Parámetro: {h['param']} -> Resultado: {h['result'].get('result', h['result'].get('error'))}" 
                for h in tool_history
            ])
            
            print("🛑 Respuesta final generada por Gemini.")
            return final_answer, tool_log

    # Si el bucle termina sin una respuesta final
    tool_log = "\n".join([f"({h['tool']}) Parámetro: {h['param']} -> Resultado: {h['result'].get('result', h['result'].get('error'))}" for h in tool_history])
    return "El Agente alcanzó el límite de pasos sin generar una respuesta final.", tool_log