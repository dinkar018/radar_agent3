from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.agent import AgentRunRequest, AgentRunResponse
from app.schemas.experiment import ExperimentCreate
from app.api.routes.experiments import create_experiment

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.post("/run", response_model=AgentRunResponse)
async def run_agent(
    request: AgentRunRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    exp_create = ExperimentCreate(
        paper_id=request.paper_id,
        data_file_ids=request.data_file_ids,
        user_instructions=request.user_instructions
    )
    
    # We can reuse the logic from the experiments router
    experiment = await create_experiment(exp_create, background_tasks, db)
    
    return AgentRunResponse(
        experiment_id=experiment.id,
        status="started"
    )
