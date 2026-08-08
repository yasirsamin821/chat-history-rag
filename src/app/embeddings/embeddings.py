import requests
from langchain_core.embeddings import Embeddings

from configs.config import (
    LM_STUDIO_BASE_URL,
    TEXT_EMBED_MODEL,
    LLAMACPP_BASE_URL,
    CODE_EMBED_MODEL,
    CODE_EMBED_API_KEY,
)


class LMStudioEmbeddings(Embeddings):
    def __init__(self, base_url=LM_STUDIO_BASE_URL, model=TEXT_EMBED_MODEL):
        self.base_url = base_url
        self.model = model

    def _embed(self, texts):
        response = requests.post(
            f"{self.base_url}/embeddings",
            json={"model": self.model, "input": texts},
            timeout=300,
        )
        response.raise_for_status()
        return [item["embedding"] for item in response.json()["data"]]

    def embed_documents(self, texts):
        return self._embed(texts)

    def embed_query(self, text):
        return self._embed([text])[0]


class LlamaCppEmbeddings(Embeddings):
    def __init__(self, base_url=LLAMACPP_BASE_URL, model=CODE_EMBED_MODEL, api_key=CODE_EMBED_API_KEY):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key

    def _embed(self, texts):
        response = requests.post(
            f"{self.base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={"model": self.model, "input": texts},
            timeout=300,
        )
        response.raise_for_status()
        return [item["embedding"] for item in response.json()["data"]]

    def embed_documents(self, texts):
        return self._embed(texts)

    def embed_query(self, text):
        return self._embed([text])[0]
