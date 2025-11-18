"""CrewAI framework integration plugin"""
from typing import Dict, List, Any
from dataclasses import dataclass
from crewai import Agent, Task, Crew, Process
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from typing import Optional


class ControlRoomLLM(LLM):
    """Wrapper to use Control Room model adapters as LangChain LLMs"""

    model_adapter: Any
    model_id: str

    @property
    def _llm_type(self) -> str:
        return "control_room"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the model adapter"""
        import asyncio

        # Convert prompt to messages format
        messages = [{"role": "user", "content": prompt}]

        # Run async method in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            response = loop.run_until_complete(
                self.model_adapter.send_message(
                    messages=messages,
                    temperature=kwargs.get("temperature", 0.7),
                    max_tokens=kwargs.get("max_tokens"),
                    stream=False
                )
            )
            return response.content
        finally:
            loop.close()


@dataclass
class CrewAIConfig:
    """Configuration for a CrewAI workflow"""
    agents: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    process: str = "sequential"  # or "hierarchical"
    verbose: bool = True


class CrewAIPlugin:
    """CrewAI framework integration"""

    def __init__(self, model_adapters: Dict[str, Any]):
        """
        Args:
            model_adapters: Dict mapping model_id to ModelAdapter instances
        """
        self.model_adapters = model_adapters

    async def execute(self, config: CrewAIConfig, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a CrewAI workflow"""

        # Build agents
        agents = []
        for agent_config in config.agents:
            model_id = agent_config["model_id"]
            adapter = self.model_adapters.get(model_id)

            if not adapter:
                raise ValueError(f"Model adapter not found: {model_id}")

            # Wrap adapter as LangChain LLM
            llm = ControlRoomLLM(model_adapter=adapter, model_id=model_id)

            # Create agent
            agent = Agent(
                role=agent_config["role"],
                goal=agent_config["goal"],
                backstory=agent_config.get("backstory", ""),
                verbose=config.verbose,
                llm=llm,
                allow_delegation=agent_config.get("allow_delegation", False)
            )
            agents.append(agent)

        # Build tasks
        tasks = []
        for task_config in config.tasks:
            agent_index = task_config["agent_index"]

            if agent_index >= len(agents):
                raise ValueError(f"Agent index out of range: {agent_index}")

            task = Task(
                description=task_config["description"],
                agent=agents[agent_index],
                expected_output=task_config.get("expected_output", "Task completed")
            )
            tasks.append(task)

        # Determine process type
        process_type = Process.sequential
        if config.process == "hierarchical":
            process_type = Process.hierarchical

        # Create and execute crew
        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=process_type,
            verbose=config.verbose
        )

        # Execute
        result = crew.kickoff(inputs=inputs)

        return {
            "success": True,
            "output": str(result),
            "tasks_completed": len(tasks),
            "agents_used": len(agents)
        }

    def get_schema(self) -> Dict[str, Any]:
        """Return configuration schema"""
        return {
            "type": "object",
            "properties": {
                "agents": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "model_id": {"type": "string"},
                            "role": {"type": "string"},
                            "goal": {"type": "string"},
                            "backstory": {"type": "string"},
                            "allow_delegation": {"type": "boolean"}
                        },
                        "required": ["model_id", "role", "goal"]
                    }
                },
                "tasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "agent_index": {"type": "integer"},
                            "expected_output": {"type": "string"}
                        },
                        "required": ["description", "agent_index"]
                    }
                },
                "process": {
                    "type": "string",
                    "enum": ["sequential", "hierarchical"]
                }
            },
            "required": ["agents", "tasks"]
        }


# Example CrewAI configuration for YouTube content creation
EXAMPLE_CREWAI_CONFIG = {
    "agents": [
        {
            "model_id": "model_1",
            "role": "Content Researcher",
            "goal": "Research trending topics and gather comprehensive information",
            "backstory": "Expert researcher with deep knowledge of current tech trends",
            "allow_delegation": False
        },
        {
            "model_id": "model_2",
            "role": "Script Writer",
            "goal": "Write engaging YouTube scripts based on research",
            "backstory": "Professional content writer specialized in technical topics",
            "allow_delegation": False
        },
        {
            "model_id": "model_3",
            "role": "Code Reviewer",
            "goal": "Review and optimize code examples in the script",
            "backstory": "Senior developer focused on code quality and best practices",
            "allow_delegation": False
        }
    ],
    "tasks": [
        {
            "description": "Research the topic: {topic}",
            "agent_index": 0,
            "expected_output": "Comprehensive research summary with key points"
        },
        {
            "description": "Write a YouTube script based on the research",
            "agent_index": 1,
            "expected_output": "Complete script with intro, body, and conclusion"
        },
        {
            "description": "Review all code examples in the script for accuracy",
            "agent_index": 2,
            "expected_output": "Reviewed script with optimized code examples"
        }
    ],
    "process": "sequential",
    "verbose": True
}
