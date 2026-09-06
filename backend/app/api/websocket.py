from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, experiment_id: str):
        await websocket.accept()
        if experiment_id not in self.active_connections:
            self.active_connections[experiment_id] = []
        self.active_connections[experiment_id].append(websocket)
        
    def disconnect(self, websocket: WebSocket, experiment_id: str):
        if experiment_id in self.active_connections:
            if websocket in self.active_connections[experiment_id]:
                self.active_connections[experiment_id].remove(websocket)
            if not self.active_connections[experiment_id]:
                del self.active_connections[experiment_id]
                
    async def broadcast(self, experiment_id: str, message: dict):
        if experiment_id in self.active_connections:
            for connection in self.active_connections[experiment_id]:
                await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/experiments/{experiment_id}")
async def experiment_ws(websocket: WebSocket, experiment_id: str):
    await manager.connect(websocket, experiment_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, experiment_id)
