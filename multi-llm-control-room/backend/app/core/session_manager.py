"""Session management for multi-LLM conversations"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from app.adapters import AdapterFactory, ModelAdapter, ModelResponse
from app.core.routers import MessageRouter, get_router
from app.models.schemas import ModelConfig, Message


@dataclass
class ConversationHistory:
    """Manages conversation history"""
    messages: List[Message] = field(default_factory=list)

    def add_user_message(self, content: str) -> Message:
        """Add user message"""
        msg = Message(
            id=str(uuid.uuid4()),
            role="user",
            content=content,
            timestamp=datetime.utcnow()
        )
        self.messages.append(msg)
        return msg

    def add_model_response(self, response: ModelResponse) -> Message:
        """Add model response"""
        msg = Message(
            id=str(uuid.uuid4()),
            role="assistant",
            content=response.content,
            model_id=response.model_id,
            timestamp=response.timestamp,
            tokens=response.tokens,
            cost=response.cost,
            metadata=response.metadata
        )
        self.messages.append(msg)
        return msg

    def get_context(self, max_messages: Optional[int] = None) -> List[Dict[str, str]]:
        """Get context for model (formatted as OpenAI messages)"""
        messages = self.messages if not max_messages else self.messages[-max_messages:]

        context = []
        for msg in messages:
            context.append({
                "role": msg.role,
                "content": msg.content
            })

        return context


@dataclass
class Session:
    """Active multi-LLM session"""
    id: str
    conversation_id: str
    routing_pattern: str
    model_configs: List[ModelConfig]
    coordinator_model_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "active"
    cost_limit: Optional[float] = None

    # Runtime state
    models: List[ModelAdapter] = field(default_factory=list)
    router: Optional[MessageRouter] = None
    history: ConversationHistory = field(default_factory=ConversationHistory)
    total_tokens: int = 0
    total_cost: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "routing_pattern": self.routing_pattern,
            "models": [
                {
                    "id": config.id,
                    "provider": config.provider,
                    "model_name": config.model_name,
                    "role": config.role
                }
                for config in self.model_configs
            ],
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "message_count": len(self.history.messages)
        }


class SessionManager:
    """Manages all active sessions"""

    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    def create_session(
        self,
        routing_pattern: str,
        model_configs: List[ModelConfig],
        coordinator_model_id: Optional[str] = None,
        cost_limit: Optional[float] = None
    ) -> Session:
        """Create a new session"""

        session_id = str(uuid.uuid4())
        conversation_id = str(uuid.uuid4())

        # Initialize model adapters
        models = []
        for config in model_configs:
            try:
                adapter = AdapterFactory.create(
                    model_id=config.id,
                    provider_type=config.provider,
                    config={
                        "model_name": config.model_name,
                        "base_url": config.metadata.get("base_url"),
                        "api_key": config.metadata.get("api_key"),
                        "endpoint": config.metadata.get("endpoint"),
                        "deployment_name": config.metadata.get("deployment_name"),
                        **config.metadata
                    }
                )
                models.append(adapter)
            except Exception as e:
                print(f"Failed to initialize model {config.id}: {e}")
                continue

        if not models:
            raise ValueError("No models could be initialized")

        # Create router
        router = get_router(
            routing_pattern,
            coordinator_model_id=coordinator_model_id
        )

        # Create session
        session = Session(
            id=session_id,
            conversation_id=conversation_id,
            routing_pattern=routing_pattern,
            model_configs=model_configs,
            coordinator_model_id=coordinator_model_id,
            cost_limit=cost_limit,
            models=models,
            router=router
        )

        self.sessions[session_id] = session
        return session

    async def send_message(
        self,
        session_id: str,
        message: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> List[ModelResponse]:
        """Send message to session and get responses"""

        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if session.status != "active":
            raise ValueError(f"Session is not active: {session.status}")

        # Check cost limit
        if session.cost_limit and session.total_cost >= session.cost_limit:
            raise ValueError(f"Session cost limit reached: ${session.total_cost:.2f}")

        # Add user message to history
        session.history.add_user_message(message)

        # Get context
        context = session.history.get_context()

        # Route message to models
        responses = await session.router.route(
            message=message,
            models=session.models,
            context=context,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Update session state
        for response in responses:
            session.history.add_model_response(response)

            if response.tokens:
                session.total_tokens += response.tokens
            if response.cost:
                session.total_cost += response.cost

        return responses

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        return self.sessions.get(session_id)

    def get_all_sessions(self) -> List[Session]:
        """Get all sessions"""
        return list(self.sessions.values())

    def pause_session(self, session_id: str):
        """Pause a session"""
        session = self.sessions.get(session_id)
        if session:
            session.status = "paused"

    def resume_session(self, session_id: str):
        """Resume a paused session"""
        session = self.sessions.get(session_id)
        if session:
            session.status = "active"

    def end_session(self, session_id: str):
        """End a session"""
        session = self.sessions.get(session_id)
        if session:
            session.status = "completed"

    def delete_session(self, session_id: str):
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def export_session(self, session_id: str, format: str = "json") -> Dict:
        """Export session data"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if format == "json":
            return {
                "session": session.to_dict(),
                "messages": [
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
            }

        elif format == "markdown":
            lines = [
                f"# Session {session.id}",
                f"",
                f"**Created**: {session.created_at.isoformat()}",
                f"**Routing Pattern**: {session.routing_pattern}",
                f"**Total Tokens**: {session.total_tokens}",
                f"**Total Cost**: ${session.total_cost:.4f}",
                f"",
                f"## Models",
                ""
            ]

            for config in session.model_configs:
                lines.append(f"- **{config.id}**: {config.provider}/{config.model_name} ({config.role or 'general'})")

            lines.extend(["", "## Conversation", ""])

            for msg in session.history.messages:
                if msg.role == "user":
                    lines.append(f"### 👤 User")
                    lines.append(f"{msg.content}")
                else:
                    model_name = msg.model_id or "assistant"
                    lines.append(f"### 🤖 {model_name}")
                    lines.append(f"{msg.content}")

                    if msg.tokens or msg.cost:
                        meta = []
                        if msg.tokens:
                            meta.append(f"Tokens: {msg.tokens}")
                        if msg.cost:
                            meta.append(f"Cost: ${msg.cost:.4f}")
                        lines.append(f"*{', '.join(meta)}*")

                lines.append("")

            return {"content": "\n".join(lines)}

        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global session manager instance
session_manager = SessionManager()
