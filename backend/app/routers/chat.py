from __future__ import annotations

import os
import json
import re
from html import unescape

from fastapi import APIRouter

from app.schemas import ChatRequest, ChatResponse
from app.vapi_client import VapiClient

router = APIRouter(tags=["chat"])


def extract_vapi_reply(response: dict) -> str:
    output = response.get("output")
    if isinstance(output, list):
        for item in output:
            if isinstance(item, dict):
                content = item.get("content")
                # If content is a plain string, return it (sanitized from HTML)
                if isinstance(content, str) and content.strip():
                    c = content.strip()
                    if c.lower().lstrip().startswith("<!doctype") or c.lstrip().startswith("<html") or '<' in c:
                        txt = re.sub(r'<[^>]+>', '', c)
                        cleaned = unescape(txt).strip()
                        if re.search(r'[<>]|https?://', cleaned):
                            return "Assistant returned non-textual content. Check server logs."
                        return cleaned
                    return c

                # If content is a dict, try to extract a human-readable field
                if isinstance(content, dict):
                    # common keys that may contain the assistant text
                    for key in ("answer", "text", "content", "message", "reply"):
                        val = content.get(key)
                        if isinstance(val, str) and val.strip():
                            return val

                    # If the dict contains structured sources and an 'answer' is missing,
                    # try to build a readable summary (e.g., list service titles)
                    sources = content.get("sources")
                    if isinstance(sources, list) and sources:
                        titles = [s.get("title") or s.get("name") for s in sources if isinstance(s, dict) and (s.get("title") or s.get("name"))]
                        if titles:
                            return "Found services: " + ", ".join(titles)

                    # Fallback: serialize the dict to a compact readable JSON string
                    try:
                        return json.dumps(content, ensure_ascii=False)
                    except Exception:
                        return str(content)

    message = response.get("message")
    if isinstance(message, str) and message.strip():
        # sanitize HTML if present
        msg = message.strip()
        if msg.lower().lstrip().startswith("<!doctype") or msg.lstrip().startswith("<html") or '<' in msg:
            text = re.sub(r'<[^>]+>', '', msg)
            cleaned = unescape(text).strip()
            if re.search(r'[<>]|https?://', cleaned):
                return "Assistant returned non-textual content. Check server logs."
            return cleaned
        return msg

    reply = response.get("reply")
    if isinstance(reply, str) and reply.strip():
        msg = reply.strip()
        if msg.lower().lstrip().startswith("<!doctype") or msg.lstrip().startswith("<html") or '<' in msg:
            text = re.sub(r'<[^>]+>', '', msg)
            cleaned = unescape(text).strip()
            if re.search(r'[<>]|https?://', cleaned):
                return "Assistant returned non-textual content. Check server logs."
            return cleaned
        return msg

    return str(response)


@router.post("/api/chat", response_model=ChatResponse)
def api_chat(request: ChatRequest) -> ChatResponse:
    """Chat endpoint that integrates with Vapi AI assistant."""
    try:
        vapi_key = os.getenv("VAPI_PRIVATE_KEY")
        if not vapi_key:
            return ChatResponse(reply="", error="VAPI_PRIVATE_KEY not configured")

        client = VapiClient(vapi_key)
        if getattr(request, "conversationId", None):
            response = client.create_message(request.conversationId, request.message)
        else:
            response = client.chat(request.message)

        if "error" in response:
            return ChatResponse(reply="", error=response.get("error", "Unknown error"))

        reply = extract_vapi_reply(response)
        return ChatResponse(reply=reply)
    except Exception as e:
        return ChatResponse(reply="", error=str(e))


@router.get("/api/config")
def api_config() -> dict:
    """Return frontend config needed for Web SDK (public key, assistant id)."""
    public_key = os.getenv("VAPI_PUBLIC_KEY")
    assistant_id = os.getenv("VAPI_ASSISTANT_ID")
    return {"publicKey": public_key or "", "assistantId": assistant_id or ""}


@router.post("/api/session")
def api_session_create() -> dict:
    """Create a conversation session via Vapi and return conversation id."""
    try:
        vapi_key = os.getenv("VAPI_PRIVATE_KEY")
        if not vapi_key:
            return {"error": "VAPI_PRIVATE_KEY not configured"}

        client = VapiClient(vapi_key)
        assistant_id = os.getenv("VAPI_ASSISTANT_ID")
        resp = client.create_conversation(assistant_id)
        conv_id = resp.get("id") or resp.get("conversationId") or resp.get("conversation_id")
        if not conv_id:
            return {"error": "unable to create conversation", "detail": resp}
        return {"conversationId": conv_id}
    except Exception as e:
        return {"error": str(e)}
