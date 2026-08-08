from pathlib import Path

DATASET = '/home/samin96/rag_project/chat.html'

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
LLAMACPP_BASE_URL = "http://127.0.0.1:8080/v1"

ROUTER_MODEL = "qwen2.5-coder-1.5b-instruct"

TEXT_CHROMA_COLLECTION = "chatgpt_rag"
TEXT_CHROMA_DIR = str(PROJECT_ROOT / "data" / "chroma" / "no_code_advanced_chroma_db")
TEXT_EMBED_MODEL = "text-embedding-granite-embedding-107m-multilingual"
TEXT_LLM_MODEL = "qwen2.5-coder-1.5b-instruct"

CODE_CHROMA_COLLECTION = "chatgpt_rag"
CODE_CHROMA_DIR = str(PROJECT_ROOT / "data" / "chroma" / "with_code_advanced_chroma_db")
CODE_EMBED_MODEL = "jina-code-embeddings-1.5b"
CODE_EMBED_API_KEY = "dummy"
CODE_LLM_MODEL = "qwen2.5-coder-1.5b-instruct"

print(f"PROJECT_ROOT: {PROJECT_ROOT}")
print(TEXT_CHROMA_DIR)