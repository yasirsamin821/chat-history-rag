from src.app.core.vectorstores import (
    text_dense_retriever,
    text_bm25_retriever,
    code_vectorstore,
)


def hybrid_retrieve(query: str, top_k: int = 4):
    dense_docs = text_dense_retriever.invoke(query)
    bm25_docs = text_bm25_retriever.invoke(query)

    merged = {}
    for doc in dense_docs:
        merged[doc.metadata["id"]] = doc
    for doc in bm25_docs:
        if doc.metadata["id"] not in merged:
            merged[doc.metadata["id"]] = doc

    return list(merged.values())[:top_k]


def dense_retrieve_code(query: str, top_k: int = 4):
    retriever = code_vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": top_k})
    return retriever.invoke(query)
