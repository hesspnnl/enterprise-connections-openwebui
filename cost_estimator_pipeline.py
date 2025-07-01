from pydantic import BaseModel, Field
import requests
from elastic_auth import get_access_token
from open_webui.utils.chat import generate_chat_completion
from open_webui.models.users import Users



class Pipeline:
    class Valves(BaseModel):
        MODEL_ID: str = Field(default="", description="ID of the model (optional)")
        OPENAI_API_KEY: str = Field(default="", description="API key for OpenAI")

    _ENDPOINT = "https://labassist.pnnl.gov/proxy/actman/elasticsearch/hub-suggestions-people/_search"

    def __init__(self):
        self.valves = self.Valves()

    def pipe(self, body: dict):
        user_query = body.get('query', "").strip()
        if not user_query:
            return {"error": "No query provided."}

        return self.search_internal_users(user_query)

    def search_internal_users(self, query: str) -> dict:
        """
        Search for internal users based on a query string.
        This method sends a request to the internal API endpoint to search for users.
        An example query could be "skills:C#".
        :param query: The search query string.
        :return: A dictionary containing the search results or an error message.
        """
        token = get_access_token()
        headers = {}
        if self.valves.API_KEY:
            headers["Authorization"] = f"Bearer {token}"
        params = {"q": query}
        try:
            resp = requests.get(self._ENDPOINT, params=params, headers=headers, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            else:
                return {
                    "error": f"API request failed: Status {resp.status_code}",
                    "details": resp.text
                }
        except Exception as e:
            return {"error": "API call exception", "details": str(e)}
        
        