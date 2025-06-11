import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv


load_dotenv()


# Configure LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "nuclea-workshop"  # You can change this project name
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")


async def run():
    model = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    server_params = StdioServerParameters(
        command="uv",
        args=["run", "servers/generic_tools.py"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Convert MCP to into LangChain tools
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)

            print("\nMCP Chatbot started!")
            print("Type or queries or 'quit' to exit.")
            while True:
                query = input("\nQuery: ").strip()

                if query == "exit":
                    break

                agent_response = await agent.ainvoke({"messages": query})

                for m in agent_response["messages"]:
                    m.pretty_print()


if __name__ == "__main__":
    asyncio.run(run())
