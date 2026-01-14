"""Operações CRUD para participantes"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from models.participant import Participant as ParticipantModel
from models.participant import ParticipantCreate, ParticipantUpdate


def get_participants(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> List[ParticipantModel]:
    """Lista participantes com paginação e busca"""
    query = db.query(ParticipantModel)
    
    if search:
        search_filter = f"%{search.lower()}%"
        query = query.filter(
            or_(
                ParticipantModel.name.ilike(search_filter),
                ParticipantModel.common_name.ilike(search_filter),
                ParticipantModel.email.ilike(search_filter),
                ParticipantModel.phone.ilike(search_filter),
                ParticipantModel.instagram.ilike(search_filter),
                ParticipantModel.address.ilike(search_filter),
                ParticipantModel.neighborhood.ilike(search_filter),
            )
        )
    
    return query.order_by(ParticipantModel.name).offset(skip).limit(limit).all()


def get_participant(db: Session, participant_id: int) -> Optional[ParticipantModel]:
    """Obtém um participante por ID"""
    return db.query(ParticipantModel).filter(ParticipantModel.id == participant_id).first()


def create_participant(db: Session, participant: ParticipantCreate) -> ParticipantModel:
    """Cria um novo participante"""
    data = participant.model_dump()
    print(f"🔍 Debug - Criando participante com dados:")
    print(f"   birth_date: {repr(data.get('birth_date'))}")
    print(f"   email: {repr(data.get('email'))}")
    print(f"   phone: {repr(data.get('phone'))}")
    print(f"   father_contact: {repr(data.get('father_contact'))}")
    print(f"   mother_contact: {repr(data.get('mother_contact'))}")
    
    db_participant = ParticipantModel(**data)
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    
    print(f"🔍 Debug - Participante criado no banco:")
    print(f"   birth_date: {repr(db_participant.birth_date)}")
    print(f"   email: {repr(db_participant.email)}")
    print(f"   phone: {repr(db_participant.phone)}")
    
    return db_participant


def update_participant(
    db: Session,
    participant_id: int,
    participant: ParticipantUpdate
) -> Optional[ParticipantModel]:
    """Atualiza um participante"""
    db_participant = get_participant(db, participant_id)
    if not db_participant:
        return None
    
    update_data = participant.model_dump(exclude_unset=True)
    print(f"🔍 Debug - Atualizando participante {participant_id} com dados:")
    print(f"   Campos recebidos: {list(update_data.keys())}")
    print(f"   birth_date: {repr(update_data.get('birth_date'))}")
    print(f"   email: {repr(update_data.get('email'))}")
    print(f"   phone: {repr(update_data.get('phone'))}")
    print(f"   father_contact: {repr(update_data.get('father_contact'))}")
    print(f"   mother_contact: {repr(update_data.get('mother_contact'))}")
    
    for field, value in update_data.items():
        print(f"   Atualizando {field}: {repr(getattr(db_participant, field, None))} -> {repr(value)}")
        setattr(db_participant, field, value)
    
    db.commit()
    db.refresh(db_participant)
    
    print(f"🔍 Debug - Participante atualizado no banco:")
    print(f"   birth_date: {repr(db_participant.birth_date)}")
    print(f"   email: {repr(db_participant.email)}")
    print(f"   phone: {repr(db_participant.phone)}")
    
    return db_participant


def delete_participant(db: Session, participant_id: int) -> bool:
    """Exclui um participante"""
    db_participant = get_participant(db, participant_id)
    if not db_participant:
        return False
    
    db.delete(db_participant)
    db.commit()
    return True
