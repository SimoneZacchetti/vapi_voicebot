from __future__ import annotations

from datetime import date as date_type

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.appointments import store
from app.services_data import search_services


app = FastAPI(title="Municipality Voicebot API", version="0.1.0")


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
