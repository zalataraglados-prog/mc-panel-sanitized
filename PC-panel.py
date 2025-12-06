import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import requests
import threading
import time
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image
import pystray

BASE = "http://ztlearn.xyz:5000"

# ===============================
# 请求 API
# ===============================
def fetch_json(url):
    try:
        r = requests.get(url, timeout=3)
        return r.json()
    except Exception as e:
        print(f"API请求异常: {e}")
        return None


# ===============================
# 主界面类
# ===============================
class MCMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft 服务器监控")
        self.root.geometry("820x550")

        # Fluent 风格
        style = tb.Style("flatly")

        # 顶部标题条
        frame_top = ttk.Frame(self.root)
        frame_top.pack(fill=tk.X, pady=10)

        ttk.Label(frame_top, text="Minecraft 实时监控面板",
                  font=("Microsoft YaHei", 18, "bold")).pack()

        # 状态指示灯
        self.light = ttk.Label(frame_top, text="●", font=("Arial", 20))
        self.light.pack()

        # 中部：图表
        frame_chart = ttk.Frame(self.root)
        frame_chart.pack(fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(5, 3), dpi=90)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("TPS / Ping / MSPT 实时曲线")
        self.ax.set_ylim(0, 30)

        self.line_tps, = self.ax.plot([], [], label="TPS", color="lime")
        self.line_ping, = self.ax.plot([], [], label="Ping", color="cyan")
        self.line_mspt, = self.ax.plot([], [], label="MSPT", color="orange")
        self.ax.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_chart)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 右侧玩家列表
        frame_players = ttk.LabelFrame(self.root, text="在线玩家")
        frame_players.place(x=620, y=80, width=180, height=450)

        self.player_list = tk.Listbox(frame_players, font=("Microsoft YaHei", 11))
        self.player_list.pack(fill=tk.BOTH, expand=True)

        # 数据缓存
        self.tps_data = []
        self.ping_data = []
        self.mspt_data = []
        self.max_points = 50

        # 运行标志，必须在线程启动前设置
        self._running = True

        # 启动后台线程
        threading.Thread(target=self.update_loop, daemon=True).start()

        # 托盘图标
        threading.Thread(target=self.create_tray_icon, daemon=True).start()

        # 关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)


    # ===========================
    # 托盘图标
    # ===========================
    def create_tray_icon(self):
        image = Image.new("RGB", (64, 64), "green")
        def on_exit(icon, item):
            icon.stop()
            self.root.quit()
        menu = pystray.Menu(pystray.MenuItem('退出', on_exit))
        self.icon = pystray.Icon("MC Monitor", image, "MC 监控", menu=menu)
        self.icon.run()

    # ===========================
    # 更新线程
    # ===========================
    def update_loop(self):
        while self._running:
            stat = fetch_json(f"{PANEL}/api/status")
            ping = fetch_json(f"{PANEL}/api/ping")
            tps  = fetch_json(f"{PANEL}/api/tps")

            def update_ui():
                # 更新指示灯颜色
                if stat and stat.get("online"):
                    self.light.configure(foreground="lime")
                else:
                    self.light.configure(foreground="red")

                # 更新玩家列表
                self.player_list.delete(0, tk.END)
                if stat and stat.get("players"):
                    for p in stat["players"]:
                        self.player_list.insert(tk.END, p)
                else:
                    self.player_list.insert(tk.END, "无玩家在线")

                # 更新曲线数据
                if tps and isinstance(tps, dict):
                    self.tps_data.append(tps.get("tps", 0))
                    self.mspt_data.append(tps.get("mspt", 0))
                if ping and isinstance(ping, dict):
                    self.ping_data.append(ping.get("ping", 0))

                # 限制长度
                self.tps_data = self.tps_data[-self.max_points:]
                self.mspt_data = self.mspt_data[-self.max_points:]
                self.ping_data = self.ping_data[-self.max_points:]

                # 保证数据长度一致
                min_len = min(len(self.tps_data), len(self.mspt_data), len(self.ping_data))
                self.tps_data = self.tps_data[-min_len:]
                self.mspt_data = self.mspt_data[-min_len:]
                self.ping_data = self.ping_data[-min_len:]

                x = list(range(min_len))
                self.line_tps.set_data(x, self.tps_data)
                self.line_ping.set_data(x, self.ping_data)
                self.line_mspt.set_data(x, self.mspt_data)

                self.ax.set_xlim(0, self.max_points)
                self.canvas.draw()

            self.root.after(0, update_ui)
            time.sleep(2)

    def on_close(self):
        self._running = False
        try:
            if hasattr(self, 'icon') and self.icon:
                self.icon.stop()
        except Exception as e:
            print(f"托盘关闭异常: {e}")
        self.root.destroy()


# ===============================
# 主入口
# ===============================
def main():
    root = tb.Window(themename="flatly")
    app = MCMonitor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
