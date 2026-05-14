from __future__ import annotations

import os

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
                if isinstance(content, str) and content.strip():
                    return content

    message = response.get("message")
    if isinstance(message, str) and message.strip():
        return message

    reply = response.get("reply")
    if isinstance(reply, str) and reply.strip():
        return reply

    return str(response)


@router.post("/api/chat", response_model=ChatResponse)
def api_chat(request: ChatRequest) -> ChatResponse:
    """Chat endpoint that integrates with Vapi AI assistant."""
    try:
        vapi_key = os.getenv("VAPI_KEY") or os.getenv("VAPI_PRIVATE_KEY") #TODO tenere solo una, verificare se deve essere pubblica o privata
        if not vapi_key:
            return ChatResponse(reply="", error="VAPI_KEY not configured")

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
        vapi_key = os.getenv("VAPI_KEY") or os.getenv("VAPI_PRIVATE_KEY")
        if not vapi_key:
            return {"error": "VAPI_KEY not configured"}

        client = VapiClient(vapi_key)
        assistant_id = os.getenv("VAPI_ASSISTANT_ID")
        resp = client.create_conversation(assistant_id)
        conv_id = resp.get("id") or resp.get("conversationId") or resp.get("conversation_id")
        if not conv_id:
            return {"error": "unable to create conversation", "detail": resp}
        return {"conversationId": conv_id}
    except Exception as e:
        return {"error": str(e)}
