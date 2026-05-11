from __future__ import annotations

import os
from datetime import date as date_type

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.appointments import store
from app.services_data import search_services
from app.vapi_client import VapiClient

load_dotenv()


app = FastAPI(title="Municipality Voicebot API", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for UI
app.mount("/static", StaticFiles(directory="app/static"), name="static")


class SearchServicesRequest(BaseModel):
    query: str = Field(min_length=1, description="Natural language query")


class SearchSource(BaseModel):
    title: str
    office: str


class SearchServicesResponse(BaseModel):
    answer: str
    sources: list[SearchSource]


class CheckAvailabilityRequest(BaseModel):
    office: str = Field(min_length=1)
    date: date_type


class CheckAvailabilityResponse(BaseModel):
    office: str
    date: str
    available_slots: list[str]


class CreateAppointmentRequest(BaseModel):
    name: str = Field(min_length=1)
    office: str = Field(min_length=1)
    service: str = Field(min_length=1)
    date: date_type
    time: str = Field(pattern=r"^\d{2}:\d{2}$")


class CreateAppointmentResponse(BaseModel):
    confirmed: bool
    appointment_id: str | None = None
    message: str


class AppointmentItem(BaseModel):
    appointment_id: str
    name: str
    office: str
    service: str
    date: str
    time: str


class AppointmentsResponse(BaseModel):
    appointments: list[AppointmentItem]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/tools/search_services", response_model=SearchServicesResponse)
def tool_search_services(payload: SearchServicesRequest) -> SearchServicesResponse:
    matches = search_services(payload.query)

    if not matches:
        return SearchServicesResponse(
            answer="Non ho trovato servizi comunali pertinenti alla tua richiesta.",
            sources=[],
        )

    sources = [SearchSource(title=item["title"], office=item["office"]) for item in matches]
    answer = "Ho trovato questi servizi comunali pertinenti alla tua richiesta: " + ", ".join(
        source.title for source in sources
    )
    return SearchServicesResponse(answer=answer, sources=sources)


@app.post("/tools/check_availability", response_model=CheckAvailabilityResponse)
def tool_check_availability(payload: CheckAvailabilityRequest) -> CheckAvailabilityResponse:
    available_slots = store.available_slots(payload.office, payload.date.isoformat())
    return CheckAvailabilityResponse(
        office=payload.office,
        date=payload.date.isoformat(),
        available_slots=available_slots,
    )


@app.post("/tools/create_appointment", response_model=CreateAppointmentResponse)
def tool_create_appointment(payload: CreateAppointmentRequest) -> CreateAppointmentResponse:
    result = store.create_appointment(
        name=payload.name,
        office=payload.office,
        service=payload.service,
        date=payload.date.isoformat(),
        time=payload.time,
    )

    if not result["confirmed"]:
        return CreateAppointmentResponse(confirmed=False, message=str(result["message"]))

    return CreateAppointmentResponse(
        confirmed=True,
        appointment_id=str(result["appointment_id"]),
        message=str(result["message"]),
    )


@app.get("/appointments", response_model=AppointmentsResponse)
def list_appointments() -> AppointmentsResponse:
    return AppointmentsResponse(appointments=[AppointmentItem(**appointment) for appointment in store.appointments])


@app.get("/api/appointments")
def api_list_appointments() -> list[dict]:
    """API endpoint for UI - returns appointments as a plain list."""
    return store.appointments


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    reply: str
    error: str | None = None


@app.get("/")
def serve_ui() -> FileResponse:
    """Serve the main HTML UI."""
    return FileResponse("app/static/index.html")


@app.post("/api/chat", response_model=ChatResponse)
def api_chat(request: ChatRequest) -> ChatResponse:
    """Chat endpoint that integrates with Vapi AI assistant."""
    try:
        vapi_key = os.getenv("VAPI_KEY")
        if not vapi_key:
            return ChatResponse(reply="", error="VAPI_KEY not configured")

        client = VapiClient(vapi_key)
        response = client.chat(request.message)

        if "error" in response:
            return ChatResponse(reply="", error=response.get("error", "Unknown error"))

        # Extract reply from Vapi response
        reply = response.get("message") or response.get("reply") or str(response)
        return ChatResponse(reply=reply)
    except Exception as e:
        return ChatResponse(reply="", error=str(e))
