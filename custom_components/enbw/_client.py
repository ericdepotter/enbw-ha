import requests

from .const import ATTR_MANUFACTURER, ATTR_MODEL


class ENBWAPIClient:
    def __init__(self) -> None:
        self.base_url = (
            "https://enbw-emp.azure-api.net/emobility-public-api/api/v1/chargestations/"
        )
        self.api_key = None
        self.id = None

        self.model = None
        self.operator = None

    def login(self, id, api_key):
        self.api_key = (
            api_key if api_key is not None else "d4954e8b2e444fc89a89a463788c0a72"
        )
        self.id = id

        data = self.get_charging_point_info()

        self.model = data.get(ATTR_MODEL)
        self.operator = data.get(ATTR_MANUFACTURER)

        return data

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
