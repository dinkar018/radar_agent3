import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json

from app.core.database import get_db, async_sessionmaker_factory
from app.core.config import settings
from app.models.experiment import Experiment
from app.models.document import Document
from app.models.data_file import DataFile
from app.schemas.experiment import ExperimentCreate, ExperimentResponse
from app.api.websocket import manager

from app.services.vector_store import VectorStoreService
from app.services.rag_service import RAGService

router = APIRouter(prefix="/experiments", tags=["Experiments"])

async def run_experiment_pipeline(experiment_id: str):
    await manager.broadcast(experiment_id, {"status": "running", "message": "Starting experiment pipeline..."})
    
    async with async_sessionmaker_factory() as db:
        result = await db.execute(select(Experiment).where(Experiment.id == experiment_id))
        experiment = result.scalar_one_or_none()
        if not experiment:
            return
            
        try:
            # 1. Get paper document and data files from DB
            await manager.broadcast(experiment_id, {"status": "running", "message": "Fetching paper and data files..."})
            paper_res = await db.execute(select(Document).where(Document.id == experiment.paper_id))
            paper_doc = paper_res.scalar_one_or_none()
            
            data_file_ids = json.loads(experiment.data_file_ids)
            data_files = []
            for d_id in data_file_ids:
                d_res = await db.execute(select(DataFile).where(DataFile.id == d_id))
                df = d_res.scalar_one_or_none()
                if df:
                    data_files.append(df)
            
            # Initialize RAG
            vector_store = VectorStoreService(persist_dir=settings.CHROMA_PERSIST_DIR)
            rag_service = RAGService(vector_store=vector_store)
            
            # 2. Retrieve paper context
            await manager.broadcast(experiment_id, {"status": "running", "message": "Retrieving paper context..."})
            paper_context = rag_service.retrieve(
                query="methodology algorithm signal processing implementation",
                collection_name="papers",
                doc_id=experiment.paper_id
            )
            
            # 3. Retrieve radar context from KB
            await manager.broadcast(experiment_id, {"status": "running", "message": "Retrieving radar context from KB..."})
            radar_context = rag_service.retrieve(
                query="radar specifications hardware setup configuration",
                collection_name="knowledge_base"
            )
            
            # 4. Build initial AgentState and run agent
            from app.agent.graph import build_agent_graph
            from app.agent.tools import format_data_description
            import asyncio
            
            data_file_paths = [df.file_path for df in data_files]
            data_description = format_data_description(data_file_paths)
            
            agent_state = {
                "paper_id": experiment.paper_id,
                "paper_context": paper_context,
                "radar_context": radar_context,
                "data_file_paths": data_file_paths,
                "data_description": data_description,
                "user_instructions": experiment.user_instructions or "",
                "messages": [],
                "generated_code": "",
                "execution_output": "",
                "execution_error": "",
                "result_files": [],
                "iteration_count": 0,
                "max_iterations": 3,
                "status": "pending",
                "status_message": "",
                "is_complete": False,
            }
            
            # 5. Run the LangGraph agent graph
            await manager.broadcast(experiment_id, {"status": "running", "message": "Running agent graph..."})
            graph = build_agent_graph()
            
            # Run graph in thread pool since LangGraph nodes are sync
            final_state = await asyncio.to_thread(graph.invoke, agent_state)
            
            # 6. Update experiment record with results
            experiment.status = "completed" if final_state.get("status") == "complete" else "failed"
            experiment.completed_at = datetime.utcnow()
            experiment.generated_code = final_state.get("generated_code", "")
            experiment.execution_output = final_state.get("execution_output", "")
            experiment.execution_error = final_state.get("execution_error", "")
            experiment.result_files = json.dumps(final_state.get("result_files", []))
            experiment.iteration_count = final_state.get("iteration_count", 0)
            
            db.add(experiment)
            await db.commit()
            
            # 7. Broadcast status updates
            await manager.broadcast(experiment_id, {"status": "completed", "message": "Experiment finished."})
            
        except Exception as e:
            experiment.status = "failed"
            experiment.execution_error = str(e)
            db.add(experiment)
            await db.commit()
            await manager.broadcast(experiment_id, {"status": "failed", "message": f"Error: {str(e)}"})

@router.post("/", response_model=ExperimentResponse)
async def create_experiment(
    data: ExperimentCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    experiment_id = str(uuid.uuid4())
    
    experiment = Experiment(
        id=experiment_id,
        paper_id=data.paper_id,
        data_file_ids=json.dumps(data.data_file_ids),
        user_instructions=data.user_instructions,
        status="pending",
        iteration_count=0
    )
    
    db.add(experiment)
    await db.commit()
    await db.refresh(experiment)
    
    background_tasks.add_task(run_experiment_pipeline, experiment_id)
    
    return experiment

@router.get("/", response_model=list[ExperimentResponse])
async def list_experiments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Experiment))
    experiments = result.scalars().all()
    return list(experiments)

@router.get("/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(experiment_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Experiment).where(Experiment.id == experiment_id))
    experiment = result.scalar_one_or_none()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment

@router.post("/{experiment_id}/rerun", response_model=ExperimentResponse)
async def rerun_experiment(
    experiment_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Experiment).where(Experiment.id == experiment_id))
    experiment = result.scalar_one_or_none()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
        
    experiment.status = "pending"
    experiment.generated_code = None
    experiment.execution_output = None
    experiment.execution_error = None
    experiment.result_files = None
    experiment.completed_at = None
    experiment.iteration_count += 1
    
    db.add(experiment)
    await db.commit()
    await db.refresh(experiment)
    
    background_tasks.add_task(run_experiment_pipeline, experiment_id)
    
    return experiment

@router.delete("/{experiment_id}")
async def delete_experiment(experiment_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Experiment).where(Experiment.id == experiment_id))
    experiment = result.scalar_one_or_none()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
        
    await db.delete(experiment)
    await db.commit()
    return {"message": "Experiment deleted"}
