import tkinter as tk
import logging
import queue
from src.api_client import ClashAPIClient
from src.ui import ClashUI

def main():
    logging.basicConfig(filename='clash_gui.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("程序启动")

    root = tk.Tk()
    log_queue = queue.Queue()  # 创建日志队列

    # Clash API 客户端实例化
    proxy_manager = ClashAPIClient()

    # 创建 UI
    ui = ClashUI(root, proxy_manager, log_queue)

    def process_log_queue():
        """处理日志队列并更新 UI"""
        while not log_queue.empty():
            item_type, item_value = log_queue.get()
            if item_type == "proxies":
                # 更新代理列表
                ui.proxy_list['values'] = item_value
            elif item_type == "message":
                # 显示普通消息
                logging.info(item_value)
                ui.log_text.config(state=tk.NORMAL)
                ui.log_text.insert(tk.END, f"{item_value}\n")
                ui.log_text.config(state=tk.DISABLED)
                ui.log_text.see(tk.END)  # 滚动到最后
            elif item_type == "mode":
                # 更新代理模式显示
                ui.mode_label.config(text=f"当前模式: {item_value}")

        root.after(100, process_log_queue)

    # 启动日志队列处理
    root.after(100, process_log_queue)

    root.mainloop()

if __name__ == "__main__":
    main()
