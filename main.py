import argparse
import pandas as pd
from vector_db import VectorDB
from rag import RAG


def build_database():
    """Reconstruye la base de datos desde el CSV."""
    csv_path = "olympic_medals_2000_2024.csv"
    print(f"📂 Cargando datos desde {csv_path}...")

    df = pd.read_csv(csv_path)
    print(f"✅ CSV cargado correctamente: {len(df)} registros")

    vdb = VectorDB()
    vdb.clear()
    vdb.upsert_from_dataframe(df)
    print("🎯 Base de datos Chroma reconstruida con éxito.")


def interactive_rag():
    """Ejecuta el modo de preguntas RAG."""
    rag = RAG()
    print("✅ RAG listo. Escribe una pregunta o 'salir' para terminar.\n")

    while True:
        q = input("❓ Pregunta: ").strip()
        if q.lower() in ["salir", "exit", "quit"]:
            break

        try:
            ans, docs = rag.answer_question(q)
            print("\n🤖 Respuesta:\n", ans)
            print("\n📄 Documentos recuperados (top 5):")
            for d in docs[:5]:
                print(" -", d)
        except Exception as e:
            print(f"⚠️ Error procesando la consulta: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Olympic RAG Demo")
    parser.add_argument("--build-db", action="store_true", help="Reconstruye la base de datos desde el CSV")
    parser.add_argument("--run", action="store_true", help="Ejecuta el chat RAG")

    args = parser.parse_args()

    if args.build_db:
        build_database()
    elif args.run:
        interactive_rag()
    else:
        print("⚙️ Usa uno de los modos:\n")
        print("   python main.py --build-db   → reconstruye la base de datos")
        print("   python main.py --run        → inicia el chat interactivo")
