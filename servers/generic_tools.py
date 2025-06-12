import json

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("nuclea-workshop")


@mcp.tool()
def add_numbers(a: float, b:float) -> float:
    """
        Adds two numbers together.
    """
    return a + b


@mcp.tool()
def subtract_numbers(a: float, b:float) -> float:
    """
        Subtract two numbers together.
    """
    return a - b 


@mcp.tool()
def multiply_numbers(a: float, b:float) -> float:
    """
        Mutiply two numbers together.
    """
    return a * b 


@mcp.resource("customers://{customer_id}")
def get_customer_info(customer_id: str) -> str:
    """
        Get detailed information about customers.
    """
    try:
        path_customer = "customers/" + customer_id + ".json"
        with open(path_customer, 'r') as file:
            return  json.load(file)
    except FileNotFoundError:
        return "Customer not found."


@mcp.prompt()
def generate_search_prompt(area: str, num_customers: int) -> str:
    """
        Generate a prompt for a LLM model to find and discuss customer information. 
    """
    PROMPT =\
    f"""
    Search for {num_customers} customers from {area} using the search tool.
    """
    return PROMPT


if __name__ == "__main__":
    mcp.run(transport="stdio")
    