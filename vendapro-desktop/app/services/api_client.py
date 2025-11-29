import requests

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def post(self, route, data):
        return requests.post(self.base_url + route, json=data)
