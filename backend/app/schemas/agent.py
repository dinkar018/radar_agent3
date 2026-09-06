from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class AgentRunRequest(BaseModel):
    paper_id: str
    data_file_ids: List[str]
    user_instructions: str = ''

class AgentRunResponse(BaseModel):
    experiment_id: str
    status: str

class WebSocketMessage(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
