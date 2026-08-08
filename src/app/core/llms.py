from langchain_openai import ChatOpenAI

from configs.config import (
    LM_STUDIO_BASE_URL,
    ROUTER_MODEL,
    TEXT_LLM_MODEL,
    CODE_LLM_MODEL,
)

router_llm = ChatOpenAI(
    base_url=LM_STUDIO_BASE_URL,
    api_key="lm-studio",
    model=ROUTER_MODEL,
    temperature=0,
)

text_llm = ChatOpenAI(
    base_url=LM_STUDIO_BASE_URL,
    api_key="lm-studio",
    model=TEXT_LLM_MODEL,
    temperature=0.2,
)

code_llm = ChatOpenAI(
    base_url=LM_STUDIO_BASE_URL,
    api_key="lm-studio",
    model=CODE_LLM_MODEL,
    temperature=0.2,
)
