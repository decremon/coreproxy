import logging
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from src.control_buttons import ClashController
from src.rounded_button import RoundedButton  # 导入 RoundedButton 类

class ClashUI:
    def __init__(self, root, proxy_manager, log_queue):
        self.root = root
        self.proxy_manager = proxy_manager
        self.log_queue = log_queue
        self.proxy_list = None  # 代理列表下拉框
        self.controller = ClashController(proxy_manager, log_queue, None, self.proxy_list)
        
        self.root.title("Coreproxy Version0.1alpha By@Hudson Huang")
        self.root.geometry("600x380")
        self.create_widgets()
        self.process_log_queue()

    def create_widgets(self):
        """创建所有的UI组件"""
        self.create_left_panel()
        self.create_right_panel()

    def create_left_panel(self):
        """创建左侧的代理选择列表和按钮"""
        left_frame = tk.Frame(self.root, bg="#3E4451", width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # 代理选择标签
        proxy_label = tk.Label(left_frame, text="选择代理", bg="#3E4451", fg="white", font=("Arial", 12))
        proxy_label.pack(pady=10)

        # 代理选择下拉框
        self.proxy_list = ttk.Combobox(left_frame)  # 初始化代理列表下拉框
        self.proxy_list.pack(padx=10, pady=5, fill=tk.X)

        # 将 proxy_list 传递给 ClashController
        self.controller.proxy_list = self.proxy_list

        # 切换代理按钮
        switch_proxy_button = RoundedButton(left_frame, width=150, height=40, radius=10, color="#61AFEF", text="切换代理", command=self.controller.switch_proxy)
        switch_proxy_button.pack(pady=10)

        # 获取代理列表按钮
        update_proxies_button = RoundedButton(left_frame, width=150, height=40, radius=10, color="#61AFEF", text="获取代理列表", command=self.controller.load_proxies_from_config)
        update_proxies_button.pack(pady=10)

        # 测试延迟按钮
        test_latency_button = RoundedButton(left_frame, width=150, height=40, radius=10, color="#61AFEF", text="测试延迟", command=self.controller.test_all_latencies)
        test_latency_button.pack(pady=10)

        # 启动 Clash 按钮
        start_button = RoundedButton(left_frame, width=150, height=40, radius=10, color="#98C379", text="启动内核", command=lambda: self.controller.start_clash(start_button, stop_button))
        start_button.pack(pady=10)

        # 停止 Clash 按钮
        stop_button = RoundedButton(left_frame, width=150, height=40, radius=10, color="#E06C75", text="关闭内核", command=lambda: self.controller.stop_clash(start_button, stop_button))
        stop_button.pack(pady=10)

    def create_right_panel(self):
        """创建右侧的日志显示和模式切换按钮"""
        right_frame = tk.Frame(self.root, bg="#282C34")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 日志文本框
        log_label = tk.Label(right_frame, text="日志输出", bg="#282C34", fg="white", font=("Arial", 12))
        log_label.pack(pady=10)
        
        self.log_text = ScrolledText(right_frame, state=tk.DISABLED, height=20, bg="#1C1E26", fg="white", font=("Courier", 10))
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # 模式显示标签
        self.mode_label = tk.Label(right_frame, text="当前模式: 未知", bg="#282C34", fg="white", font=("Arial", 12))
        self.mode_label.pack(pady=10)

        # 模式选择按钮
        button_frame = tk.Frame(right_frame, bg="#282C34")
        button_frame.pack(side=tk.BOTTOM, pady=20)

        # Global 模式按钮
        global_button = RoundedButton(button_frame, width=150, height=40, radius=10, color="#98C379", text="全局模式", command=lambda: self.controller.set_mode("global"))
        global_button.grid(row=0, column=0, padx=10)

        # Rule 模式按钮
        rule_button = RoundedButton(button_frame, width=150, height=40, radius=10, color="#98C379", text="规则模式", command=lambda: self.controller.set_mode("rule"))
        rule_button.grid(row=0, column=1, padx=10)

        # Direct 模式按钮
        direct_button = RoundedButton(button_frame, width=150, height=40, radius=10, color="#98C379", text="直连模式", command=lambda: self.controller.set_mode("direct"))
        direct_button.grid(row=0, column=2, padx=10)

    def process_log_queue(self):
        """处理日志队列并将日志输出到日志框"""
        try:
            if not self.log_queue.empty():
                item_type, item_value = self.log_queue.get_nowait()

                if item_type == "message":
                    self.log_text.config(state=tk.NORMAL)
                    self.log_text.insert(tk.END, f"{item_value}\n")
                    self.log_text.config(state=tk.DISABLED)
                    self.log_text.yview(tk.END)
                elif item_type == "mode":
                    self.mode_label.config(text=f"当前模式: {item_value}")

            self.root.after(100, self.process_log_queue)
        except Exception as e:
            logging.error(f"处理日志队列时出错: {str(e)}")
