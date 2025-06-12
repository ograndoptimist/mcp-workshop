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


async def get_resource(
    session: ClientSession,
    resource_uri: str):
    """
        Get specific resource content.
    """
    try:
        result = await session.read_resource(uri=resource_uri)
        if result and result.contents:
            print(f"\nResource: {resource_uri}")
            print("Content:")
            print(result.contents[0].text)
        else:
            print("No content available!")
    except Exception as e:
        print(f"Error: {e}")


async def list_prompts(session: ClientSession) -> None:
    """
        Execute a specific prompt.
    """
    try:
        prompts_response = await session.list_prompts()
        if prompts_response and prompts_response.prompts:
            for prompt in prompts_response.prompts:
                print(f"- {prompt.name}: {prompt.description}")
                if prompt.arguments:
                    print(f"  Arguments:")
                    for arg in prompt.arguments:
                        arg_name = arg.name if hasattr(arg, 'name') else arg.get('name', '')
                        print(f"    - {arg_name}")
    except Exception as e:
        print(f"Error: {e}")


async def execute_prompt(
    session: ClientSession,
    prompt_name: str,
    args: dict) -> str:
    """
        Execute a specific prompt.
    """
    try:
        result = await session.get_prompt(prompt_name, arguments=args)
        if result and result.messages:
            prompt_content = result.messages[0].content

            # Extract text from content (handles different formats)
            if isinstance(prompt_content, str):
                text = prompt_content
            elif hasattr(prompt_content, 'text'):
                text = prompt_content.text
            else:
                # Handle list of content items
                text = " ".join(item.text if hasattr(item, 'text') else str(item) for item in prompt_content)
            
            return text
    except Exception as e:
        print(f"Error: {e}")


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
            print("Use @<customer_id> to search for customers information")
            print("Use /prompts to list available prompts")
            print("Use /prompt <name> <arg1=value1> to execute a prompt")
            while True:
                query = input("\nQuery: ").strip()

                if query == "exit":
                    break

                # Check for @resource syntax first
                if query.startswith('@'):
                    customer_id = query[1:]
                    resource_uri = f"customers://{customer_id}"
                    await get_resource(session, resource_uri)
                    continue

                # Check for /command syntax
                if query.startswith('/'):
                    parts = query.split()
                    command = parts[0].lower()

                    if command == '/prompts':
                        await list_prompts(session)
                        continue
                    elif command == '/prompt':
                        if len(parts) < 2:
                            print("Usage: /prompt <name> <arg1=value1> <arg2=value2>")
                            continue

                        prompt_name = parts[1]
                        args = {}

                        for arg in parts[2:]:
                            if "=" in arg:
                                key, value = arg.split("=", 1)
                                args[key] = value

                        print(f"\nExecuting prompt...'{prompt_name}'...")
                        query = await execute_prompt(session, prompt_name, args)
                    else:
                        print(f"Unknown command: {command}")

                agent_response = await agent.ainvoke({"messages": query})

                for m in agent_response["messages"]:
                    m.pretty_print()


if __name__ == "__main__":
    asyncio.run(run())
