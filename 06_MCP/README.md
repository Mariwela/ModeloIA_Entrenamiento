Activar el entorno virtual:
python -m venv venv
source venv/bin/activate   # o venv\Scripts\activate en Windows


Instalas dependencias
pip install -r requirements.txt

Instala el Inspector global de MCP:
npm install -g @modelcontextprotocol/inspector

Crea un archivo .env en la raíz del proyecto y añade tu API Key:
GROQ_API_KEY=tu_clave_de_groq_aqui


Guía de Ejecución:

Terminal 1 (Inspector stdio):
mcp-inspector python server/main.py

Terminal 2 (Servidor para Cherry Studio):
python server/main.py sse

Terminal 3 (Probar Agente LangGraph):
Configurar el enpoint "zapier_webhook_url" en tools/external_mcp.py
python agents/agente_langgraph.py

Terminal 4 (Interfaz Streamlit):
streamlit run server/app_ui.py


-----------------------------------------------------
Cherry Studio web oficial: https://www.cherry-ai.com/
Busca el icono de Ajustes (Settings) -> haz clic en MCP Server -> Haz clic en el botón + Add ->
Configúralo así:
Name: Medallero Olímpico
Type: SSE
URL: http://127.0.0.1:8000/sse

Pulsa Save y asegúrate de que el interruptor esté en ON

Default Topic chat -> Default Assistant -> MCP Servers -> elegir manual y activar tu MCP Server
------------------------------------------------------

cerrar el proceso que está bloqueando el puerto 6277:
Stop-Process -Id (Get-NetTCPConnection -LocalPort 6277).OwningProcess -Force

