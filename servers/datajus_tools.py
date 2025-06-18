import os 
import requests
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from dotenv import load_dotenv


# Carregando variáveis de ambiente do arquivo dotenv
dotenv_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

DATAJUD_API_KEY = os.getenv("DATAJUD_API_KEY")

# Create an MCP server




def consulta_processo_numero(numero_do_processo: str) -> dict:
    """
        Consulta informações de um processo judicial a partir do seu número,
        utilizando a API pública DataJud para o TJSP.

        Args:
            numero_do_processo (str): O número do processo a ser consultado. 
            Converta sempre para o padrão XXXXXXXXXXXXXXXXXXXX. Exemplo: 00000000000004010000

        Returns:
            dict: Um dicionário contendo a resposta da API DataJud em formato JSON.  
            Retorna um dicionário vazio se a requisição falhar ou se o processo não for encontrado.

        Raises:
            requests.exceptions.RequestException: Se ocorrer algum erro durante a requisição HTTP.

        Example:
            >>> consulta_processo_numero("00000000000004010000")
    """
    DATAJUD_API_KEY = os.getenv("DATAJUD_API_KEY")
    
    # DataJud endpoint
    url = "https://api-publica.datajud.cnj.jus.br/api_publica_tjsp/_search"

    # Payload
    payload = json.dumps({
    "query": {
        "match": {
        "numeroProcesso": numero_do_processo
        }
    }
    })

    # Headers
    headers = {
        'Authorization': f'ApiKey {DATAJUD_API_KEY}',
        'Content-Type': 'application/json'
    }

    try:
        # Request
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status() 
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return {}
    
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar a resposta JSON: {e}")

        return {}



def lista_processos_usuario() -> dict: 
    """
        Consulta o número dos processos do usuário.

        Returns:
            dict: Um dicionário contendo o número dos procesos disponíveis para o usuário.
    """
    processos = ["10015732720238260624", "10100814520238260079", "10502191820238260576"]
    return dict(list=processos)



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
    print("Iniciando servidor MCP...")
    # Run MCP Server:
    
    print("Servidor disponível!")
