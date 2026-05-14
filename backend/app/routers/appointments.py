from __future__ import annotations

from fastapi import APIRouter

from app.appointments import store
from app.schemas import AppointmentItem, AppointmentsResponse

router = APIRouter(tags=["appointments"])


@router.get("/appointments", response_model=AppointmentsResponse)
def list_appointments() -> AppointmentsResponse:
    return AppointmentsResponse(appointments=[AppointmentItem(**appointment) for appointment in store.appointments])


@router.get("/api/appointments")
def api_list_appointments() -> list[dict]:
    """API endpoint for UI - returns appointments as a plain list."""
    return store.appointments
