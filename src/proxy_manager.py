from src.api_client import ClashAPIClient
import logging
import requests

class ProxyManager:
    def __init__(self):
        self.client = ClashAPIClient()

    def list_proxies(self):
        try:
            proxies = self.client.get_proxies()
            return proxies
        except Exception as e:
            logging.error(f"无法列出代理: {str(e)}")
            return None

    def switch_proxy(self, proxy_name, selected_proxy):
        url = f"{self.client.base_url}/proxies/{proxy_name}"
        data = {"name": selected_proxy}
        try:
            response = self.client.session.put(url, json=data, headers=self.client.headers)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logging.error(f"切换代理时出错: {str(e)}")
            return False
