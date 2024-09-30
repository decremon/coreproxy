import requests
import logging

class ClashAPIClient:
    def __init__(self, base_url="http://127.0.0.1:9090", secret=""):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {secret}"
        }

    def get_proxies(self):
        """获取 Clash 代理列表"""
        url = f"{self.base_url}/proxies"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # 检查请求是否成功
            return response.json()
        except requests.RequestException as e:
            logging.error(f"获取 Clash 代理列表时出错: {str(e)}")
            return None

    def get_configs(self):
        """获取 Clash 的配置信息"""
        url = f"{self.base_url}/configs"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # 检查请求是否成功
            return response.json()
        except requests.RequestException as e:
            logging.error(f"获取 Clash 配置时出错: {str(e)}")
            return None

    def set_mode(self, mode):
        """设置代理模式"""
        url = f"{self.base_url}/configs"
        data = {"mode": mode}
        try:
            response = requests.patch(url, json=data, headers=self.headers)
            response.raise_for_status()  # 检查请求是否成功
            return True
        except requests.RequestException as e:
            logging.error(f"设置 Clash 模式时出错: {str(e)}")
            return False

    def test_latency(self, proxy_name):
        """测试指定代理节点的延迟"""
        url = f"{self.base_url}/proxies/{proxy_name}/delay"
        params = {
            "timeout": 5000,  # 设置延迟测试超时（单位：毫秒）
            "url": "http://www.gstatic.com/generate_204"  # 使用一个常见的 URL 来进行延迟测试
        }
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()  # 检查请求是否成功
            latency = response.json().get('delay', -1)
            return latency if latency != -1 else "测试失败"
        except requests.RequestException as e:
            logging.error(f"测试代理延迟时出错: {str(e)}")
            return "测试失败"
    
    def switch_proxy(self, group_name, proxy_name):
        url = f"{self.base_url}/proxies/{group_name}"
        data = {"name": proxy_name}
        try:
            response = requests.put(url, json=data, headers=self.headers)
            response.raise_for_status()  # 检查请求是否成功
            return True
        except requests.RequestException as e:
            logging.error(f"切换代理时出错: {str(e)}")
            return False
