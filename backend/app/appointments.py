from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field


DEFAULT_SLOTS = ["09:30", "10:30", "11:30"]


@dataclass
class AppointmentStore:
    appointments: list[dict[str, str]] = field(default_factory=list)
    next_id: int = 1

    def available_slots(self, office: str, date: str, occupied: Iterable[str] | None = None) -> list[str]:
        occupied_slots = set(occupied or [])
        for appointment in self.appointments:
            if appointment["office"].lower() == office.lower() and appointment["date"] == date:
                occupied_slots.add(appointment["time"])
        return [slot for slot in DEFAULT_SLOTS if slot not in occupied_slots]

    def create_appointment(
        self,
        *,
        name: str,
        office: str,
        service: str,
        date: str,
        time: str,
    ) -> dict[str, str | bool]:
        if time not in self.available_slots(office, date):
            return {"confirmed": False, "message": "Lo slot richiesto non e' piu' disponibile."}

        appointment_id = f"APT-{self.next_id:03d}"
        self.next_id += 1

        appointment = {
            "appointment_id": appointment_id,
            "name": name,
            "office": office,
            "service": service,
            "date": date,
            "time": time,
        }
        self.appointments.append(appointment)

        return {
            "confirmed": True,
            "appointment_id": appointment_id,
            "message": (
                f"Appuntamento confermato per {name} il {date[8:10]}/{date[5:7]}/{date[0:4]} "
                f"alle {time} presso {office}."
            ),
        }


store = AppointmentStore()
