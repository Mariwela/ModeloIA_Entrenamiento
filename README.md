# 🏅 Agente Olímpico Inteligente

Un asistente conversacional avanzado capaz de responder preguntas sobre los Juegos Olímpicos (2000–2024), comparar países, ofrecer datos curiosos, consultar el clima o la hora actual, combinando IA generativa (Gemini), RAG (búsqueda semántica) y herramientas funcionales (Tools).

## 🚀 Características principales

✅ RAG + Gemini: búsqueda contextual en datos y generación natural de respuestas
✅ Datos reales: medallero olímpico 2000–2024
✅ Herramientas integradas:

🧠 Datos curiosos sobre los Juegos

🌤️ Clima actual (API OpenWeather)

⏰ Hora y fecha actuales

📊 Comparación entre países por resultados
✅ Interfaz visual moderna con Gradio
✅ Soporte de preguntas semánticas y numéricas

## ⚙️ Instalación
### 1. Clona el repositorio
git clone https://github.com/usuario/agente-olimpico.git
cd agente-olimpico

### 2. Crea un entorno virtual
python -m venv venv
source venv/bin/activate    # En Linux / macOS
venv\Scripts\activate       # En Windows

### 3. Instala dependencias
pip install -r requirements.txt

### 4. Crea el archivo .env

En el directorio raíz, crea un archivo .env con tus claves API:

GOOGLE_API_KEY=tu_clave_de_gemini
OPENWEATHER_KEY=tu_clave_de_openweather
CHROMA_DIR=./chroma_db

## 🧠 Uso
### 🔹 Modo interfaz (Gradio)

Lanza la interfaz gráfica:

python app_gradio.py


Se abrirá en tu navegador una ventana tipo chat donde puedes preguntar libremente:

Ejemplos:

“¿Qué país ganó más medallas de oro en 2020?”

“Compara España y Italia en 2020.”

“Dame un dato curioso sobre los Juegos Olímpicos.”

“Qué clima hace en Tokio ahora mismo.”

### 🔹 Modo consola

Para probarlo en terminal:

python main.py --run

## 📂 Estructura del proyecto
Archivo / Carpeta	Descripción
app_gradio.py	Define la interfaz gráfica con Gradio. Contiene el diseño visual (chat, colores, botones, etc.) y las funciones de interacción entre usuario y agente.
main.py	Ejecuta el agente en modo consola, ideal para depuración y pruebas sin entorno gráfico.
agente.py	Núcleo del agente inteligente. Decide si usar una herramienta, una búsqueda semántica o el modelo generativo. Combina lógica de decisión y formato de respuesta.
tools.py	Contiene las herramientas funcionales (Tools): hora actual, clima (OpenWeather), comparación entre países y datos curiosos.
rag.py	Implementa el sistema RAG (Retrieval-Augmented Generation). Recupera contexto desde una base vectorial (ChromaDB) y lo combina con el modelo Gemini para generar respuestas precisas.
olympic_medals_2000_2024.csv	Dataset del medallero olímpico histórico (2000–2024) con columnas: país, año, medallas, ranking, totales, etc.
chroma_db/	Carpeta persistente de la base vectorial usada por RAG para búsquedas semánticas.
.env	Variables de entorno que guardan las claves de las APIs (Gemini, OpenWeather). ⚠️ No subir este archivo a GitHub.
requirements.txt	Lista de dependencias Python necesarias para ejecutar el agente.
README.md	Este documento, con toda la explicación del proyecto.
## 💡 Ejemplos de interacción
Ejemplo de pregunta	Tipo de respuesta
“¿Qué país ganó más medallas de oro en 2020?”	📊 Datos estructurados (CSV - medallero)
“Compara España y Italia en 2020”	📈 Tool de comparación numérica
“Dame un dato curioso sobre los Juegos Olímpicos”	🧠 Tool: dato curioso aleatorio
“Qué clima hace en París”	🌦️ Tool: API de OpenWeather
“Qué hora es ahora”	🕒 Tool: hora local actual
