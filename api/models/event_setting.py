"""Modelo para configurações do evento (ex: URL da logo no Supabase Storage)"""
from sqlalchemy import Column, Integer, String
from database.database import Base


class EventSetting(Base):
    __tablename__ = "event_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(String(2000), nullable=True)
