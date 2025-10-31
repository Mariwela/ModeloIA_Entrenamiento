# Scraping-con-Playwright-RAG-TOOLS-GRADIO
Scraping de una página de Juegos Olýmpicos, almacena esta información en una base de datos vectorial (ChromaDB) y usa RAG para dar respuestas sobre los rankings de medallas

Primero creamos un entorno virtual:

  python -m venv venv

  venv\Scripts\activate

Luego instalamos dependencias:

  pip install playwright pandas chromadb sentence_transformers lxml gradio chromadb python-dotenv

  playwright install


## 1. EXTRACCIÓN DE DATOS - scraper.py
https://en.wikipedia.org/wiki/2024_Summer_Olympics_medal_table
Utiliza la biblioteca playwright para abrir una instancia de navegador (headless) y navegar a las páginas de la tabla de medallas de los Juegos Olímpicos de Verano désde el 1996 hasta 2024 en Wikipedia.

Una vez que la página está cargada, obtiene el código HTML.

Analiza el HTML y encontrar la tabla de medallas específica.

pandas se utiliza para leer directamente el HTML de la tabla y convertirlo en un DataFrame, una estructura de datos tabular conveniente para el procesamiento.

Normaliza las columnas a ["Rank", "Nation", "Gold", "Silver", "Bronze", "Total"] y devuelve el DataFrame.

## 2. ALMACENAMIENTO VECTORIAL - vector_db.py
Limpia el DataFrame de pandas de símbolos especiales y convierte las columnas de medallas y Rank a tipos de datos enteros.

Embeddings: Configura la función de embedding para convertir el texto en vectores.

El proyecto usa por defecto embeddings locales con SentenceTransformers.

Crea una colección llamada "olympic_medals" en ChromaDB.

## 3. RAG - rag.py
Obtiene los documentos vectoriales más relevantes a la consulta del usuario.

Analiza la consulta, valida datos y ordena el DataFrame real según el tipo de medalla extraído

Genera nuevos "documentos" de contexto a partir de los países con mejores resultados del DataFrame.

Generación del Resumen: Utiliza los datos del DataFrame ordenado para construir una respuesta final textual que identifica al país líder y a otros destacados.
## 4. rag_tools.py


## 6. TOOLS - tools.py
Contiene un conjunto de funciones "tools" que llaman a APIs externas y devuelven resultados sencillos para enriquecer respuestas.

## 7. INTERFAZ - gradio_app.py
Se ha añadido una interfaz web con Gradio para interactuar con el flujo RAG y las tools.

- La app scrapea la tabla, crea la colección vectorial y expone una caja de texto para consultas.
- Output para las tools (NewsAPI u OpenWeather).
- Devuelve la respuesta con un modelo llm y el RAG (resumen generado a partir de los datos) y el resultado de la tool seleccionada.
