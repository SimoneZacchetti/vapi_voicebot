from __future__ import annotations

from datetime import date as date_type

from pydantic import BaseModel, Field


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


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    conversationId: str | None = None


class ChatResponse(BaseModel):
    reply: str
    error: str | None = None
