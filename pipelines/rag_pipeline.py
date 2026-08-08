from src.app.prompts.templates import condense_prompt, text_answer_prompt, code_answer_prompt
from src.app.rag.retrieval import hybrid_retrieve, dense_retrieve_code
from src.app.core.llms import text_llm, code_llm


def condense_question(llm, question: str, history: list[dict]) -> str:
    if not history:
        return question
    history_text = "\n".join(f"{turn['role']}: {turn['content']}" for turn in history)
    messages = condense_prompt.invoke({"history": history_text, "question": question})
    response = llm.invoke(messages)
    return response.content.strip()


def resolve_pipeline(route: str):
    if route == "CodeRetrieval":
        return code_llm, dense_retrieve_code, code_answer_prompt
    return text_llm, hybrid_retrieve, text_answer_prompt
