import uuid
import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

# Adjust imports based on the schema and model definitions
from app.models.experiment import Experiment
from app.schemas.experiment import ExperimentCreate

logger = logging.getLogger(__name__)

class ExperimentService:
    def __init__(self, db_session: AsyncSession, settings: Any):
        self.db_session = db_session
        self.settings = settings
        logger.info("Initialized ExperimentService")

    async def create_experiment(self, data: ExperimentCreate, db: AsyncSession) -> Experiment:
        experiment_id = str(uuid.uuid4())
        
        # We assume data is a Pydantic model
        experiment_data = data.model_dump()
        
        experiment = Experiment(
            id=experiment_id,
            **experiment_data
        )
        db.add(experiment)
        await db.commit()
        await db.refresh(experiment)
        logger.info(f"Created experiment {experiment_id}")
        return experiment

    async def get_experiment(self, experiment_id: str, db: AsyncSession) -> Experiment:
        result = await db.execute(select(Experiment).where(Experiment.id == experiment_id))
        experiment = result.scalar_one_or_none()
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
        return experiment

    async def list_experiments(self, db: AsyncSession) -> List[Experiment]:
        result = await db.execute(select(Experiment))
        return list(result.scalars().all())

    async def update_experiment(self, experiment_id: str, updates: Dict[str, Any], db: AsyncSession) -> Experiment:
        experiment = await self.get_experiment(experiment_id, db)
        for key, value in updates.items():
            if hasattr(experiment, key):
                setattr(experiment, key, value)
        await db.commit()
        await db.refresh(experiment)
        logger.info(f"Updated experiment {experiment_id}")
        return experiment

    async def delete_experiment(self, experiment_id: str, db: AsyncSession):
        experiment = await self.get_experiment(experiment_id, db)
        await db.delete(experiment)
        await db.commit()
        logger.info(f"Deleted experiment {experiment_id}")
