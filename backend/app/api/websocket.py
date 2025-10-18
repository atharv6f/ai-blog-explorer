from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
import json
import asyncio
from typing import List, Dict, Any

router = APIRouter()

# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat functionality
    """
    await manager.connect(websocket)

    # Send welcome message
    await websocket.send_json({
        "type": "system",
        "message": "Connected to AI Blog Chat",
        "timestamp": datetime.utcnow().isoformat()
    })

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                message = {"type": "message", "content": data}

            # Echo the message back (placeholder for AI processing)
            response = {
                "type": "response",
                "content": f"Hello! You said: {message.get('content', data)}",
                "timestamp": datetime.utcnow().isoformat()
            }

            # Simulate AI processing delay
            await asyncio.sleep(0.5)

            # Send response
            await websocket.send_json(response)

            # Broadcast to all clients (optional)
            if message.get("broadcast"):
                await manager.broadcast(json.dumps({
                    "type": "broadcast",
                    "content": message.get("content"),
                    "timestamp": datetime.utcnow().isoformat()
                }))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(json.dumps({
            "type": "system",
            "message": "A user disconnected",
            "timestamp": datetime.utcnow().isoformat()
        }))

@router.websocket("/ws/test")
async def websocket_test(websocket: WebSocket):
    """
    Simple WebSocket test endpoint
    """
    await websocket.accept()

    try:
        # Send initial message
        await websocket.send_text("WebSocket connection established!")

        # Echo loop
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Test echo: {data}")

    except WebSocketDisconnect:
        print("Test WebSocket disconnected")

@router.get("/ws/status")
async def websocket_status():
    """
    Get WebSocket connection status
    """
    return {
        "active_connections": len(manager.active_connections),
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }