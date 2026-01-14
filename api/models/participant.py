"""Modelos Pydantic e SQLAlchemy para participantes"""
from sqlalchemy import Column, Integer, String, Boolean, Text
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import date
from database.database import Base


# SQLAlchemy Model
class Participant(Base):
    __tablename__ = "participants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    common_name = Column(String, nullable=True)
    birth_date = Column(String, nullable=True)  # ISO format YYYY-MM-DD
    instagram = Column(String, nullable=True)
    address = Column(String, nullable=True)
    neighborhood = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    sacraments = Column(Text, nullable=True)  # JSON string
    church_movement = Column(String, nullable=True)
    church_movement_info = Column(Text, nullable=True)
    father_name = Column(String, nullable=True)
    father_contact = Column(String, nullable=True)
    mother_name = Column(String, nullable=True)
    mother_contact = Column(String, nullable=True)
    ecc_participant = Column(Boolean, nullable=True, default=False)
    ecc_info = Column(Text, nullable=True)
    has_restrictions = Column(Boolean, nullable=True, default=False)
    restrictions_info = Column(Text, nullable=True)
    observations = Column(Text, nullable=True)
    photo_path = Column(String, nullable=True)


# Pydantic Models
class ParticipantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    common_name: Optional[str] = Field(default=None, max_length=200)
    birth_date: Optional[str] = Field(default=None)
    instagram: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=500)
    neighborhood: Optional[str] = Field(default=None, max_length=200)
    email: Optional[str] = Field(default=None, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=20)
    sacraments: Optional[str] = Field(default=None)
    church_movement: Optional[str] = Field(default=None, max_length=200)
    church_movement_info: Optional[str] = Field(default=None, max_length=500)
    father_name: Optional[str] = Field(default=None, max_length=200)
    father_contact: Optional[str] = Field(default=None, max_length=20)
    mother_name: Optional[str] = Field(default=None, max_length=200)
    mother_contact: Optional[str] = Field(default=None, max_length=20)
    ecc_participant: Optional[bool] = Field(default=False)
    ecc_info: Optional[str] = Field(default=None, max_length=500)
    has_restrictions: Optional[bool] = Field(default=False)
    restrictions_info: Optional[str] = Field(default=None, max_length=500)
    observations: Optional[str] = Field(default=None)
    photo_path: Optional[str] = Field(default=None)
    
    class Config:
        # Permite strings vazias serem convertidas para None
        str_strip_whitespace = True
    
    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v):
        if v:
            try:
                from datetime import datetime
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Data deve estar no formato YYYY-MM-DD")
        return v
    
    @model_validator(mode='before')
    @classmethod
    def convert_empty_strings(cls, data):
        """Converte strings vazias em None para campos opcionais"""
        if isinstance(data, dict):
            optional_string_fields = [
                'common_name', 'instagram', 'address', 'neighborhood', 
                'phone', 'sacraments', 'church_movement', 'church_movement_info',
                'father_name', 'father_contact', 'mother_name', 'mother_contact',
                'ecc_info', 'restrictions_info', 'observations', 'photo_path'
            ]
            for field in optional_string_fields:
                if field in data and (data[field] == '' or (isinstance(data[field], str) and data[field].strip() == '')):
                    data[field] = None
            # Tratamento especial para email
            if 'email' in data:
                if data['email'] == '' or (isinstance(data['email'], str) and data['email'].strip() == ''):
                    data['email'] = None
                elif data['email'] is not None:
                    import re
                    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
                    if not re.match(email_pattern, data['email']):
                        raise ValueError("Email inválido")
        return data


class ParticipantCreate(ParticipantBase):
    class Config:
        # Permite strings vazias serem convertidas para None
        str_strip_whitespace = True


class ParticipantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    common_name: Optional[str] = Field(None, max_length=200)
    birth_date: Optional[str] = None
    instagram: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=500)
    neighborhood: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    sacraments: Optional[str] = None
    church_movement: Optional[str] = Field(default=None, max_length=200)
    church_movement_info: Optional[str] = Field(default=None, max_length=500)
    father_name: Optional[str] = Field(None, max_length=200)
    father_contact: Optional[str] = Field(None, max_length=20)
    mother_name: Optional[str] = Field(None, max_length=200)
    mother_contact: Optional[str] = Field(None, max_length=20)
    ecc_participant: Optional[bool] = None
    ecc_info: Optional[str] = Field(None, max_length=500)
    has_restrictions: Optional[bool] = None
    restrictions_info: Optional[str] = Field(None, max_length=500)
    observations: Optional[str] = None
    photo_path: Optional[str] = None


class ParticipantResponse(ParticipantBase):
    id: int
    
    class Config:
        from_attributes = True
