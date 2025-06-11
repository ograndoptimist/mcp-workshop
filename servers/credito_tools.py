from mcp.server.fastmcp import FastMCP


mcp = FastMCP("nuclea-workshop-credito")


@mcp.tool()
def consulta_score_empresa(cnpj: int) -> float:
    """
        Função que consulta o score de crédito de uma empresa a partir do seu CNPJ.
    """
    empresas = {
        "avenue code": 780,
        "nuclea": 800
    }
    return empresas[cnpj]