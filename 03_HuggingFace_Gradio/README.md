# 🏅 SUBTITULADOR AUTOMÁTICO con Hugging Face + Whisper + Gradio
Este proyecto permite subtitular automáticamente cualquier video, generar el archivo .srt, y crear una versión del video con subtítulos incrustados.

Además, incluye una función adicional que resume automáticamente el contenido hablado usando un modelo de lenguaje de Hugging Face.
## 🚀 Características principales
🎧 Transcripción automática del audio del video con Whisper (openai/whisper-small).

⏱️ Timestamps reales para sincronizar subtítulos con precisión.

💬 Generación automática de archivo .srt (SubRip).

🎬 Exportación de video subtitulado con estilo personalizado.

🧠 Resumen automático del texto transcrito con BART (facebook/bart-large-cnn).

🌐 Interfaz web interactiva creada con Gradio.

⚙️ Compatible con Google Colab, Hugging Face Spaces o ejecución local.
## 🧩 Tecnologías usadas
Componente	Descripción

Transformers (Hugging Face)	Carga y ejecución de los modelos Whisper y BART

Gradio	Interfaz web interactiva

MoviePy	Extracción del audio desde el video

FFmpeg	Creación del video con subtítulos

PySRT	Generación de archivos .srt

Hugging Face Hub	Fuente de los modelos preentrenados
