import subprocess
import threading
import logging
import yaml
import winreg as reg
import ctypes
import io

class ClashController:
    def __init__(self, proxy_manager, log_queue, log_text, proxy_list):
        self.proxy_manager = proxy_manager
        self.log_queue = log_queue
        self.log_text = log_text
        self.proxy_list = proxy_list
        self.clash_process = None
        self.proxy_group_name = 'Auto'  # 默认代理组名称

    def set_system_proxy(self, proxy_ip_port):
        """在 Windows 上设置系统代理"""
        try:
            internet_settings = reg.OpenKey(reg.HKEY_CURRENT_USER,
                                            r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
                                            0, reg.KEY_ALL_ACCESS)

            reg.SetValueEx(internet_settings, 'ProxyEnable', 0, reg.REG_DWORD, 1)
            reg.SetValueEx(internet_settings, 'ProxyServer', 0, reg.REG_SZ, proxy_ip_port)
            reg.CloseKey(internet_settings)

            ctypes.windll.Wininet.InternetSetOptionW(0, 39, 0, 0)

            self.log_queue.put(("message", "Windows 系统代理设置成功。"))
        except Exception as e:
            self.log_queue.put(("message", f"设置系统代理时出错: {str(e)}"))

    def disable_system_proxy(self):
        """在 Windows 上禁用系统代理"""
        try:
            internet_settings = reg.OpenKey(reg.HKEY_CURRENT_USER,
                                            r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
                                            0, reg.KEY_ALL_ACCESS)

            reg.SetValueEx(internet_settings, 'ProxyEnable', 0, reg.REG_DWORD, 0)
            reg.CloseKey(internet_settings)

            ctypes.windll.Wininet.InternetSetOptionW(0, 39, 0, 0)

            self.log_queue.put(("message", "Windows 系统代理已禁用。"))
        except Exception as e:
            self.log_queue.put(("message", f"禁用系统代理时出错: {str(e)}"))

    def start_clash(self, start_button, stop_button):
        """启动内核并捕获日志"""
        if self.clash_process is None:
            try:
                clash_path = "./core/core.exe"  #内核可执行文件路径
                self.clash_process = subprocess.Popen(
                    [clash_path, "-d", "./config"],  # 启动 Clash
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1,
                    encoding='utf-8',  # 指定编码为 UTF-8
                    errors='replace'  # 在遇到无法解码的字符时，替换这些字符
                )

                # 启动两个线程来分别读取 stdout 和 stderr
                threading.Thread(target=self.read_clash_stdout_logs, daemon=True).start()
                threading.Thread(target=self.read_clash_stderr_logs, daemon=True).start()

                self.log_queue.put(("message", "内核已启动"))
                self.set_system_proxy("127.0.0.1:7890")
                self.load_proxies_from_config()

                start_button.config(state="disabled")
                stop_button.config(state="normal")

            except FileNotFoundError:
                logging.error(f"启动内核时出错: 未找到内核可执行文件")
                self.log_queue.put(("message", "启动内核时出错: 未找到内核可执行文件"))
            except Exception as e:
                logging.error(f"启动内核时出错: {str(e)}")
                self.log_queue.put(("message", f"启动内核时出错: {str(e)}"))

    def read_clash_stdout_logs(self):
        """读取内核进程的标准输出日志"""
        if self.clash_process:
            for line in iter(self.clash_process.stdout.readline, ''):
                self.log_queue.put(("message", line.strip()))

    def read_clash_stderr_logs(self):
        """读取内核进程的错误输出日志"""
        if self.clash_process:
            for line in iter(self.clash_process.stderr.readline, ''):
                self.log_queue.put(("message", line.strip()))

    def load_proxies_from_config(self):
        """从 config.yaml 文件中加载代理列表"""
        try:
            with open('./config/config.yaml', 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)

            proxies = config_data.get('proxies', [])
            if not proxies:
                self.log_queue.put(("message", "配置文件中没有找到代理列表"))
                return

            proxy_names = [proxy['name'] for proxy in proxies]
            logging.info(f"从配置文件中加载代理列表: {proxy_names}")
            
            if self.proxy_list is not None and proxy_names:
                self.proxy_list['values'] = proxy_names
                self.proxy_list.current(0)
                self.log_queue.put(("message", "代理列表已从配置文件中加载"))
            else:
                self.log_queue.put(("message", "代理列表为空或 UI 尚未初始化"))

        except FileNotFoundError:
            logging.error(f"未找到 config.yaml 文件")
            self.log_queue.put(("message", "未找到 config.yaml 文件"))
        except Exception as e:
            logging.error(f"加载配置文件时出错: {str(e)}")
            self.log_queue.put(("message", f"加载配置文件时出错: {str(e)}"))

    def stop_clash(self, start_button, stop_button):
        """停止 Clash"""
        if self.clash_process is not None:
            try:
                logging.info("停止 Clash")
                self.clash_process.terminate()
                self.clash_process = None
                self.log_queue.put(("message", "Clash 已停止"))

                self.disable_system_proxy()

                start_button.config(state="normal")
                stop_button.config(state="disabled")

            except Exception as e:
                logging.error(f"停止内核时出错: {str(e)}")
                self.log_queue.put(("message", f"停止内核时出错: {str(e)}"))

    def switch_proxy(self):
        """在后台线程中切换代理"""
        threading.Thread(target=self._switch_proxy_in_thread).start()

    def _switch_proxy_in_thread(self):
        """切换代理的后台线程方法"""
        try:
            selected_proxy = self.proxy_list.get()
            if selected_proxy:
                success = self.proxy_manager.switch_proxy(self.proxy_group_name, selected_proxy)
                if success:
                    logging.info(f"已切换代理到: {selected_proxy}")
                    self.log_queue.put(("message", f"已切换到代理: {selected_proxy}"))
                else:
                    self.log_queue.put(("message", f"切换代理失败"))
        except Exception as e:
            logging.error(f"切换代理时出错: {str(e)}")
            self.log_queue.put(("message", f"切换代理时出错: {str(e)}"))

    def test_all_latencies(self):
        """在后台线程中测试所有代理节点的延迟"""
        threading.Thread(target=self._test_latencies_in_thread).start()

    def _test_latencies_in_thread(self):
        """测试所有代理的延迟"""
        try:
            proxies = self.proxy_manager.get_proxies().get("proxies", {})
            for proxy_name in proxies:
                delay = self.proxy_manager.test_latency(proxy_name)
                self.log_queue.put(("message", f"{proxy_name} 的延迟为: {delay} ms"))
        except Exception as e:
            logging.error(f"测试延迟时出错: {str(e)}")

    def set_mode(self, mode):
        """设置代理模式"""
        threading.Thread(target=self._set_mode_in_thread, args=(mode,)).start()

    def _set_mode_in_thread(self, mode):
        """后台线程切换代理模式"""
        try:
            success = self.proxy_manager.set_mode(mode)
            if success:
                logging.info(f"代理模式已切换为: {mode}")
                self.log_queue.put(("message", f"代理模式已切换为: {mode}"))
                self.log_queue.put(("mode", mode))  # 更新 UI 中的模式显示
            else:
                self.log_queue.put(("message", "切换代理模式失败"))
        except Exception as e:
            logging.error(f"切换代理模式时出错: {str(e)}")
            self.log_queue.put(("message", f"切换代理模式时出错: {str(e)}"))

    def update_mode(self, button):
        """刷新代理模式"""
        threading.Thread(target=self._update_mode_in_thread, args=(button,)).start()

    def _update_mode_in_thread(self, button):
        """后台线程刷新代理模式"""
        try:
            config = self.proxy_manager.get_configs()
            mode = config.get("mode", "未知")
            logging.info(f"当前代理模式: {mode}")
            button.config(text=f"当前模式: {mode}")
            self.log_queue.put(("mode", mode))
        except Exception as e:
            logging.error(f"获取代理模式时出错: {str(e)}")
            self.log_queue.put(("message", f"获取代理模式时出错: {str(e)}"))
