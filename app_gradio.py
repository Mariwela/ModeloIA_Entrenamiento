import gradio as gr
from agente import OlympicAgent

# ==============================
# 🚀 Inicialización del agente
# ==============================
agent = OlympicAgent()

# ==============================
# 💬 Función principal del chatbot
# ==============================
def chat_with_agent(message, history):
    """
    Procesa la consulta del usuario y devuelve respuesta + fuente de información.
    """
    try:
        answer, source = agent.answer(message)

        # Estructura del mensaje tipo "messages" (nuevo formato Gradio)
        history = history or []
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": f"{answer}\n\n📊 **Fuente:** {source}"})
        return history, history

    except Exception as e:
        history = history or []
        history.append({"role": "assistant", "content": f"⚠️ Error: {e}"})
        return history, history


# ==============================
# 🎨 Interfaz con diseño mejorado
# ==============================
custom_css = """
body {
    background: linear-gradient(135deg, #0b3d2e, #164a41);
    color: #f8f9fa;
}

#chatbot {
    border-radius: 15px;
    background-color: #ffffff;
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.25);
}

#input-box textarea {
    font-size: 18px;
    height: 130px;
    border-radius: 10px;
    border: 2px solid #1a6f50;
}

#send-btn {
    background-color: #1b5e20;
    color: white;
    font-weight: bold;
    border-radius: 10px;
}

#clear-btn {
    background-color: #e8f5e9;
    color: #2e7d32;
    font-size: 13px;
    padding: 4px 8px;
    border-radius: 8px;
    border: 1px solid #a5d6a7;
}

/* Chat bubbles */
.message.user {
    background-color: #c8e6c9;
    color: #1b5e20;
    border-radius: 10px;
}
.message.bot {
    background-color: #f1f8e9;
    color: #2e7d32;
    border-radius: 10px;
}
"""

with gr.Blocks(
    title="🏅 Agente Olímpico Inteligente",
    theme=gr.themes.Soft(primary_hue="green", secondary_hue="emerald"),
    css=custom_css
) as demo:

    # Encabezado
    gr.Markdown(
        """
        <div style="text-align:center; margin-bottom: 10px;">
        <h1>🏅 Agente Olímpico Inteligente</h1>
        <p style="font-size:16px; color:gray;">
        Descubre datos, compara países y obtén curiosidades sobre los Juegos Olímpicos (2000–2024)
        </p>
        </div>
        """,
        elem_id="header"
    )

    with gr.Row():
        # Panel lateral
        with gr.Column(scale=1, min_width=260):
            gr.Markdown(
                """
                ### 🧭 Ejemplos de preguntas
                - 🥇 “¿Qué país ganó más medallas de oro/plata/bronce en un año específico?”
                - ⚔️ “Compara dos paises en un año concreto”
                - 💡 “Dame un dato curioso sobre los Juegos Olímpicos”
                - ☀️ “Qué clima hace en una ciudad concreta ahora mismo”
                - ⏰ “Qué hora es en un país concreto”
                """,
                elem_id="examples"
            )

        # Columna principal del chat
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                type="messages",
                height=400,
                label="Chat Olímpico 🤖",
                elem_id="chatbot",
                show_copy_button=True
            )

            # Campo de texto amplio
            user_input = gr.Textbox(
                placeholder="Escribe tu pregunta aquí...",
                label="💬 Tu pregunta",
                elem_id="input-box",
                lines=5,
            )

            # Botones debajo del cuadro
            with gr.Row(variant="compact", elem_id="buttons-row"):
                send_btn = gr.Button("🚀 Enviar", elem_id="send-btn")
                clear_btn = gr.Button("🧹 Limpiar historial", elem_id="clear-btn")

            # Eventos
            send_btn.click(chat_with_agent, [user_input, chatbot], [chatbot, chatbot])
            user_input.submit(chat_with_agent, [user_input, chatbot], [chatbot, chatbot])
            clear_btn.click(lambda: None, None, chatbot, queue=False)

    # Pie de página
    gr.Markdown(
        """
        ---
        <div style="text-align:center; color:gray; margin-top:10px;">
        Desarrollado por MARINA, ERIC Y DANIEL</b>.
        </div>
        """,
        elem_id="footer"
    )

# ==============================
# 🚀 Lanzar servidor
# ==============================
if __name__ == "__main__":
    demo.launch(server_name="localhost", server_port=7860)
