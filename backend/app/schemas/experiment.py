from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class ExperimentCreate(BaseModel):
    paper_id: str
    data_file_ids: List[str]
    user_instructions: str = ''

class ExperimentResponse(BaseModel):
    id: str
    paper_id: str
    data_file_ids: str
    user_instructions: Optional[str] = None
    status: str
    generated_code: Optional[str] = None
    execution_output: Optional[str] = None
    execution_error: Optional[str] = None
    result_files: Optional[str] = None
    iteration_count: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class ExperimentStatus(BaseModel):
    id: str
    status: str
    iteration_count: int
    message: str
