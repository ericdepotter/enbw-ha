import requests


class ENBWAPIClient:
    def __init__(self) -> None:
        self.base_url = (
            "https://enbw-emp.azure-api.net/emobility-public-api/api/v1/chargestations/"
        )
        self.api_key = None
        self.id = None

    def login(self, id, api_key="d4954e8b2e444fc89a89a463788c0a72"):
        self.api_key = api_key
        self.id = id

        return self.get_charging_point_info()

    def get_charging_point_info(self):
        return self._get_endpoint(self.id)

    def _get_endpoint(self, endpoint, timeout=30):
        url = f"{self.base_url}{endpoint}"
        headers = {
            "content-type": "application/json",
            "Ocp-Apim-Subscription-Key": self.api_key,
            "User-Agent": "Home Assistant",
            "Origin": "https://www.enbw.com",
            "Referer": "https://www.enbw.com/",
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
