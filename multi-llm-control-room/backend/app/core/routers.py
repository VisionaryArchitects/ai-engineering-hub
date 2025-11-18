"""Message routing patterns for multi-LLM orchestration"""
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime

from app.adapters import ModelAdapter, ModelResponse


class MessageRouter(ABC):
    """Base class for message routing strategies"""

    @abstractmethod
    async def route(
        self,
        message: str,
        models: List[ModelAdapter],
        context: List[Dict[str, str]],
        **kwargs
    ) -> List[ModelResponse]:
        """Route message to models and return responses"""
        pass


class BroadcastRouter(MessageRouter):
    """Broadcast message to all models simultaneously"""

    async def route(
        self,
        message: str,
        models: List[ModelAdapter],
        context: List[Dict[str, str]],
        **kwargs
    ) -> List[ModelResponse]:
        """Send to all models in parallel"""

        # Add user message to context
        full_context = context + [{"role": "user", "content": message}]

        # Send to all models concurrently
        tasks = [
            model.send_message(
                messages=full_context,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens"),
                stream=False
            )
            for model in models
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and return valid responses
        valid_responses = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"Model {models[i].model_id} error: {response}")
                # Create error response
                valid_responses.append(ModelResponse(
                    content=f"[Error: {str(response)}]",
                    model_id=models[i].model_id,
                    tokens=0,
                    cost=0.0,
                    latency_ms=0,
                    timestamp=datetime.utcnow(),
                    metadata={"error": True}
                ))
            else:
                valid_responses.append(response)

        return valid_responses


class RoundRobinRouter(MessageRouter):
    """Models take turns responding"""

    def __init__(self):
        self.turn_index = 0

    async def route(
        self,
        message: str,
        models: List[ModelAdapter],
        context: List[Dict[str, str]],
        **kwargs
    ) -> List[ModelResponse]:
        """Send to one model per turn"""

        if not models:
            return []

        # Select model for this turn
        current_model = models[self.turn_index % len(models)]
        self.turn_index += 1

        # Add user message to context
        full_context = context + [{"role": "user", "content": message}]

        # Send to selected model
        try:
            response = await current_model.send_message(
                messages=full_context,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens"),
                stream=False
            )
            return [response]
        except Exception as e:
            print(f"Model {current_model.model_id} error: {e}")
            return [ModelResponse(
                content=f"[Error: {str(e)}]",
                model_id=current_model.model_id,
                tokens=0,
                cost=0.0,
                latency_ms=0,
                timestamp=datetime.utcnow(),
                metadata={"error": True}
            )]


class CoordinatorRouter(MessageRouter):
    """Coordinator model delegates to specialist models"""

    def __init__(self, coordinator_model_id: str):
        self.coordinator_model_id = coordinator_model_id

    async def route(
        self,
        message: str,
        models: List[ModelAdapter],
        context: List[Dict[str, str]],
        **kwargs
    ) -> List[ModelResponse]:
        """Coordinator decides which models to use"""

        # Find coordinator model
        coordinator = None
        specialists = []

        for model in models:
            if model.model_id == self.coordinator_model_id:
                coordinator = model
            else:
                specialists.append(model)

        if not coordinator:
            # Fallback to broadcast if no coordinator found
            return await BroadcastRouter().route(message, models, context, **kwargs)

        # Step 1: Ask coordinator to analyze and decide
        specialist_info = "\n".join([
            f"- {m.model_id}: {m.config.get('role', 'general')}"
            for m in specialists
        ])

        coordinator_prompt = f"""You are coordinating a team of AI specialists.

User message: {message}

Available specialists:
{specialist_info}

Decide which specialists should handle this request. You can select multiple or none.
Respond with a JSON array of model IDs, e.g.: ["model_1", "model_2"] or [] if you'll handle it yourself.
Only respond with the JSON array, nothing else."""

        coordinator_context = context + [{"role": "user", "content": coordinator_prompt}]

        try:
            coordinator_response = await coordinator.send_message(
                messages=coordinator_context,
                temperature=0.3,  # Lower temp for coordination decisions
                max_tokens=100,
                stream=False
            )

            # Parse coordinator decision
            import json
            try:
                selected_ids = json.loads(coordinator_response.content.strip())
                if not isinstance(selected_ids, list):
                    selected_ids = []
            except:
                selected_ids = []

            # Step 2: Get responses from selected specialists
            selected_models = [
                m for m in specialists if m.model_id in selected_ids
            ]

            if not selected_models:
                # Coordinator handles it alone
                full_context = context + [{"role": "user", "content": message}]
                final_response = await coordinator.send_message(
                    messages=full_context,
                    temperature=kwargs.get("temperature", 0.7),
                    max_tokens=kwargs.get("max_tokens"),
                    stream=False
                )
                return [final_response]

            # Get specialist responses
            full_context = context + [{"role": "user", "content": message}]
            tasks = [
                model.send_message(
                    messages=full_context,
                    temperature=kwargs.get("temperature", 0.7),
                    max_tokens=kwargs.get("max_tokens"),
                    stream=False
                )
                for model in selected_models
            ]

            specialist_responses = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter valid responses
            valid_responses = []
            for i, response in enumerate(specialist_responses):
                if not isinstance(response, Exception):
                    valid_responses.append(response)

            return valid_responses

        except Exception as e:
            print(f"Coordinator error: {e}")
            # Fallback to broadcast
            return await BroadcastRouter().route(message, models, context, **kwargs)


