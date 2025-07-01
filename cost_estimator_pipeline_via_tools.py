"""
title: Tool Pipeline
author: open-webui
date: 2025-07-01
version: 1.1
license: MIT
description: A tool pipeline for searching internal users based on a query string.
requirements: requests, msal, pydantic, open-webui
"""

import requests
from pydantic import Field
import requests
from open_webui.models.users import Users
from msal import ConfidentialClientApplication
from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint


class Pipeline(FunctionCallingBlueprint):
    class Valves(FunctionCallingBlueprint.Valves):
        CLIENT_ID: str = Field(default="", description="client ID for service account")
        CLIENT_SECRET: str = Field(default="", description="client secret for service account")
        TENANT_ID: str = Field(default="", description="tenant ID for service account")

    _ENDPOINT = "https://labassist.pnnl.gov/proxy/actman/elasticsearch/hub-suggestions-people/_search"

    class Tools:
        def __init__(self, pipeline) -> None:
            self.pipeline = pipeline

        def _get_access_token(self) -> str:
            """
            Retrieve an access token from Azure AD using Client Credentials flow.
            This method uses the CLIENT_ID, CLIENT_SECRET, and TENANT_ID from the pipeline's valves.
            :return: Access token as a string.
            """
            SCOPE = ["https://labassist.pnnl.gov/proxy/.default"]
            TOKEN_URL = f"https://login.microsoftonline.com/{self.pipeline.valves.TENANT_ID}/"
            app = ConfidentialClientApplication(client_id=self.pipeline.valves.CLIENT_ID, client_credential=self.pipeline.valves.CLIENT_SECRET, authority=TOKEN_URL)
            response = app.acquire_token_for_client(scopes=SCOPE)
            if 'error' in response:
                raise Exception(f"Error acquiring token: {response['error_description']}")
            return response['access_token']
            
        def search_internal_users(self, query: str) -> dict:
            """
            Search for internal users based on a query string.
            This method sends a request to the internal API endpoint to search for users.
            An example query could be "skills:C#".
            
            :param query: The search query string.
            :return: A dictionary containing the search results or an error message.
            """
            token = self._get_access_token()
            headers = {"Authorization": f"Bearer {token}"}
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

    def __init__(self):
        super().__init__()
        self.name = "My Hub Search Tool Pipeline"
        self.valves = self.Valves(
            **{
                **self.valves.model_dump(),
                "pipelines": ["*"],  # Connect to all pipelines
            },
        )
        self.tools = self.Tools(self)