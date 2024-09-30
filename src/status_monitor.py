from src.api_client import ClashAPIClient
import logging

class StatusMonitor:
    def __init__(self):
        self.client = ClashAPIClient()

    def get_status(self):
        try:
            config = self.client.get_configs()
            if config:
                return config
            else:
                logging.error("未能获取 Clash 配置")
                return {"mode": "未知"}
        except Exception as e:
            logging.error(f"获取 Clash 配置时出错: {str(e)}")
            return {"mode": "未知"}  # 返回一个默认值以避免 NoneType 错误
