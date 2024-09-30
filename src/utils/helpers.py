import logging
import os

def setup_logging(log_file="logs/clash_control.log"):
    # 获取项目根目录路径
    base_dir = os.path.dirname(os.path.dirname(__file__))  # 获取 main.py 的上一级目录
    log_file_path = os.path.join(base_dir, log_file)  # 生成完整的日志文件路径

    # 获取日志目录路径并创建目录
    log_dir = os.path.dirname(log_file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)  # 如果目录不存在，创建该目录

    # 配置日志记录
    logging.basicConfig(
        filename=log_file_path,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("Logging setup complete.")
