"""WebSocket endpoint for real-time chat"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio

from app.core.session_manager import session_manager

router = APIRouter()

# Track active connections per session
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manage WebSocket connections"""

    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept WebSocket connection"""
        await websocket.accept()

        if session_id not in active_connections:
            active_connections[session_id] = set()

        active_connections[session_id].add(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str):
        """Remove WebSocket connection"""
        if session_id in active_connections:
            active_connections[session_id].discard(websocket)

            if not active_connections[session_id]:
                del active_connections[session_id]

    async def broadcast(self, session_id: str, message: dict):
        """Broadcast message to all connections for a session"""
        if session_id not in active_connections:
            return

        disconnected = []

        for connection in active_connections[session_id]:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn, session_id)


manager = ConnectionManager()


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""

    # Check if session exists
    session = session_manager.get_session(session_id)
    if not session:
        await websocket.close(code=1008, reason="Session not found")
        return

    await manager.connect(websocket, session_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                action = message.get("action")

                if action == "send_message":
                    content = message.get("content")
                    if not content:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Message content required"
                        })
                        continue

                    # Broadcast user message to all clients
                    await manager.broadcast(session_id, {
                        "type": "user_message",
                        "content": content,
                        "timestamp": None  # Will be set by session manager
                    })

                    # Send to models
                    try:
                        responses = await session_manager.send_message(
                            session_id=session_id,
                            message=content,
                            temperature=message.get("temperature", 0.7),
                            max_tokens=message.get("max_tokens")
                        )

                        # Broadcast each model response
                        for response in responses:
                            await manager.broadcast(session_id, {
                                "type": "model_response",
                                "model_id": response.model_id,
                                "content": response.content,
                                "tokens": response.tokens,
                                "cost": response.cost,
                                "latency_ms": response.latency_ms,
                                "timestamp": response.timestamp.isoformat(),
                                "metadata": response.metadata
                            })

                        # Send summary
                        await manager.broadcast(session_id, {
                            "type": "response_complete",
                            "total_tokens": sum(r.tokens or 0 for r in responses),
                            "total_cost": sum(r.cost or 0.0 for r in responses),
                            "session_total_tokens": session.total_tokens,
                            "session_total_cost": session.total_cost
                        })

                    except Exception as e:
                        await manager.broadcast(session_id, {
                            "type": "error",
                            "message": str(e)
                        })

                elif action == "ping":
                    await websocket.send_json({"type": "pong"})

                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown action: {action}"
                    })

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, session_id)
