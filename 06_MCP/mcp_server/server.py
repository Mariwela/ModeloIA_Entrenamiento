import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from groq import Groq

load_dotenv()

# Verificar API Key de Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError(
        "ERROR: No se encontró la API Key de Groq. "
        "Asegúrate de configurar GROQ_API_KEY en tu archivo .env"
    )

client = Groq(api_key=GROQ_API_KEY)

# Verificar transporte MCP
# Establecer en .env (stdio / streamable-http)
MCP_TRANSPORT = os.getenv("MCP_TRANSPORT")
if MCP_TRANSPORT not in ("stdio", "streamable-http"):
    print(
        f"Advertencia: MCP_TRANSPORT no definido o inválido ('{MCP_TRANSPORT}'). "
        "Se usará el valor por defecto 'stdio'."
    )
    MCP_TRANSPORT = "stdio"

mcp = FastMCP("Servidor Olimpico MCP")

@mcp.tool(description="Obtener información de un país en los Juegos Olímpicos")
def get_country_medals(country: str) -> str:
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{country}_at_the_Olympics"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("extract", "No se encontró información")
        return f"Error al consultar la API: {response.status_code}"
    except Exception as e:
        return f"Error al conectar con la API: {str(e)}"

@mcp.tool(description="Analizar desempeño olímpico usando Groq AI")
def analyze_performance(text: str) -> str:
    try:
        response = client.completions.create(
            model="groq-alpha-1",
            prompt=f"Analiza este texto sobre Juegos Olímpicos y genera insights:\n{text}",
            max_tokens=500
        )
        return response.choices[0].text
    except Exception as e:
        return f"Error al llamar a Groq AI: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport=MCP_TRANSPORT)