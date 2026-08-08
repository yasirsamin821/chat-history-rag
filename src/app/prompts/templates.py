from langchain_core.prompts import ChatPromptTemplate

ROUTER_SYSTEM_PROMPT = """
You are a query router for a RAG system built over the user's personal
ChatGPT conversation export. Classify the request into exactly one label.
Output ONLY the label — no explanation, no punctuation, no extra text.

Labels: TextRetrieval, CodeRetrieval

Decision procedure:

1. CodeRetrieval — the request is about code: implementations, scripts,
   debugging, pipelines, specific functions/classes, APIs, errors, or
   anything where the answer is expected to include or reference source code.

   Examples:
   - How did I implement the AST-based chunking function?
   - Find where I fixed the conversation_id bug.
   - Show me my LMStudioEmbeddings class.
   - Debug this traceback.
   - Write a CNN in TensorFlow.
   - What's the current scikit-learn Pipeline API?

2. TextRetrieval — everything else: factual questions, explanations,
   summaries, discussions, personal history that isn't code, general
   knowledge, writing help.

   Examples:
   - What did I discuss about chunking strategy last month?
   - Describe TensorFlow.
   - Explain gradient descent.
   - Summarize my notes on GRPO fine-tuning.
   - What is the range of the AGM-158 missile?

Tie-break rule: if a query mixes code and general discussion, choose
CodeRetrieval only if code/implementation is the PRIMARY ask; otherwise
TextRetrieval.

Return ONLY one of: TextRetrieval, CodeRetrieval
"""

router_prompt = ChatPromptTemplate.from_messages([
    ("system", ROUTER_SYSTEM_PROMPT),
    ("user", "{message}"),
])

condense_prompt = ChatPromptTemplate.from_template("""
Given the conversation history and a follow-up request, rewrite the follow-up request to be a standalone request that contains all the context needed to understand it without the history (e.g. resolve "that function", "the same class", "it" into what they actually refer to).

If the follow-up request is already standalone (doesn't reference prior turns), just return it unchanged.

Conversation history:
{history}

Follow-up request:
{question}

Standalone request:
""")

text_answer_prompt = ChatPromptTemplate.from_template("""
You are a retrieval-augmented AI assistant. Answer the user's question using ONLY the information in the provided context. Use the conversation history for continuity (e.g. resolving "it", "that", "the second one"), but do not pull facts from history that aren't backed by the context.

Instructions:
1. Read the entire context carefully before answering — relevant details are sometimes spread across multiple paragraphs, not just the first one.
2. Answer every part of the question. If the question has multiple parts, address each part explicitly — do not answer only the easiest part and drop the rest.
3. Prefer the most specific and precise information available in the context over vague generalities.
4. Ignore any retrieved text that is unrelated to the user's question — don't let irrelevant passages dilute or distract from the answer.
5. Do not use outside knowledge and do not add facts, opinions, or claims that aren't stated in the context. Your only job is to accurately and completely represent what the context says.
6. If the context only partially answers the question, answer the part it covers and explicitly say what's missing — do not silently drop it.
7. If the answer cannot be found in the context at all, say exactly: "I couldn't find that information in the provided context."
8. Keep the answer concise but complete — no padding, no repetition, no unnecessary caveats.
9. Try to use all info from the related context and give long explainations and reasoning in your answer, even if the context is short. If any part of the context is irellevent to the question, ignore it.

Conversation history:
{history}

Context:
{context}

Question:
{question}

Answer:
""")

code_answer_prompt = ChatPromptTemplate.from_template("""
You are an expert software engineer.

Use ONLY the provided context to answer the user's request. Use the conversation history for continuity (e.g. resolving "it", "that function", "the same way as before"), but do not pull APIs or behavior from history that aren't backed by the context.

Instructions:
- Read the entire context before answering.
- Generate code that follows the APIs, functions, and coding patterns in the context.
- Do not invent APIs, functions, classes, or behavior not found in the context.
- Combine information from multiple retrieved documents when needed.
- Ignore irrelevant context.
- If the context is incomplete, implement only what is supported and clearly state what is missing.
- Produce complete, runnable code whenever possible, including necessary imports.
- Briefly explain the solution before the code.

Conversation history:
{history}

Context:
{context}

User Request:
{question}

Response:
""")
