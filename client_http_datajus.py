import os
import asyncio
from dotenv import load_dotenv

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

from langgraph.prebuilt import create_react_agent


# Carregando variáveis de ambiente do arquivo dotenv
load_dotenv()

# Gemini API Key (Get from Google AI Studio: https://aistudio.google.com/app/apikey)
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGSMITH_PROJECT"] = "nuclea-workshop-jusdata-mcp-agent"


async def get_resource(
    session: MultiServerMCPClient,
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


async def list_prompts(session: MultiServerMCPClient) -> None:
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


async def main():
    sse_parameters = {
        "DataJud MCP": {
            "url": "http://127.0.0.1:9000/mcp",
            "transport": "streamable_http"
        }
    }

    client = MultiServerMCPClient(sse_parameters)
    async with client.session("DataJud MCP") as session:
        # Convert MCP to into LangChain tools
        tools = await load_mcp_tools(session)
        
        PROMPT =\
        """
        Você é um assistente especialista em consulta de processos do Tribunal de Justiça de São Paulo (TJSP).
                
        Utilize as tools para consultar informações referentes à processos,
        baseado nos identificadores que o usuário tiver à disposição
        (cada tool utiliza identificadores diferentes).

        Adote uma linguagem simples (para leigos) e 
        descontraída (inclusive utilizando emojis em algumas interações).
        Ao comunicar informações referentes à data e hora, 
        utilize um formato simplificado, como DD/MM/YYYY HH:MM.
        """
        agent = create_react_agent(
            model="claude-3-7-sonnet-latest",
            tools=tools,
            prompt=PROMPT
        )

        print("\nMCP Chatbot started!")
        print("Type or queries or 'quit' to exit.")
        print("Use @<customer_id> to search for customers information")
        print("Use /prompts to list available prompts")
        print("Use /prompt <name> <arg1=value1> to execute a prompt")
        while True:
            try:
                user_input = await asyncio.to_thread(input, "💬: ") # Use asyncio.to_thread for blocking input
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break

                # Check for @resource syntax first
                if user_input.startswith('@'):
                    customer_id = user_input[1:]
                    resource_uri = f"customers://{customer_id}"
                    await get_resource(session, resource_uri)
                    continue

                # Check for /command syntax
                if user_input.startswith('/'):
                    parts = user_input.split()
                    command = parts[0].lower()

                    if command == '/prompts':
                        await list_prompts(session)
                        continue

                async for event in agent.astream({"messages": [{"role": "user", "content": user_input}]}):
                    for key, value in event.items():
                        if key == "agent": # Or whatever the key for the agent's response is
                            if isinstance(value, dict) and "messages" in value:
                                last_message = value["messages"][-1]
                                if last_message.content: # Ensure content is not empty
                                    print("🤖:", last_message.content, "\n")
                        elif key == "tool":
                            print(f"🛠️ Tool Invoked: {value}")
                print("-" * 30) # Separator after full response
            except Exception as e:
                print(f"An error occurred: {e}")
                break # Exit after fallback attempt
        
        return agent


if __name__ == "__main__":
    asyncio.run(main())
