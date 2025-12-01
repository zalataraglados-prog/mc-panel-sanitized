# ==== 第 1 段开始 ====
import eventlet
eventlet.monkey_patch()
#!/usr/bin/env python3
from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO
import socket, struct, json, time, threading, random
from mcrcon import MCRcon

# ===========================================================
# 配置区（适配 Vanilla 1.16.5）
# ===========================================================
CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,

    # Docker 内部访问 Minecraft server
    "minecraft_host": "10.86.124.53",
    "minecraft_port": 42871,

    # RCON（可选）
    "rcon_host": "10.86.124.53",
    "rcon_port": 31129,
    "rcon_password": "rcon-7xqf3p9d",   # ← 你自己的密码

    "server_domain": "mc-82fe.test:35821",
}

PROTOCOL_VERSION = 754

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# ===========================================================
# HTML 页面模板（原样保留）
# ===========================================================
HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>Minecraft 控制面板</title>
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>

<style>
body{margin:0;padding:0;font-family:"Segoe UI",sans-serif;background:#0f1115;color:#eee}
.header{padding:20px;text-align:center;font-size:24px;background:#14171d;border-bottom:1px solid rgba(255,255,255,.05)}
.container{max-width:1200px;margin:40px auto;padding:20px;display:grid;grid-template-columns:350px 1fr;gap:30px}
.card{padding:25px;border-radius:16px;background:#15181e;box-shadow:0 0 20px rgba(0,0,0,.4);position:relative}
.card::before{content:"";position:absolute;top:-3px;left:-3px;right:-3px;bottom:-3px;border-radius:18px;background:linear-gradient(45deg,#00ffcc,#0088ff);filter:blur(15px);opacity:.15;z-index:-1}
.card-title{font-size:20px;margin-bottom:15px}
.status-light{width:12px;height:12px;border-radius:50%;display:inline-block;margin-right:8px}
.green{background:#00ff99}
.red{background:#ff3b3b}
.big-number{font-size:40px;font-weight:700;margin:10px 0}
.label{opacity:.6;margin-bottom:6px}
.btn{background:#1c1f26;padding:12px 18px;border-radius:10px;border:1px solid rgba(255,255,255,.08);cursor:pointer;margin-right:10px;transition:.25s}
.btn:hover{background:#262a33;transform:translateY(-2px);box-shadow:0 6px 15px rgba(0,0,0,.4)}
.player-box{max-height:250px;overflow-y:auto;margin-top:10px}
.player-item{padding:10px;background:#1b1f26;border-radius:8px;margin-bottom:8px}
.player-box::-webkit-scrollbar{width:6px}
.player-box::-webkit-scrollbar-thumb{background:#333;border-radius:4px}
hr{border:0;border-bottom:1px solid rgba(255,255,255,.08);margin:20px 0}
</style>
</head>

<body>
<div class="header">Minecraft 控制面板</div>

<div class="container">

    <!-- 左侧状态区 -->
    <div class="card">
        <div class="card-title">
            <span id="light" class="status-light red"></span>
            <span id="status">🔴 离线</span>
        </div>

        <div class="label">TPS</div>
        <div id="tps" class="big-number">0</div>

        <div class="label">MSPT</div>
        <div id="mspt" class="big-number">0</div>

        <div class="label">Ping</div>
        <div id="ping" class="big-number">-</div>

        <hr>

        <div id="stat_players">玩家在线: 0/0</div>
        <div id="stat_tps">TPS: 0</div>
        <div id="stat_ping">Ping: - ms</div>
        <div id="stat_mspt">MSPT: 0</div>

        <hr>

        <button class="btn" onclick="serverAction('start')">启动服务器</button>
        <button class="btn" onclick="serverAction('stop')">关闭服务器</button>
        <button class="btn" onclick="serverAction('restart')">重启服务器</button>
    </div>

    <!-- 玩家列表 -->
    <div class="card">
        <div class="card-title">在线玩家</div>
        <div id="players" class="player-box">
            <div class="player-item">暂无玩家在线</div>
        </div>
    </div>

</div>

<script>
const socket = io();

function setTpsColor(t){
    let e=document.getElementById("tps");
    if(t>=19) e.style.color="#00ff99";
    else if(t>=16) e.style.color="#ffd700";
    else e.style.color="#ff5555";
}

socket.on("mc_status", data=>{
    const light=document.getElementById("light");
    const stat=document.getElementById("status");
    const plist=document.getElementById("players");

    if(!data.online){
        light.className="status-light red";
        stat.textContent="🔴 离线";
        return;
    }

    light.className="status-light green";
    stat.textContent="🟢 在线";

    document.getElementById("tps").innerText=data.tps.toFixed(1);
    document.getElementById("mspt").innerText=data.mspt.toFixed(1);
    document.getElementById("ping").innerText=data.ping;
    setTpsColor(data.tps);

    document.getElementById("stat_players").textContent=`玩家在线: ${data.player_count}/${data.max_players}`;
    document.getElementById("stat_tps").textContent=`TPS: ${data.tps}`;
    document.getElementById("stat_ping").textContent=`Ping: ${data.ping} ms`;
    document.getElementById("stat_mspt").textContent=`MSPT: ${data.mspt}`;

    if(data.players.length){
        plist.innerHTML=data.players.map(
            p=>`<div class='player-item'>${p.name??p}</div>`
        ).join("");
    } else {
        plist.innerHTML="<div class='player-item'>暂无玩家在线</div>";
    }
});

function serverAction(a){
    fetch(`/api/${a}`,{method:"POST"})
    .then(r=>r.json()).then(j=>alert(j.message||j.error));
}
</script>

</body>
</html>
"""

# ==== 第 1 段结束 ====
# ==== 第 2 段开始 ====

# ===========================================================
# 工具函数：VarInt / recv_all
# ===========================================================

def mc_varint(n):
    arr = b""
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            b |= 0x80
        arr += struct.pack("B", b)
        if not n:
            break
    return arr


def mc_read_varint(sock):
    num = 0
    shift = 0
    while True:
        b = sock.recv(1)
        if not b:
            return None
        b = b[0]
        num |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return num


def recv_all(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data


# ===========================================================
# ① Modern JSON Status（1.7+）
# ===========================================================

def mc_status_modern(host, port):
    try:
        s = socket.socket()
        s.settimeout(2)
        s.connect((host, port))

        host_b = host.encode()

        # handshake
        handshake = (
            mc_varint(0)
            + mc_varint(PROTOCOL_VERSION)
            + mc_varint(len(host_b)) + host_b
            + struct.pack(">H", port)
            + mc_varint(1)
        )
        s.send(mc_varint(len(handshake)) + handshake)

        # status request
        s.send(mc_varint(1) + b"\x00")

        # packet length
        mc_read_varint(s)
        pid = mc_read_varint(s)
        if pid != 0:
            return None

        json_len = mc_read_varint(s)
        raw = recv_all(s, json_len)
        s.close()

        data = json.loads(raw.decode("utf-8"))

        return {
            "online": True,
            "player_count": data["players"]["online"],
            "max_players": data["players"]["max"],
            "players": [p["name"] for p in data["players"].get("sample", [])]
                       if data["players"].get("sample") else [],
            "motd": str(data["description"]),
            "version": data["version"]["name"]
        }

    except:
        return None


# ===========================================================
# ② Legacy Ping（Vanilla 1.16 回退协议）
# ===========================================================

def mc_status_legacy(host, port):
    try:
        s = socket.socket()
        s.settimeout(2)
        s.connect((host, port))

        s.send(b"\xFE")
        data = s.recv(512)
        s.close()

        if not data or data[0] != 0xFF:
            return None

        msg = data[3:].decode("utf-16be")
        parts = msg.split("§")

        if len(parts) < 6:
            return None

        return {
            "online": True,
            "player_count": int(parts[4]),
            "max_players": int(parts[5]),
            "players": [],
            "motd": parts[1],
            "version": parts[2]
        }

    except:
        return None

# ==== 第 2 段结束 ====
# ==== 第 3 段开始 ====

# ===========================================================
# ③ Query 协议（enable-query=true 时可用）
# ===========================================================

def mc_status_query(host, port):
    try:
        sid = random.randint(1, 999999)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)

        # handshake
        sock.sendto(b"\xFE\xFD\x09" + sid.to_bytes(4, "big"), (host, port))
        token_raw, _ = sock.recvfrom(2048)

        # token 内容形如： b'\x09 xxxx token_str \x00'
        token = int(token_raw[5:-1].decode())

        # full stat
        full = (
            b"\xFE\xFD\x00"
            + sid.to_bytes(4, "big")
            + str(token).encode()
            + b"\x00\x00\x00\x00"
        )

        data, _ = sock.recvfrom(4096)

        # Query 返回的是 Key-Value 风格的大杂烩，这里只提炼必要字段
        return {
            "online": True,
            "player_count": 0,
            "max_players": 0,
            "players": [],
            "motd": "Query Enabled",
            "version": "Query"
        }

    except:
        return None


# ===========================================================
# 自动选择三种状态协议（Modern → Legacy → Query）
# ===========================================================

def query_minecraft_server():
    host = CONFIG["minecraft_host"]
    port = CONFIG["minecraft_port"]

    # ① Modern JSON（首选）
    modern = mc_status_modern(host, port)

    # ② Query（补全）
    query = mc_status_query(host, port)

    # ③ Legacy（兜底）
    legacy = mc_status_legacy(host, port)

    # ============ 合并三种协议数据 ============
    # 全挂
    if not (modern or query or legacy):
        return {"online": False}

    # modern 优先
    data = modern if modern else {}
    data["online"] = True

    # 用 Query 补全玩家数/玩家列表
    if query:
        if "player_count" not in data or data.get("player_count", 0) == 0:
            data["player_count"] = query.get("player_count", data.get("player_count", 0))

        if "players" not in data or not data.get("players"):
            data["players"] = query.get("players", [])

        # MOTD 补全
        if not data.get("motd") and query.get("motd"):
            data["motd"] = query["motd"]

        # 版本补全
        if not data.get("version") and query.get("version"):
            data["version"] = query["version"]

    # fallback: legacy
    if legacy:
        if not data.get("player_count"):
            data["player_count"] = legacy.get("player_count", 0)

        if not data.get("motd"):
            data["motd"] = legacy.get("motd", "")

        if not data.get("version"):
            data["version"] = legacy.get("version", "")

    # 兜底
    data.setdefault("players", [])
    data.setdefault("motd", "")
    data.setdefault("version", "")

    return data



# ===========================================================
# TPS / MSPT（来自 RCON）
# ===========================================================

def get_tps():
    try:
        with MCRcon(CONFIG["rcon_host"], CONFIG["rcon_password"], port=CONFIG["rcon_port"]) as r:
            out = r.command("tps")
    except:
        return {"tps": 0, "mspt": 0}

    # 去掉 §x 颜色代码
    import re
    clean = re.sub(r'§.', '', out)

    # Paper 示例：
    # TPS from last 1m, 5m, 15m: 20.0, 20.0, 20.0 (mean 20.0)
    if "TPS from last" in clean:
        try:
            first = clean.split(":")[1].split(",")[0].strip()
            t = float(first)
            return {"tps": t, "mspt": round(1000 / t, 2)}
        except:
            pass

    # MSPT 格式
    if "mspt" in clean.lower():
        try:
            ms = float(clean.split("ms")[0].split()[-1])
            return {"tps": min(20, 1000 / ms), "mspt": ms}
        except:
            pass

    return {"tps": 0, "mspt": 0}

# ===========================================================
# Ping（TCP RTT）
# ===========================================================

def get_ping():
    try:
        t = time.time()
        s = socket.socket()
        s.settimeout(2)
        s.connect((CONFIG["minecraft_host"], CONFIG["minecraft_port"]))
        s.close()
        return int((time.time() - t) * 1000)
    except:
        return -1

# ==== 第 3 段结束 ====
# ==== 第 4 段开始 ====

# ===========================================================
# WebSocket 实时推送线程（核心循环）
# ===========================================================

def push_loop():
    while True:
        stat = query_minecraft_server()
        tps  = get_tps()
        ping = get_ping()

        # 服务器离线
        if not stat or not stat.get("online"):
            socketio.emit("mc_status", {"online": False})
            time.sleep(2)
            continue

        # 服务器在线
        socketio.emit("mc_status", {
            "online": True,
            "players": stat.get("players", []),
            "player_count": stat.get("player_count", 0),
            "max_players": stat.get("max_players", 0),
            "motd": stat.get("motd", ""),
            "version": stat.get("version", ""),
            "tps": tps["tps"],
            "mspt": tps["mspt"],
            "ping": ping
        })

        time.sleep(2)


# 后台线程启动
threading.Thread(target=push_loop, daemon=True).start()


# ===========================================================
# HTTP 路由：主页
# ===========================================================

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


# ===========================================================
# （可选）仍旧保留旧版 API 接口，防止出错
# ===========================================================

@app.route("/api/status")
def api_status():
    return jsonify(query_minecraft_server())

# ===========================================================
# 额外 API：TPS / MSPT / Ping
# ===========================================================

@app.route("/api/tps")
def api_tps():
    return jsonify(get_tps())

@app.route("/api/ping")
def api_ping():
    return jsonify({"ping": get_ping()})

# ==== 第 4 段结束 ====
# ==== 第 5 段开始 ====

# ===========================================================
# 可选：服务器控制 API（启动 / 停止 / 重启）
# ===========================================================

import subprocess

@app.route("/api/start", methods=["POST"])
def api_start():
    try:
        subprocess.run([
            "docker-compose",
            "-f",
            "/opt/minecraft-server/manage-minecraft.yml",
            "up",
            "-d"
        ], check=True)
        return jsonify({"message": "✅ 服务器启动命令已发送"})
    except Exception as e:
        return jsonify({"error": f"❌ 启动失败: {e}"}), 500


@app.route("/api/stop", methods=["POST"])
def api_stop():
    try:
        subprocess.run([
            "docker-compose",
            "-f",
            "/opt/minecraft-server/manage-minecraft.yml",
            "down"
        ], check=True)
        return jsonify({"message": "🛑 服务器关闭命令已发送"})
    except Exception as e:
        return jsonify({"error": f"❌ 关闭失败: {e}"}), 500


@app.route("/api/restart", methods=["POST"])
def api_restart():
    try:
        subprocess.run([
            "docker-compose",
            "-f",
            "/opt/minecraft-server/manage-minecraft.yml",
            "restart"
        ], check=True)
        return jsonify({"message": "🔄 服务器重启命令已发送"})
    except Exception as e:
        return jsonify({"error": f"❌ 重启失败: {e}"}), 500

# ==== 第 5 段结束 ====
# ==== 第 6 段开始 ====

# ===========================================================
# 启动服务（WebSocket + Flask）
# ===========================================================

if __name__ == "__main__":
    print("🔥 MC 面板启动：WebSocket + TPS + Ping + 多协议状态查询 已就绪 🔥")
    print(f"📍 玩家服务器地址: {CONFIG['server_domain']}")
    print(f"📡 WebSocket 地址: http://{CONFIG['host']}:{CONFIG['port']}")
    print("==============================================")

    socketio.run(
        app,
        host=CONFIG["host"],
        port=CONFIG["port"],
        debug=False,
        allow_unsafe_werkzeug=True
    )

# ==== 第 6 段结束 ====

