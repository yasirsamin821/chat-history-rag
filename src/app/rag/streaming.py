import json

from src.app.rag.router import route_request
from pipelines.rag_pipeline import condense_question, resolve_pipeline


def rag_answer_stream(message: str, history: list[dict]):
    route = route_request(message)
    yield f"event: route\ndata: {json.dumps(route)}\n\n"

    llm, retrieve_fn, answer_prompt = resolve_pipeline(route)

    standalone = condense_question(llm, message, history)
    docs = retrieve_fn(standalone, top_k=4)
    context = "\n\n".join(doc.page_content for doc in docs)
    history_text = "\n".join(f"{t['role']}: {t['content']}" for t in history)

    messages = answer_prompt.invoke({"history": history_text, "context": context, "question": message})

    sources = [doc.metadata.get("id", "unknown") for doc in docs]
    yield f"event: standalone\ndata: {json.dumps(standalone)}\n\n"
    yield f"event: sources\ndata: {json.dumps(sources)}\n\n"

    for chunk in llm.stream(messages):
        token = chunk.content
        if token:
            yield f"event: token\ndata: {json.dumps(token)}\n\n"

    yield "event: done\ndata: {}\n\n"
