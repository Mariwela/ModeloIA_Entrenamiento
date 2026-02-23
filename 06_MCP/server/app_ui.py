import streamlit as st
import os
import sys

# 1. Configurar ruta
sys.path.append(os.getcwd())

# 2. Configuración de Streamlit
st.set_page_config(page_title="Olympic Intelligence Agent", page_icon="🏆", layout="wide")

# 3. Importar el agente
from agents.agente_langgraph import app 

# --- INTERFAZ ---
st.title("🏆 Olympic Intelligence Agent")
st.markdown("""
Esta interfaz conecta un **Agente LangGraph** con un **Servidor MCP** para analizar 
el rendimiento olímpico con datos reales y contexto histórico.
""")

# Barra lateral para inputs
with st.sidebar:
    st.header("📍 Parámetros")
    pais = st.text_input("País:", value="Spain")
    año = st.number_input("Año:", min_value=1896, max_value=2024, value=1992)
    st.divider()
    consultar = st.button("🚀 Consultar Agente", use_container_width=True)

# Área principal
if consultar:
    with st.status("🤖 El agente está trabajando...", expanded=True) as status:
        # Nota: Asegúrate de que tu agente acepte estos nombres de llaves
        inputs = {"target_country": pais, "target_year": año}
        config = {"configurable": {"thread_id": "demo_1"}}
        
        st.write("🔍 **Fase 1:** Conectando con servidor MCP...")
        
        final_res = ""
        # Ejecutamos el flujo de LangGraph
        for output in app.stream(inputs, config):
            for key, value in output.items():
                if key == "get_data":
                    st.success("✅ Datos recuperados del CSV.")
                    # Si value tiene 'data_results', lo mostramos opcionalmente
                elif key == "get_analysis":
                    st.info("🧠 Generando análisis cualitativo...")
                elif key == "write_report":
                    final_res = value.get('final_answer', "No se pudo generar el reporte.")
        
        status.update(label="✅ ¡Proceso completado!", state="complete", expanded=False)

    # Mostrar resultado final con estilo
    st.divider()
    st.header(f"📊 Informe: {pais} en {año}")
    st.markdown(final_res)

else:
    st.info("👈 Introduce un país y un año en la barra lateral para comenzar.")