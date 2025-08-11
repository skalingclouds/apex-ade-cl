from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json
from typing import List

from app.core.database import get_db
from app.models.saved_schema import SavedSchema
from app.schemas.extraction import FieldInfo, SavedSchemaCreate, SavedSchemaResponse

router = APIRouter()


@router.post("/", response_model=SavedSchemaResponse, status_code=status.HTTP_201_CREATED)
def create_schema(payload: SavedSchemaCreate, db: Session = Depends(get_db)):
    existing = db.query(SavedSchema).filter(SavedSchema.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Schema name already exists")

    record = SavedSchema(
        name=payload.name,
        description=payload.description,
        fields_json=json.dumps([f.dict() for f in payload.fields]),
        created_by="system",
        is_active=True,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return SavedSchemaResponse(
        id=record.id,
        name=record.name,
        description=record.description,
        fields=[FieldInfo(**f) for f in json.loads(record.fields_json)],
        is_active=record.is_active,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.get("/", response_model=List[SavedSchemaResponse])
def list_schemas(db: Session = Depends(get_db)):
    rows = db.query(SavedSchema).filter(SavedSchema.is_active == True).order_by(SavedSchema.created_at.desc()).all()
    out: List[SavedSchemaResponse] = []
    for r in rows:
        out.append(SavedSchemaResponse(
            id=r.id,
            name=r.name,
            description=r.description,
            fields=[FieldInfo(**f) for f in json.loads(r.fields_json)],
            is_active=r.is_active,
            created_at=r.created_at,
            updated_at=r.updated_at,
        ))
    return out


@router.get("/{schema_id}", response_model=SavedSchemaResponse)
def get_schema(schema_id: int, db: Session = Depends(get_db)):
    r = db.query(SavedSchema).filter(SavedSchema.id == schema_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Schema not found")
    return SavedSchemaResponse(
        id=r.id,
        name=r.name,
        description=r.description,
        fields=[FieldInfo(**f) for f in json.loads(r.fields_json)],
        is_active=r.is_active,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


