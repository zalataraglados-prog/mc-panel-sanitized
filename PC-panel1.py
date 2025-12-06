import threading
import time
import requests
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem

# ============================================
# 配置
# ============================================
BASE_URL = "http://ztlearn.xyz:15000"
REFRESH_INTERVAL = 2  # 秒

# ============================================
# 托盘图标生成
# ============================================
def generate_icon(color):
    img = Image.new("RGB", (64, 64), "white")
    d = ImageDraw.Draw(img)
    d.ellipse((10, 10, 54, 54), fill=color)
    return img

ICON_GREEN = generate_icon("green")
ICON_YELLOW = generate_icon("yellow")
ICON_RED = generate_icon("red")


# ============================================
# 主 GUI 程序
# ============================================
class MCPClient:
    def __init__(self):
        self.root = ttk.Window(themename="litera")
        self.root.title("Minecraft 控制面板")
        self.root.geometry("720x540")

        # 数据缓存
        self.tps_history = []
        self.ping_history = []

        # 上半部分：状态卡片
        frame_top = ttk.Frame(self.root)
        frame_top.pack(fill=X, pady=10)

        self.label_online = ttk.Label(frame_top, text="服务器状态：未知", font=("Microsoft YaHei", 16))
        self.label_online.pack(side=LEFT, padx=20)

        self.label_players = ttk.Label(frame_top, text="玩家：-", font=("Microsoft YaHei", 16))
        self.label_players.pack(side=LEFT, padx=20)

        # 下半部分：折线图
        frame_chart = ttk.Frame(self.root)
        frame_chart.pack(fill=BOTH, expand=True)

        fig = Figure(figsize=(6, 4), dpi=100)
        self.ax_tps = fig.add_subplot(211)
        self.ax_ping = fig.add_subplot(212)

        self.ax_tps.set_title("TPS (最近数据)")
        self.ax_ping.set_title("Ping (最近数据)")

        self.canvas = FigureCanvasTkAgg(fig, master=frame_chart)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        # 托盘线程
        self.tray_icon = None
        threading.Thread(target=self.init_tray, daemon=True).start()

        # 开始轮询线程
        threading.Thread(target=self.update_loop, daemon=True).start()

    # ============================================
    # 托盘图标系统
    # ============================================
    def init_tray(self):
        def on_quit():
            if self.tray_icon:
                self.tray_icon.stop()
            self.root.quit()

        menu = (
            MenuItem("打开窗口", lambda: self.root.deiconify()),
            MenuItem("退出程序", on_quit)
        )

        self.tray_icon = pystray.Icon("mc_panel", ICON_RED, "MC Panel", menu)
        self.tray_icon.run()

    def set_tray_green(self):
        if self.tray_icon:
            self.tray_icon.icon = ICON_GREEN

    def set_tray_yellow(self):
        if self.tray_icon:
            self.tray_icon.icon = ICON_YELLOW

    def set_tray_red(self):
        if self.tray_icon:
            self.tray_icon.icon = ICON_RED

    # ============================================
    # 后台轮询线程
    # ============================================
    def update_loop(self):
        while True:
            try:
                status = requests.get(f"{BASE_URL}/api/status", timeout=4).json()
                tps_data = requests.get(f"{BASE_URL}/api/tps", timeout=4).json()
                ping_data = requests.get(f"{BASE_URL}/api/ping", timeout=4).json()

                # 更新 GUI 文本
                online = status.get("online", False)
                players = status.get("players", [])
                self.label_online.config(text=f"服务器状态：{'在线' if online else '离线'}")

                self.label_players.config(text=f"玩家：{', '.join(players) if players else '无'}")

                # 更新曲线数据
                tps = tps_data.get("tps", 0)
                ping = ping_data.get("ping", 0)

                self.tps_history.append(tps)
                self.ping_history.append(ping)

                # 历史长度限制
                if len(self.tps_history) > 50:
                    self.tps_history.pop(0)
                if len(self.ping_history) > 50:
                    self.ping_history.pop(0)

                # 绘图
                self.ax_tps.clear()
                self.ax_ping.clear()

                self.ax_tps.plot(self.tps_history, label="TPS")
                self.ax_ping.plot(self.ping_history, label="Ping")

                self.ax_tps.set_ylim(0, 25)
                self.ax_ping.set_ylim(0, max(self.ping_history + [400]))

                self.ax_tps.set_title("TPS")
                self.ax_ping.set_title("Ping")

                self.canvas.draw()

                # 托盘图标逻辑
                if not online:
                    self.set_tray_red()
                else:
                    if tps >= 19:
                        self.set_tray_green()
                    elif tps >= 14:
                        self.set_tray_yellow()
                    else:
                        self.set_tray_red()

            except Exception:
                self.set_tray_red()
                self.label_online.config(text="服务器状态：连接失败")
                self.label_players.config(text="玩家：-")

            time.sleep(REFRESH_INTERVAL)

    # ============================================
    # 主循环
    # ============================================
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MCPClient()
    app.run()
