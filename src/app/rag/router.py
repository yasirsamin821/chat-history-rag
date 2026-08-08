from langchain_core.output_parsers import StrOutputParser

from src.app.core.llms import router_llm
from src.app.prompts.templates import router_prompt

router_chain = router_prompt | router_llm | StrOutputParser()


def route_request(message: str) -> str:
    """Returns 'TextRetrieval' or 'CodeRetrieval'. Defaults to TextRetrieval
    on any unparseable output instead of raising."""
    raw = router_chain.invoke({"message": message}).strip()
    normalized = raw.replace(" ", "").lower()
    if "coderetrieval" in normalized:
        return "CodeRetrieval"
    return "TextRetrieval"
