"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""

from mcp.server.fastmcp import FastMCP
from azure.identity import ClientSecretCredential
import requests

# Create an MCP server
mcp = FastMCP("Demo")

def _get_access_token(TENANT_ID, CLIENT_ID, CLIENT_SECRET) -> str:
        """
        Retrieve an access token from Azure AD using Client Credentials flow.
        This method uses the CLIENT_ID, CLIENT_SECRET, and TENANT_ID from the pipeline's valves.
        :return: Access token as a string.
        """
        SCOPE = "https://labassist.pnnl.gov/proxy/.default"

       
        try:
            credential = ClientSecretCredential(tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
            token = credential.get_token(SCOPE).token
        except Exception as e:
           
            raise Exception(f"Failed to create ClientSecretCredential: {str(e)}")
        return token


# Add a search user tool
@mcp.tool()
def search_user(query_string, TENANT_ID, CLIENT_ID, CLIENT_SECRET) -> dict:
    """Search for a user by query string. Use ElasticSearch query syntax.
    Some things you can search for:
    - skills
    - name
    - email
    - location
    - title
    - department
    - description
    Example query: "skills:Nuclear Reactors"
    """
    token = _get_access_token(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query_string}
    resp = requests.get("https://labassist.pnnl.gov/proxy/actman/elasticsearch/hub-suggestions-people/_search", params=params, headers=headers, timeout=10)
    if resp.status_code == 200:
        return resp.json()
    else:
        return {"error": f"Failed to search for user: {resp.status_code} - {resp.text}"}