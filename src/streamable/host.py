
"""HOST: AI application that streams agent execution events."""

import asyncio
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from client import load_tools

load_dotenv()

SYSTEM_PROMPT = (
    "You are a helpful weather assistant. "
    "Use the available tools to answer questions instead of guessing. "
    "If a tool returns an error, explain it and suggest valid options."
)


async def main() -> None:
    tools = await load_tools()

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    agent = create_agent(
        model,
        tools,
        system_prompt=SYSTEM_PROMPT,
    )

    question = "What is the weather in Mumbai?"

    print(f"\n[USER] {question}\n")

    async for event in agent.astream_events(
        {"messages": [{"role": "user", "content": question}]},
        version="v2",
    ):
        event_name = event["event"]
        data = event["data"]

        if event_name == "on_tool_start":
            print(
                f"\n[AGENT] Calling tool: {event['name']}",
                flush=True,
            )

        elif event_name == "on_tool_end":
            print(
                f"\n[AGENT] Tool completed: {event['name']}",
                flush=True,
            )

        elif event_name == "on_chat_model_stream":
            chunk = data.get("chunk")
            content = getattr(chunk, "content", "")

            if isinstance(content, str) and content:
                print(content, end="", flush=True)

    print("\n")


if __name__ == "__main__":
    asyncio.run(main())


# uv run src/streamable/host.py