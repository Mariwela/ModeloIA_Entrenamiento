import sys
import os
sys.path.append(os.getcwd()) 
from mcp.server.fastmcp import FastMCP
from tools.medals_api import get_olympic_medals
from tools.llm_analysis import analyze_country_performance

mcp = FastMCP("Olympic Intelligence Server")

@mcp.tool()
def medals(country: str, year: int) -> str:
    """Consulta las medallas olímpicas de un país en un año específico."""
    data = get_olympic_medals(country, year)
    
    # Si hay un error en la búsqueda
    if "error" in data:
        return f"❌ Error: {data['error']}"
    
    # Formateamos una respuesta "bien visible" y elegante
    # Esto elimina el aviso de 'Unstructured Content' y se ve genial
    reporte = (
        f"📊 RESULTADOS OLÍMPICOS: {country.upper()} ({year})\n"
        f"------------------------------------------\n"
        f"🥇 Oros: {data['gold']}\n"
        f"🥈 Platas: {data['silver']}\n"
        f"🥉 Bronces: {data['bronze']}\n"
        f"🏆 TOTAL: {data['total']} medallas\n"
        f"------------------------------------------\n"
        f"📌 Fuente: {data['source']}"
    )
    return reporte

@mcp.tool()
def analyze(country: str) -> str:
    """Proporciona un análisis histórico del desempeño olímpico de un país."""
    analisis = analyze_country_performance(country)
    # Le añadimos un encabezado para que en el Inspector se distinga rápido
    return f"🧠 ANÁLISIS DE EXPERTO PARA {country.upper()}:\n\n{analisis}"

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sse":
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")