# inspect_db.py
import chromadb

CHROMA_PATH = "./chroma_db"

client = chromadb.PersistentClient(path=CHROMA_PATH)

# Ver todas las colecciones existentes
collections = client.list_collections()
print("📦 Colecciones disponibles:")
for c in collections:
    print(f" - {c.name}")

# Obtener la colección principal
collection = client.get_collection("olympic_medals")

# Mostrar conteo
print(f"\n📊 La colección 'olympic_medals' contiene {collection.count()} documentos.\n")

# Obtener algunos documentos (primeros 5)
data = collection.get(limit=5)

# Mostrar estructura completa para depurar
print("🔍 Estructura interna de los primeros documentos:\n")
for i, doc in enumerate(data.get("documents", []), 1):
    print(f"{i}. {doc}")

# Si quieres ver también los IDs:
print("\n🆔 IDs de los documentos obtenidos:")
print(data.get("ids", []))
