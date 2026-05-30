"""The Claude-driven research agent.

A thin wrapper over the Claude Agent SDK that wires in BOSC's in-process tools,
applies project defaults from :mod:`bosc.config`, and exposes a simple
``await agent.run(prompt) -> str`` surface plus a streaming variant.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    query,
)

from bosc.agent import tools
from bosc.config import Settings, get_settings
from bosc.logging import get_logger

log = get_logger(__name__)


@dataclass
class AgentResult:
    """The outcome of one research turn: the answer plus run metadata."""

    text: str
    tools_used: list[str] = field(default_factory=list)
    num_turns: int = 0
    cost_usd: float | None = None
    is_error: bool = False


DEFAULT_SYSTEM_PROMPT = """\
You are the Project BOSC research agent. You investigate public-records source
material about the privately funded BOSC roadwork program and its engineering
cost estimates. Be precise and cite source pages/files. When numbers are
involved, prefer the deterministic BOSC tools (reconcile_summary, read_extraction)
over estimating in your head. Distinguish high-confidence figures from
approximate (~) transcriptions. Never fabricate line items or sources.
"""


class ResearchAgent:
    """Reusable handle to a configured Claude research agent."""

    def __init__(
        self,
        *,
        model: str | None = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        max_turns: int | None = None,
        settings: Settings | None = None,
        enable_tools: bool = True,
    ) -> None:
        self.settings = settings or get_settings()
        self.model = model or self.settings.model
        self.system_prompt = system_prompt
        self.max_turns = max_turns or self.settings.max_turns
        self.enable_tools = enable_tools

    def _options(self) -> ClaudeAgentOptions:
        kwargs: dict[str, object] = {
            "model": self.model,
            "system_prompt": self.system_prompt,
            "max_turns": self.max_turns,
            # Headless: the BOSC tools are read-only, so auto-run them without prompts.
            "permission_mode": "bypassPermissions",
        }
        if self.enable_tools:
            kwargs["mcp_servers"] = {tools.SERVER_NAME: tools.build_server()}
            kwargs["allowed_tools"] = tools.ALLOWED_TOOL_NAMES
        return ClaudeAgentOptions(**kwargs)  # type: ignore[arg-type]

    async def converse(
        self, prompt: str, *, on_text: Callable[[str], None] | None = None
    ) -> AgentResult:
        """Run one turn, optionally streaming text via ``on_text``; return the result.

        Captures the final answer (the SDK ``ResultMessage`` if present, else the
        concatenated assistant text), which tools the agent invoked, and run cost.
        """
        log.info("agent.run", model=self.model, tools=self.enable_tools)
        parts: list[str] = []
        result = AgentResult(text="")
        async for message in query(prompt=prompt, options=self._options()):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        parts.append(block.text)
                        if on_text is not None:
                            on_text(block.text)
                    elif isinstance(block, ToolUseBlock):
                        result.tools_used.append(block.name)
            elif isinstance(message, ResultMessage):
                result.num_turns = message.num_turns
                result.cost_usd = message.total_cost_usd
                result.is_error = message.is_error
                if message.result:
                    result.text = message.result
        if not result.text:
            result.text = "\n".join(parts).strip()
        log.info(
            "agent.done",
            tools=len(result.tools_used),
            turns=result.num_turns,
            cost_usd=result.cost_usd,
        )
        return result

    async def stream(self, prompt: str) -> AsyncIterator[str]:
        """Yield assistant text blocks as they arrive."""
        async for message in query(prompt=prompt, options=self._options()):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        yield block.text

    async def run(self, prompt: str) -> str:
        """Run a single research turn and return the final answer text."""
        return (await self.converse(prompt)).text
