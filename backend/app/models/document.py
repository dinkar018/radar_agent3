from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, func, Text
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    doc_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    parsed_content = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)
    file_size = Column(Integer, nullable=False)
    upload_date = Column(DateTime, server_default=func.now(), nullable=False)
    collection_name = Column(String, nullable=False)
