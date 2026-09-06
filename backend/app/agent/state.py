import operator
from typing import Annotated, TypedDict

class AgentState(TypedDict):
    # Input
    paper_id: str
    paper_context: str          # RAG-retrieved paper chunks
    radar_context: str          # RAG-retrieved KB chunks  
    data_file_paths: list[str]
    data_description: str
    user_instructions: str
    
    # Agent working memory
    messages: Annotated[list, operator.add]
    generated_code: str
    execution_output: str
    execution_error: str
    result_files: list[str]
    
    # Control
    iteration_count: int
    max_iterations: int
    status: str
    status_message: str
    is_complete: bool
