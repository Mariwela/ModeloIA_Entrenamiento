import re
from tools import get_weather, generate_fun_fact, compare_countries, get_current_time
from rag import RAG

class OlympicAgent:
    """
    Agente que decide si usar una Tool o delegar en RAG/Gemini.
    Devuelve texto + fuente (como tupla para app_gradio.py)
    """

    def __init__(self):
        self.rag = RAG()
        self.tools = {
            "weather": get_weather,
            "fun_fact": generate_fun_fact,
            "compare": compare_countries,
            "time": get_current_time
        }

    # ============================
    # 🔍 Selección de herramienta
    # ============================
    def decide_and_call_tool(self, query: str):
        q = query.lower().strip()

        # Hora / fecha
        if any(tok in q for tok in ["hora", "qué hora", "dime la hora", "fecha", "hoy"]):
            return self.tools["time"](), "🕒 Tool: get_current_time()"

        # Dato curioso
        if any(tok in q for tok in ["dato curioso", "curiosidad", "hecho interesante", "sabías que"]):
            return self.tools["fun_fact"](), "🧠 Tool: generate_fun_fact()"

        # Clima
        if any(tok in q for tok in ["clima", "tiempo", "temperatura", "hace calor", "hace frío"]):
            match = re.search(r"en ([a-záéíóúñ \-]+)", q)
            city = match.group(1).strip() if match else "Madrid"
            return self.tools["weather"](city), f"🌤️ Tool: get_weather('{city}')"

        # Comparación entre países
        if "compara" in q or " vs " in q or " v " in q or " o " in q:
            # Extraer año
            year_match = re.search(r"(20\d{2})", q)
            year = int(year_match.group()) if year_match else 2024

            # Buscar dos países después de palabras clave
            pattern = r"(?:compara|entre|qué país obtuvo mejor resultado en|qué país ganó más medallas en)?\s*([a-záéíóúñ\s]+?)\s+(?:vs|v|o|y)\s+([a-záéíóúñ\s]+)"
            m = re.search(pattern, q)
            if m:
                c1 = m.group(1).strip()
                c2 = m.group(2).strip()
                # Limpiar basura como "qué país obtuvo mejor resultado en 2020"
                c1 = re.sub(r"(qué país|obtuvo|mejor|resultado|en|los|juegos|olímpicos|olimpicos|de|el|la|del|los)", "", c1, flags=re.I).strip()
                c2 = re.sub(r"(qué país|obtuvo|mejor|resultado|en|los|juegos|olímpicos|olimpicos|de|el|la|del|los)", "", c2, flags=re.I).strip()

                resp = self.tools["compare"](c1, c2, year)
                return resp, f"📊 Tool: compare_countries({c1}, {c2}, {year})"

        return None, None

    # ============================
    # 💬 Respuesta final
    # ============================
    def answer(self, query: str):
        # 1️⃣ Intentar con Tools
        tool_resp, tool_src = self.decide_and_call_tool(query)
        if tool_resp:
            return tool_resp, tool_src

        # 2️⃣ Delegar a RAG
        answer, docs = self.rag.answer_question(query)

        # 3️⃣ Determinar fuente
        if isinstance(answer, str) and any(x in answer for x in ["En ", "ocupó", "medallas", "fue el país"]):
            source = "📊 Datos estructurados (CSV - medallero)"
        elif isinstance(answer, str) and answer.startswith("⚠️"):
            source = "⚠️ Error (modelo o datos faltantes)"
        else:
            source = "💬 Gemini + RAG semántico"

        return answer, source


# ============================
# ⚡ Interfaz para otros módulos
# ============================
def handle_agent_query(query: str):
    agent = OlympicAgent()
    return agent.answer(query)
