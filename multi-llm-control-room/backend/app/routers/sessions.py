"""Session management API endpoints"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.models.schemas import SessionCreate, Session as SessionSchema, ModelConfigCreate
from app.core.session_manager import session_manager

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("/", response_model=Dict[str, Any])
async def create_session(session_create: SessionCreate):
    """Create a new multi-LLM session"""
    try:
        # Build model configs
        from app.models.schemas import ModelConfig
        import uuid

        model_configs = []
        for i, model_create in enumerate(session_create.config.models):
            model_config = ModelConfig(
                id=f"model_{i+1}",
                provider=model_create.provider,
                model_name=model_create.model_name,
                role=model_create.role,
                system_prompt=model_create.system_prompt,
                temperature=model_create.temperature,
                max_tokens=model_create.max_tokens,
                metadata={}
            )
            model_configs.append(model_config)

        session = session_manager.create_session(
            routing_pattern=session_create.config.routing_pattern,
            model_configs=model_configs,
            coordinator_model_id=session_create.config.coordinator_model_id,
            cost_limit=session_create.config.cost_limit
        )

        return session.to_dict()

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Dict[str, Any]])
async def list_sessions():
    """List all sessions"""
    sessions = session_manager.get_all_sessions()
    return [session.to_dict() for session in sessions]


@router.get("/{session_id}", response_model=Dict[str, Any])
async def get_session(session_id: str):
    """Get session details"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session.to_dict()


@router.post("/{session_id}/messages", response_model=Dict[str, Any])
async def send_message(session_id: str, message: Dict[str, Any]):
    """Send a message to the session"""
    try:
        content = message.get("content")
        if not content:
            raise HTTPException(status_code=400, detail="Message content required")

        responses = await session_manager.send_message(
            session_id=session_id,
            message=content,
            temperature=message.get("temperature", 0.7),
            max_tokens=message.get("max_tokens")
        )

        return {
            "session_id": session_id,
            "responses": [
                {
                    "model_id": resp.model_id,
                    "content": resp.content,
                    "tokens": resp.tokens,
                    "cost": resp.cost,
                    "latency_ms": resp.latency_ms,
                    "timestamp": resp.timestamp.isoformat()
                }
                for resp in responses
            ],
            "total_tokens": sum(r.tokens or 0 for r in responses),
            "total_cost": sum(r.cost or 0.0 for r in responses)
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/pause")
async def pause_session(session_id: str):
    """Pause a session"""
    session_manager.pause_session(session_id)
    return {"status": "paused"}


@router.post("/{session_id}/resume")
async def resume_session(session_id: str):
    """Resume a paused session"""
    session_manager.resume_session(session_id)
    return {"status": "active"}


@router.post("/{session_id}/end")
async def end_session(session_id: str):
    """End a session"""
    session_manager.end_session(session_id)
    return {"status": "completed"}


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    session_manager.delete_session(session_id)
    return {"status": "deleted"}


@router.get("/{session_id}/export/{format}")
async def export_session(session_id: str, format: str):
    """Export session in specified format"""
    try:
        exported = session_manager.export_session(session_id, format)
        return exported
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{session_id}/history", response_model=List[Dict[str, Any]])
async def get_session_history(session_id: str):
    """Get conversation history"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "model_id": msg.model_id,
            "timestamp": msg.timestamp.isoformat(),
            "tokens": msg.tokens,
            "cost": msg.cost
        }
        for msg in session.history.messages
    ]
