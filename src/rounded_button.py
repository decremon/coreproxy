import tkinter as tk
from tkinter import Canvas

class RoundedButton(tk.Canvas):
    def __init__(self, parent, width, height, radius, color, text='', command=None):
        tk.Canvas.__init__(self, parent, height=height, width=width, bg=parent['bg'], highlightthickness=0)
        self.command = command

        # 绘制圆角矩形按钮
        self.radius = radius
        self.rect = self.create_rounded_rect(0, 0, width, height, radius, fill=color)
        self.text = self.create_text(width//2, height//2, text=text, fill="white", font=("Arial", 12))

        # 绑定点击事件
        self.bind("<Button-1>", self.on_click)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        """绘制一个圆角矩形"""
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1,
                  x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r,
                  x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2,
                  x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def on_click(self, event):
        """点击按钮时调用的函数"""
        if self.command:
            self.command()
