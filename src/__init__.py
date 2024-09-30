# 导入模块
from .api_client import ClashAPIClient
from .proxy_manager import ProxyManager
from .status_monitor import StatusMonitor
from .log_listener import LogListener

# 包级别的常量
PACKAGE_VERSION = "1.0.0"
PACKAGE_AUTHOR = "Your Name"

# 初始化函数
def initialize_package():
    print("Package initialized successfully.")