class VotingRouter(MessageRouter):
    """Models propose answers and vote on the best one"""

    async def route(
        self,
        message: str,
        models: List[ModelAdapter],
        context: List[Dict[str, str]],
        **kwargs
    ) -> List[ModelResponse]:
        """Two-phase: propose then vote"""

        if len(models) < 2:
            # Need at least 2 models for voting
            return await BroadcastRouter().route(message, models, context, **kwargs)

        # Phase 1: All models propose answers
        full_context = context + [{"role": "user", "content": message}]

        proposal_tasks = [
            model.send_message(
                messages=full_context,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens"),
                stream=False
            )
            for model in models
        ]

        proposals = await asyncio.gather(*proposal_tasks, return_exceptions=True)

        # Filter valid proposals
        valid_proposals = []
        for i, prop in enumerate(proposals):
            if not isinstance(prop, Exception):
                valid_proposals.append((i, prop))

        if len(valid_proposals) < 2:
            return [p[1] for p in valid_proposals]

        # Phase 2: Vote on best proposal
        proposals_text = "\n\n".join([
            f"Proposal {i+1} (from {prop.model_id}):\n{prop.content}"
            for i, prop in valid_proposals
        ])

        vote_prompt = f"""Review these proposals and vote for the best one.

{proposals_text}

Respond with only the number (1, 2, 3, etc.) of the best proposal."""

        vote_tasks = [
            model.send_message(
                messages=[{"role": "user", "content": vote_prompt}],
                temperature=0.3,
                max_tokens=10,
                stream=False
            )
            for model in models
        ]

        votes = await asyncio.gather(*vote_tasks, return_exceptions=True)

        # Tally votes
        vote_counts = {}
        for vote in votes:
            if not isinstance(vote, Exception):
                try:
                    vote_num = int(vote.content.strip())
                    if 1 <= vote_num <= len(valid_proposals):
                        vote_counts[vote_num] = vote_counts.get(vote_num, 0) + 1
                except:
                    pass

        # Find winner
        if vote_counts:
            winner_num = max(vote_counts, key=vote_counts.get)
            winner_proposal = valid_proposals[winner_num - 1][1]

            # Add voting metadata
            winner_proposal.metadata["voting"] = {
                "votes": vote_counts.get(winner_num, 0),
                "total_proposals": len(valid_proposals)
            }

            return [winner_proposal]

        # If voting fails, return all proposals
        return [p[1] for p in valid_proposals]


def get_router(pattern: str, **kwargs) -> MessageRouter:
    """Factory function to get router instance"""
    routers = {
        "broadcast": BroadcastRouter,
        "round_robin": RoundRobinRouter,
        "coordinator": CoordinatorRouter,
        "voting": VotingRouter
    }

    router_class = routers.get(pattern)
    if not router_class:
        raise ValueError(f"Unknown routing pattern: {pattern}")

    # Some routers need parameters
    if pattern == "coordinator":
        coordinator_id = kwargs.get("coordinator_model_id")
        if not coordinator_id:
            raise ValueError("Coordinator pattern requires coordinator_model_id")
        return router_class(coordinator_id)

    return router_class()
