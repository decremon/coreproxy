import websocket

class LogListener:
    def __init__(self, url="ws://127.0.0.1:9090/logs?level=info"):
        self.url = url

    def on_message(self, ws, message):
        print(f"Log: {message}")

    def on_error(self, ws, error):
        print(f"Error: {error}")

    # 修改 on_close 方法，添加参数
    def on_close(self, ws, close_status_code, close_msg):
        print(f"Connection closed with status: {close_status_code}, message: {close_msg}")

    def on_open(self, ws):
        print("Connection opened")

    def start(self):
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(self.url,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        ws.on_open = self.on_open
        ws.run_forever()
