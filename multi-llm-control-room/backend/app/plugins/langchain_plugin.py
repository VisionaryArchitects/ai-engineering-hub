"""LangChain framework integration plugin"""
from typing import Dict, List, Any
from dataclasses import dataclass
from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import PromptTemplate
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
class LangChainConfig:
    """Configuration for a LangChain workflow"""
    chain_type: str  # "sequential", "map_reduce", "stuff"
    steps: List[Dict[str, Any]]
    input_variables: List[str]
    output_variables: List[str]


class LangChainPlugin:
    """LangChain framework integration"""

    def __init__(self, model_adapters: Dict[str, Any]):
        """
        Args:
            model_adapters: Dict mapping model_id to ModelAdapter instances
        """
        self.model_adapters = model_adapters

    async def execute(self, config: LangChainConfig, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a LangChain workflow"""

        if config.chain_type == "sequential":
            return await self._execute_sequential(config, inputs)
        else:
            raise ValueError(f"Unsupported chain type: {config.chain_type}")

    async def _execute_sequential(self, config: LangChainConfig, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a sequential chain"""

        chains = []

        for step in config.steps:
            model_id = step["model_id"]
            adapter = self.model_adapters.get(model_id)

            if not adapter:
                raise ValueError(f"Model adapter not found: {model_id}")

            # Wrap adapter as LangChain LLM
            llm = ControlRoomLLM(model_adapter=adapter, model_id=model_id)

            # Create prompt template
            prompt = PromptTemplate(
                template=step["prompt_template"],
                input_variables=step.get("input_vars", [])
            )

            # Create chain
            chain = LLMChain(
                llm=llm,
                prompt=prompt,
                output_key=step["output_key"]
            )
            chains.append(chain)

        # Create overall sequential chain
        overall_chain = SequentialChain(
            chains=chains,
            input_variables=config.input_variables,
            output_variables=config.output_variables,
            verbose=True
        )

        # Execute
        result = overall_chain(inputs)

        return {
            "success": True,
            "output": result,
            "steps_completed": len(chains)
        }

    def get_schema(self) -> Dict[str, Any]:
        """Return configuration schema"""
        return {
            "type": "object",
            "properties": {
                "chain_type": {
                    "type": "string",
                    "enum": ["sequential", "map_reduce", "stuff"]
                },
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "model_id": {"type": "string"},
                            "prompt_template": {"type": "string"},
                            "input_vars": {"type": "array", "items": {"type": "string"}},
                            "output_key": {"type": "string"}
                        },
                        "required": ["model_id", "prompt_template", "output_key"]
                    }
                },
                "input_variables": {"type": "array", "items": {"type": "string"}},
                "output_variables": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["chain_type", "steps", "input_variables", "output_variables"]
        }


# Example LangChain configuration
EXAMPLE_LANGCHAIN_CONFIG = {
    "chain_type": "sequential",
    "steps": [
        {
            "model_id": "model_1",
            "prompt_template": "You are a product manager. Create a brief for: {topic}",
            "input_vars": ["topic"],
            "output_key": "brief"
        },
        {
            "model_id": "model_2",
            "prompt_template": "Based on this brief:\n{brief}\n\nWrite technical specifications.",
            "input_vars": ["brief"],
            "output_key": "specs"
        },
        {
            "model_id": "model_3",
            "prompt_template": "Based on these specs:\n{specs}\n\nWrite implementation code.",
            "input_vars": ["specs"],
            "output_key": "code"
        }
    ],
    "input_variables": ["topic"],
    "output_variables": ["brief", "specs", "code"]
}
