import os

import httpx
from dotenv import load_dotenv

load_dotenv()


class VapiClient:
    """Client to interact with Vapi AI assistant using HTTP API."""

    def __init__(self, vapi_key: str | None = None):
        self.vapi_key = vapi_key or os.getenv("VAPI_KEY") or os.getenv("VAPI_PRIVATE_KEY")
        self.base_url = "https://api.vapi.ai"
        self.headers = {"Authorization": f"Bearer {self.vapi_key}"}

    def chat(self, message: str, assistant_id: str | None = None) -> dict:
        """Send a message to Vapi assistant and get response."""
        assistant_id = assistant_id or os.getenv("VAPI_ASSISTANT_ID", "default")

        payload = {
            "input": message,
            "assistantId": assistant_id,
        }

        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/chat",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": e.response.text,
                "message": "Failed to contact Vapi API",
                "status_code": e.response.status_code,
            }
        except httpx.HTTPError as e:
            return {"error": str(e), "message": "Failed to contact Vapi API"}
        except Exception as e:
            return {"error": str(e), "message": "Unexpected error"}

    def create_message(self, conversation_id: str, content: str) -> dict:
        """Send a message in an existing conversation."""
        payload = {"content": content}

        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/conversations/{conversation_id}/messages",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"error": str(e)}

    def create_conversation(self, assistant_id: str | None = None) -> dict:
        """Create a new conversation for an assistant."""
        payload = {}
        if assistant_id:
            payload["assistantId"] = assistant_id

        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/conversations",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"error": str(e)}
