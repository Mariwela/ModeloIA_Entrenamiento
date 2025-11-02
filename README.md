# 🏅 Agente Olímpico Inteligente

Un asistente conversacional avanzado capaz de responder preguntas sobre los Juegos Olímpicos (2000–2024), comparar países, ofrecer datos curiosos, consultar el clima o la hora actual, combinando IA generativa (Gemini), RAG (búsqueda semántica) y herramientas funcionales (Tools).

## 🚀 Características principales

✅ RAG + Gemini: búsqueda contextual en datos y generación natural de respuestas

✅ Datos reales: medallero olímpico 2000–2024

✅ Herramientas integradas:

📊 Comparación entre países por resultados

🧠 Datos curiosos sobre los Juegos

🌤️ Clima actual (API OpenWeather)

⏰ Hora y fecha actuales

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
python app_gradio.py


Se abrirá en tu navegador una ventana tipo chat donde puedes preguntar libremente:

Ejemplos:

“¿Qué país ganó más medallas de oro en 2020?”

“Compara España y Italia en 2020.”

“Dame un dato curioso sobre los Juegos Olímpicos.”

“Qué clima hace en Tokio ahora mismo.”

### 🔹 Modo consola
python main.py --run

## 📂 Estructura del proyecto
Archivo / Carpeta	Descripción
### requirements.tx
Lista de dependencias Python necesarias para ejecutar el agente.
### app_gradio.py
Define la interfaz gráfica con Gradio. Contiene el diseño visual (chat, colores, botones, etc.) y las funciones de interacción entre usuario y agente.
### main.py
Ejecuta el agente en modo consola, ideal para depuración y pruebas sin entorno gráfico.
### scraping.py
Script de web scraping para obtener o actualizar los datos del medallero olímpico desde fuentes online (Wikipedia). Limpia, estructura y guarda los resultados en olympic_medals_2000_2024.csv, el dataset del medallero olímpico histórico con columnas: país, año, medallas, ranking, totales, etc.
### vector_db.py
Construye y gestiona la base vectorial ChromaDB chroma_db/. Convierte los textos del dataset en embeddings (vectores numéricos) para que el sistema RAG pueda realizar búsquedas semánticas eficientes.
### rag.py
Implementa el sistema RAG (Retrieval-Augmented Generation). Recupera contexto desde una base vectorial (ChromaDB) y lo combina con el modelo Gemini para generar respuestas precisas.
### tools.p
Contiene las herramientas funcionales (Tools): comparación entre países, datos curiosos, hora actual y clima (OpenWeather) .
### agente.p
Núcleo del agente inteligente. Decide si usar una herramienta, una búsqueda semántica o el modelo generativo. Combina lógica de decisión y formato de respuesta.
### README.md
Este documento, con toda la explicación del proyecto.
## 💡 Ejemplos de interacción
Ejemplo de pregunta	Tipo de respuesta

“¿Qué país ganó más medallas de oro en 2020?”	📊 Datos estructurados (CSV - medallero)

“Compara España y Italia en 2020”	📈 Tool de comparación numérica

“Dame un dato curioso sobre los Juegos Olímpicos”	🧠 Tool: dato curioso aleatorio

“Qué clima hace en París”	🌦️ Tool: API de OpenWeather

“Qué hora es ahora”	🕒 Tool: hora local actual
