from dataclasses import dataclass
from typing import Optional


@dataclass
class Participant:
    id: Optional[int]
    name: str
    common_name: Optional[str] = None
    birth_date: Optional[str] = None  # ISO YYYY-MM-DD
    instagram: Optional[str] = None
    address: Optional[str] = None
    neighborhood: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    sacraments: Optional[str] = None
    church_movement: Optional[str] = None
    father_name: Optional[str] = None
    father_contact: Optional[str] = None
    mother_name: Optional[str] = None
    mother_contact: Optional[str] = None
    ecc_participant: Optional[bool] = None
    ecc_info: Optional[str] = None
    has_restrictions: Optional[bool] = None
    restrictions_info: Optional[str] = None
    observations: Optional[str] = None
    photo_path: Optional[str] = None

