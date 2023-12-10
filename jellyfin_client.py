import requests
import os

# Client based on the Seedr API V1 client documented here:
# https://www.seedr.cc/docs/api/rest/v1
class JellyfinClient():
    def __init__(self, host_url: str, api_key: str):
        self.host_url = host_url
        self.api_key = api_key
    
    def refresh_catalog(self) -> any:
        url = f'{self.host_url}/Library/Refresh'
        headers = {
            'Content-Type': 'application/json',
            'X-Emby-Token': self.api_key
        }

        response = requests.post(url, headers=headers)
        if response.status_code != 204:
            raise response
