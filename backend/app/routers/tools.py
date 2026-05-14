from __future__ import annotations

from fastapi import APIRouter

from app.appointments import store
from app.schemas import (
    CheckAvailabilityRequest,
    CheckAvailabilityResponse,
    CreateAppointmentRequest,
    CreateAppointmentResponse,
    SearchServicesRequest,
    SearchServicesResponse,
    SearchSource,
)
from app.services_data import search_services
from app.services_data import load_services

router = APIRouter(tags=["tools"])


@router.post("/tools/search_services", response_model=SearchServicesResponse)
def tool_search_services(payload: SearchServicesRequest | None = None) -> SearchServicesResponse:
    query = payload.query if payload else ""
    matches = search_services(query)

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


@router.post("/tools/check_availability", response_model=CheckAvailabilityResponse)
def tool_check_availability(payload: CheckAvailabilityRequest) -> CheckAvailabilityResponse:
    available_slots = store.available_slots(payload.office, payload.date.isoformat())
    return CheckAvailabilityResponse(
        office=payload.office,
        date=payload.date.isoformat(),
        available_slots=available_slots,
    )


@router.post("/tools/create_appointment", response_model=CreateAppointmentResponse)
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


@router.get("/api/services")
def api_list_services() -> list[dict]:
    """Return the full hardcoded services JSON for UI consumption."""
    return load_services()
