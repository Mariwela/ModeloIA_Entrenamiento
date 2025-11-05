import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "./chroma_db"

class VectorDB:
    def __init__(self):
        # Inicializa cliente Chroma y colección
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection = self.client.get_or_create_collection(
            "olympic_medals",
            embedding_function=embedding_functions.DefaultEmbeddingFunction()
        )

    def clear(self):
        """Elimina la colección existente."""
        try:
            self.client.delete_collection("olympic_medals")
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            "olympic_medals",
            embedding_function=embedding_functions.DefaultEmbeddingFunction()
        )

    def upsert_from_dataframe(self, df):
        """Carga datos del CSV en Chroma."""
        docs = []
        ids = []
        for i, row in df.iterrows():
            doc = (
                f"Year: {row['year']} | Country: {row['country']} | "
                f"Gold: {row['gold']}, Silver: {row['silver']}, "
                f"Bronze: {row['bronze']}, Total: {row['total']}"
            )
            docs.append(doc)
            ids.append(str(i))

        self.collection.add(documents=docs, ids=ids)
        print(f"✅ {len(docs)} documentos añadidos a la colección.")

    def query(self, query_text, n_results=5):
        """Busca los documentos más similares."""
        results = self.collection.query(query_texts=[query_text], n_results=n_results)
        return results.get("documents", [[]])[0]
