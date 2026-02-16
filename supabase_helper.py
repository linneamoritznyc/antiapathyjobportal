"""
Simple Supabase helper using requests library
No supabase-py client needed!
"""
import requests
import json


class SupabaseClient:
    def __init__(self, url: str, key: str):
        self.url = url.rstrip('/')
        self.key = key
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    def select(self, table: str, columns: str = "*", filters: dict = None, limit: int = None):
        """
        Query data from a table

        Example:
            client.select("jobs", columns="id,title,company", filters={"status": "open"}, limit=10)
        """
        url = f"{self.url}/rest/v1/{table}"
        params = {"select": columns}

        if filters:
            for key, value in filters.items():
                params[key] = f"eq.{value}"

        if limit:
            params["limit"] = limit

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def insert(self, table: str, data: dict):
        """Insert data into a table"""
        url = f"{self.url}/rest/v1/{table}"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def update(self, table: str, data: dict, filters: dict):
        """Update data in a table"""
        url = f"{self.url}/rest/v1/{table}"
        params = {}
        for key, value in filters.items():
            params[key] = f"eq.{value}"

        response = requests.patch(url, headers=self.headers, params=params, json=data)
        response.raise_for_status()
        return response.json()

    def delete(self, table: str, filters: dict):
        """Delete data from a table"""
        url = f"{self.url}/rest/v1/{table}"
        params = {}
        for key, value in filters.items():
            params[key] = f"eq.{value}"

        response = requests.delete(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_tables(self):
        """List all tables in the database"""
        url = f"{self.url}/rest/v1/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        # This returns OpenAPI spec, let's parse table names
        spec = response.json()
        tables = list(spec.get("definitions", {}).keys())
        return tables


# Usage example:
if __name__ == "__main__":
    import os

    # Initialize client
    client = SupabaseClient(
        url=os.getenv("SUPABASE_URL"),
        key=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    )

    # Query example
    jobs = client.select("jobs", limit=5)
    print(f"Found {len(jobs)} jobs")
    for job in jobs:
        print(f"- {job.get('title')} at {job.get('company')}")
