06_MCP/   
│
├── mcp_server/                # Servidor MCP principal
│   ├── server.py              # Archivo principal del servidor MCP
│   └── tools/                 # Carpeta con tus tools
│       ├── api_tools.py       # Tool que consume API externa
│       └── llm_tools.py       # Tool que usa LLM
│
├── agent/                     # Carpeta para tu agente
│   └── agent.py               # LangGraph Agent o cualquier otro agente
│
├── ui/                        # Interfaz de usuario (opcional: Gradio o Streamlit)
│   └── app.py                 # Archivo principal de la UI
│
├── requirements.txt           # Librerías necesarias para el proyecto
├── README.md                  # Explicación del proyecto, instrucciones
└── .env                       # Variables de entorno (API keys, puertos, etc.)

1. Copiar el .env.example a .env y establecer las variables de entorno
2. Iniciar servidor: python mcp_server/server.py
3. Probar el servidor desde el inspector MCP --> npx @modelcontextprotocol/inspector
    - Para streamable-http, endpoint: http://localhost:8000/mcp

