
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from configs.config import ROUTER_MODEL, TEXT_LLM_MODEL, CODE_LLM_MODEL
from src.app.rag.schemas import ChatRequest, ChatResponse
from src.app.rag.router import route_request
from pipelines.rag_pipeline import condense_question, resolve_pipeline
from src.app.rag.streaming import rag_answer_stream
from src.app.core.vectorstores import text_documents

app = FastAPI(title="Routed Personal RAG API (stateful, SSE)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    history = [t.dict() for t in req.history]

    route = route_request(req.message)
    llm, retrieve_fn, answer_prompt = resolve_pipeline(route)

    standalone = condense_question(llm, req.message, history)
    docs = retrieve_fn(standalone, top_k=4)
    context = "\n\n".join(doc.page_content for doc in docs)
    history_text = "\n".join(f"{t['role']}: {t['content']}" for t in history)

    messages = answer_prompt.invoke({"history": history_text, "context": context, "question": req.message})
    response = llm.invoke(messages)

    sources = [doc.metadata.get("id", "unknown") for doc in docs]
    return ChatResponse(
        route=route,
        answer=response.content,
        sources=sources,
        standalone_question=standalone,
    )


@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    history = [t.dict() for t in req.history]
    return StreamingResponse(
        rag_answer_stream(req.message, history),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable proxy buffering, e.g. through cloudflared
        },
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "text_chunks_loaded": len(text_documents),
        "router_model": ROUTER_MODEL,
        "text_llm_model": TEXT_LLM_MODEL,
        "code_llm_model": CODE_LLM_MODEL,
    }
