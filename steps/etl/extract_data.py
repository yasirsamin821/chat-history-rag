import json
import re
from datetime import datetime, timezone

from zenml import step
from configs.config import DATASET
from steps.etl.load_data import load
from src.domain.documents import CodeDocument, TextDocument



text_model = TextDocument
code_model = CodeDocument


FENCE_RE = re.compile(r"```[\s\S]*?```")

SYNTAX_PATTERNS = [
    re.compile(r"\bdef\s+\w+\s*\("),
    re.compile(r"^\s*(import|from)\s+\w+", re.M),
    re.compile(r"\bclass\s+\w+[(:]"),
    re.compile(r"\bfunction\s+\w+\s*\("),
    re.compile(r"=>\s*{"),
    re.compile(r"console\.(log|error|warn)\("),
    re.compile(r"\b(const|let|var)\s+\w+\s*="),
    re.compile(r"\bSELECT\b.+\bFROM\b", re.I),
    re.compile(r"\bINSERT INTO\b", re.I),
    re.compile(r"<(\w+)(?:\s[^>]*)?>.*?</\1>", re.S),
    re.compile(r"[{};]\s*$", re.M),
    re.compile(r"^\s*[$#]\s+\S+", re.M),
    re.compile(r"\b(pip|pip3|npm|yarn|conda)\s+install\b"),
    re.compile(r"\bgit\s+(clone|commit|push|pull|checkout)\b"),
    re.compile(r"#include\s*<\w+"),
    re.compile(r"\bpublic\s+(static\s+)?(void|class)\b"),
    re.compile(r"""require\(['"]"""),
    re.compile(r"`[^`\n]{2,60}`"),
    re.compile(r"(?:^(?: {4}|\t)\S.*\n){3,}", re.M),
]

FENCE_WEIGHT = 5
SYNTAX_WEIGHT = 1
SCORE_THRESHOLD = 3


def score_text(text: str) -> int:
    score = 0

    fence_hits = FENCE_RE.findall(text)

    if fence_hits:
        score += FENCE_WEIGHT * min(len(fence_hits), 3)

    for pattern in SYNTAX_PATTERNS:
        if pattern.search(text):
            score += SYNTAX_WEIGHT

    return score



def load_raw_conversations(path):
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()

    marker = "var jsonData = "
    idx = data.find(marker)

    if idx == -1:
        raise ValueError("Could not find jsonData in file")

    start = idx + len(marker)

    decoder = json.JSONDecoder()
    obj, _end = decoder.raw_decode(data, start)

    return obj



def extract_text(message):
    content = message.get("content") or {}
    content_type = content.get("content_type")

    if content_type == "text":
        parts = content.get("parts") or []

        text = "\n".join(
            part
            for part in parts
            if isinstance(part, str) and part.strip()
        )

        return text if text.strip() else None

    if content_type == "multimodal_text":
        parts = content.get("parts") or []
        chunks = []

        for part in parts:

            if isinstance(part, str):
                if part.strip():
                    chunks.append(part)

            elif isinstance(part, dict):
                if part.get("content_type") == "image_asset_pointer":
                    chunks.append("[image attachment]")

        text = "\n".join(chunks)

        return text if text.strip() else None

    # Skip thoughts, reasoning, code execution,
    # and other internal message types.
    return None


# 

def build_conversation(conv):
    mapping = conv.get("mapping", {})
    current_node = conv.get("current_node")

    chain = []

    node_id = current_node
    visited = set()

    while (
        node_id
        and node_id in mapping
        and node_id not in visited
    ):
        visited.add(node_id)

        node = mapping[node_id]
        chain.append(node)

        node_id = node.get("parent")

    chain.reverse()

    messages = []

    for node in chain:
        message = node.get("message")

        if not message:
            continue

        role = (message.get("author") or {}).get("role")

        if role not in ("user", "assistant"):
            continue

        text = extract_text(message)

        if not text:
            continue

        messages.append({
            "role": role,
            "content": text,
            "create_time": message.get("create_time"),
        })

    def iso(timestamp):
        if not timestamp:
            return None

        return datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc
        ).isoformat()

    return {
        "conversation_id": (
            conv.get("conversation_id")
            or conv.get("id")
        ),
        "title": conv.get("title") or "(untitled)",
        "create_time": iso(conv.get("create_time")),
        "update_time": iso(conv.get("update_time")),
        "num_messages": len(messages),
        "messages": messages,
    }



def iter_messages(conversation):
    for message in conversation.get("messages", []):
        content = message.get("content")

        if isinstance(content, str):
            yield content

        elif isinstance(content, dict):
            text = content.get("text") or content.get("parts")

            if isinstance(text, list):
                yield "\n".join(
                    part
                    for part in text
                    if isinstance(part, str)
                )

            elif isinstance(text, str):
                yield text



def has_code(conversation):
    full_text = "\n".join(
        iter_messages(conversation)
    )

    return score_text(full_text) >= SCORE_THRESHOLD


@step
def process_chat_export(path):
    raw = load_raw_conversations(path)

    print(f"Loaded {len(raw)} raw conversations")

    conversations = []
    empty = 0

    for conversation in raw:
        built = build_conversation(conversation)

        if built["num_messages"] == 0:
            empty += 1
            continue

        conversations.append(built)

    print(
        f"Built {len(conversations)} conversations "
        f"with content ({empty} empty/skipped)"
    )

    text_data = []
    code_data = []

    for conversation in conversations:
        if has_code(conversation):
            code_data.append(conversation)
        else:
            text_data.append(conversation)
    
    load(text_model, text_data)
    load(code_model, code_data)
    print(
        f"Total: {len(conversations)} | "
        f"text_data: {len(text_data)} | "
        f"code_data: {len(code_data)}"
    )
    



    
