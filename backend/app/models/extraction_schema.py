from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class ExtractionSchema(Base):
    __tablename__ = "extraction_schemas"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    schema_json = Column(Text, nullable=False)  # JSON string of Pydantic schema
    selected_fields = Column(Text, nullable=False)  # JSON array of selected field names
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", backref="extraction_schemas")