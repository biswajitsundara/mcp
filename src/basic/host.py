"""
HOST: the AI application. Owns the LLM, runs the chat, uses the MCP client.
We can call this the agent also
"""

import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from client import load_tools

load_dotenv()

OPENAI_MODEL = "gpt-4o-mini"
SYSTEM_PROMPT = (
    "You are a helpful weather assistant. "
    "Use the available tools to answer questions instead of guessing. "
    "If a tool returns an error, explain it to the user and suggest valid options."
)


def build_agent(tools):
    model = ChatOpenAI(model=OPENAI_MODEL, temperature=0)
    return create_agent(model, tools, system_prompt=SYSTEM_PROMPT)


def _text(content) -> str:
    """MCP tool results arrive as a list of blocks; plain model replies are strings."""
    if isinstance(content, list):
        return " ".join(b.get("text", "") for b in content if isinstance(b, dict))
    return str(content)


def print_trace(messages) -> None:
    """Print each step of the agent run: tool calls and tool results."""
    for msg in messages:
        if msg.type == "ai" and msg.tool_calls:
            for call in msg.tool_calls:
                print(f"[tool call]   {call['name']}({call['args']})")
        elif msg.type == "tool":
            print(f"[tool result] {msg.name} -> {_text(msg.content)}")


async def ask(agent, question: str) -> str:
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": question}]}
    )
    print_trace(response["messages"])
    return _text(response["messages"][-1].content)


async def get_tools() -> list:
    try:
        tools = await load_tools()
    except Exception as exc:
        print(f"Could not connect to the MCP server: {exc}")
        print("Is it running? Start it with: uv run python server.py")
        return []

    print("Loaded tools:", ", ".join(t.name for t in tools))
    return tools


def print_results(question, answer):
    print(f"\nQuestion: {question}")
    print(f"Answer: {answer}")


async def main() -> None:
    tools = await get_tools()
    agent = build_agent(tools)

    question = "what is weather of mumbai?"
    answer = await ask(agent, question)
    print_results(question, answer)


if __name__ == "__main__":
    asyncio.run(main())


# Run the code uv run src/basic/host.py