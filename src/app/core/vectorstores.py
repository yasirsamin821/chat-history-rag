from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever

from configs.config import (
    TEXT_CHROMA_COLLECTION,
    TEXT_CHROMA_DIR,
    CODE_CHROMA_COLLECTION,
    CODE_CHROMA_DIR,
)
from src.app.embeddings.embeddings import LMStudioEmbeddings, LlamaCppEmbeddings

text_embeddings = LMStudioEmbeddings()
code_embeddings = LlamaCppEmbeddings()

text_vectorstore = Chroma(
    collection_name=TEXT_CHROMA_COLLECTION,
    persist_directory=TEXT_CHROMA_DIR,
    embedding_function=text_embeddings,
)
code_vectorstore = Chroma(
    collection_name=CODE_CHROMA_COLLECTION,
    persist_directory=CODE_CHROMA_DIR,
    embedding_function=code_embeddings,
)


def _load_all_documents(vectorstore, label: str):
    collection = vectorstore._collection
    count = collection.count()
    print(f"[{label}] total chunks in Chroma: {count}")

    docs = []
    batch_size = 500
    for offset in range(0, count, batch_size):
        data = collection.get(limit=batch_size, offset=offset, include=["documents", "metadatas"])
        for text, metadata in zip(data["documents"], data["metadatas"]):
            docs.append(Document(page_content=text, metadata=metadata))
    print(f"[{label}] loaded {len(docs)} documents")
    return docs


text_documents = _load_all_documents(text_vectorstore, "text")
# Code pipeline is dense-only (matches rag_api.py -- notebook never wired
# up BM25/ensemble for code), so we don't build a BM25 corpus for it.

text_dense_retriever = text_vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
text_bm25_retriever = BM25Retriever.from_documents(text_documents)
text_bm25_retriever.k = 20
