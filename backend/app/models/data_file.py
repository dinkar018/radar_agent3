from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, func, Text
from app.core.database import Base

class DataFile(Base):
    __tablename__ = "data_files"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    upload_date = Column(DateTime, server_default=func.now(), nullable=False)
