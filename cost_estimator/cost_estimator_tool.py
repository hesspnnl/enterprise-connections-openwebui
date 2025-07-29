"""
title: Cost Tool
author: open-webui
date: 2025-07-01
version: 1.1
license: MIT
description: A tool pipeline for searching internal project costs on based on fiscal year, hanford id, and project number.
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

    _ENDPOINT = "https://apimdevgw.pnnl.gov/proof-of-concept-costs-mcp/v1/costs"

    def __init__(self):
        """Initialize the Tool."""
        self.valves = self.Valves()

    async def _get_access_token(self, __event_emitter__=None) -> str:
        """
        Retrieve an access token from Azure AD using Client Credentials flow.
        This method uses the CLIENT_ID, CLIENT_SECRET, and TENANT_ID from the pipeline's valves.
        :return: Access token as a string.
        """
        SCOPE = "api://proof-of-concept.pnnl.gov/cost-estimator/.default"

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

    async def search_costs(
        self,
        fiscalYear: str,
        hanfordID: int,
        projectNumber: int,
        __event_emitter__=None,
    ) -> dict:
        """
        Search for costs based on the fiscal year, hanford ID, and project number.
        This method sends a request to the internal API endpoint to search for costs.

        :fiscalYear: The fiscal year to query.
        :hanfordID: the hanford ID to query. This should be in the format of a seven digit number and can be sourced from a users hub profile response.
        :projectNumber: the project number to query.

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
        params = {
            "fiscalYear": fiscalYear,
            "resourceID": str(hanfordID),
            "projectNumber": str(projectNumber),
        }
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
