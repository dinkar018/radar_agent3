from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, func, Text
from app.core.database import Base

class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(String, primary_key=True)
    paper_id = Column(String, nullable=False)
    data_file_ids = Column(Text, nullable=False)
    user_instructions = Column(Text, nullable=True)
    status = Column(String, nullable=False)
    generated_code = Column(Text, nullable=True)
    execution_output = Column(Text, nullable=True)
    execution_error = Column(Text, nullable=True)
    result_files = Column(Text, nullable=True)
    iteration_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)
