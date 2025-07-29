"""
title: Hub Search Tool Pipeline
author: open-webui
date: 2025-07-01
version: 1.1
license: MIT
description: A tool pipeline for searching internal users on based on a query string using the hub elastic search index.
requirements: requests, pydantic, open-webui, azure-identity
"""

import requests
from pydantic import Field, BaseModel
from open_webui.models.users import Users
from azure.identity import ClientSecretCredential


class Tools:
    class Valves(BaseModel):
        CLIENT_ID: str = Field(default="", description="client ID for service account")
        CLIENT_SECRET: str = Field(
            default="", description="client secret for service account"
        )
        TENANT_ID: str = Field(default="", description="tenant ID for service account")

    _ENDPOINT = "https://apimdevgw.pnnl.gov/proof-of-concept-hub-mcp/v1/hub"

    def __init__(self):
        """Initialize the Tool."""
        self.valves = self.Valves()

    async def _get_access_token(self, __event_emitter__=None) -> str:
        """
        Retrieve an access token from Azure AD using Client Credentials flow.
        This method uses the CLIENT_ID, CLIENT_SECRET, and TENANT_ID from the pipeline's valves.
        :return: Access token as a string.
        """
        SCOPE = "api://proof-of-concept.pnnl.gov/hub/.default"
        await __event_emitter__(
            {
                "type": "message",
                "data": {"content": "Inside the _get_access_token method\n"},
            }
        )
        try:
            credential = ClientSecretCredential(
                tenant_id=self.valves.TENANT_ID,
                client_id=self.valves.CLIENT_ID,
                client_secret=self.valves.CLIENT_SECRET,
            )
            token = credential.get_token(SCOPE).token

            await __event_emitter__(
                {
                    "type": "message",
                    "data": {"content": "The token was retrieved successfully.\n"},
                }
            )
        except Exception as e:
            await __event_emitter__(
                {
                    "type": "message",
                    "data": {"content": "The token creation was NOT successful.\n"},
                }
            )
            raise Exception(f"Failed to create ClientSecretCredential: {str(e)}")
        await __event_emitter__(
            {
                "type": "message",
                "data": {"content": "The token creation was successful.\n"},
            }
        )

        return token

    async def search_internal_users(
        self, searchTerm: str, has_availability: bool = True, __event_emitter__=None
    ) -> dict:
        """
        Search for internal users based on a string.
        This method sends a request to the internal API endpoint to search for users.

        :searchTerm: The search term to query.
        :has_availability: Whether to filter by user availability for work. Defualt is True.

        :return: A dictionary containing the search results or an error message.
        """

        token = await self._get_access_token(__event_emitter__)
        await __event_emitter__(
            {
                "type": "message",
                "data": {"content": "The token was retrieved successfully.\n"},
            }
        )
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "requests",  # Example curl User-Agent value
        }
        params = {"searchTerm": searchTerm, "hasAvailability": has_availability}
        await __event_emitter__(
            {
                "type": "message",
                "data": {"content": "The params are " + str(params) + "\n"},
            }
        )
        try:
            resp = requests.post(
                self._ENDPOINT, data=params, headers=headers, timeout=10
            )
            if resp.status_code == 200:
                await __event_emitter__(
                    {
                        "type": "message",
                        "data": {"content": "The endpoint was called successfully.\n"},
                    }
                )
                return resp.json()
            else:
                await __event_emitter__(
                    {
                        "type": "message",
                        "data": {
                            "content": "There was an error calling the endpoint. The error reads: "
                            + resp.text
                        },
                    }
                )
                return {
                    "error": f"API request failed: Status {resp.status_code}",
                    "details": resp.text,
                }
        except Exception as e:
            await __event_emitter__(
                {
                    "type": "message",
                    "data": {
                        "content": "There was an exception calling the endpoint. The error reads: "
                        + str(e)
                        + "\n"
                    },
                }
            )
            return {"error": "API call exception", "details": str(e)}

    async def search_internal_users_by_name(
        self, name: str, __event_emitter__=None
    ) -> dict:
        """
        Search for an internal user based on name.
        This method sends a request to the internal API endpoint to search for users.

        :name: name of the user to search for.

        :return: A dictionary containing the search results or an error message.
        """

        token = await self._get_access_token(__event_emitter__)
        await __event_emitter__(
            {
                "type": "message",
                "data": {"content": "The token was retrieved successfully.\n"},
            }
        )
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "requests",  # Example curl User-Agent value
        }
        params = {"name": name}
        await __event_emitter__(
            {
                "type": "message",
                "data": {"content": "The params are " + str(params) + "\n"},
            }
        )
        try:
            resp = requests.get(
                self._ENDPOINT, params=params, headers=headers, timeout=10
            )
            if resp.status_code == 200:
                await __event_emitter__(
                    {
                        "type": "message",
                        "data": {"content": "The endpoint was called successfully.\n"},
                    }
                )
                return resp.json()
            else:
                await __event_emitter__(
                    {
                        "type": "message",
                        "data": {
                            "content": "There was an error calling the endpoint. The error reads: "
                            + resp.text
                        },
                    }
                )
                return {
                    "error": f"API request failed: Status {resp.status_code}",
                    "details": resp.text,
                }
        except Exception as e:
            await __event_emitter__(
                {
                    "type": "message",
                    "data": {
                        "content": "There was an exception calling the endpoint. The error reads: "
                        + str(e)
                        + "\n"
                    },
                }
            )
            return {"error": "API call exception", "details": str(e)}
