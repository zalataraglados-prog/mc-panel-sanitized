import { useEffect, useMemo, useRef, useState } from "react";

type Metric = { label: string; value: string };
type MetricPoint = { timestamp: number; value: number };
type Player = { name: string; uuid: string; skin_url: string; position: { x: number; y: number; z: number } };
type Rule = { key: string; value: string };
type CommandTemplate = { name: string; command: string };
type InstanceItem = { name?: string; path?: string };

const translations = {
  en: {
    title: "MC Panel",
    dashboard: "Dashboard",
    instances: "Instances",
    logs: "Logs",
    players: "Players",
    rules: "Server Rules",
    map: "World Map",
    command: "Command",
    rcon: "RCON",
    control: "Control",
    login: "Login",
    username: "Username",
    password: "Password",
    templates: "Command Templates",
    addTemplate: "Add Template",
    start: "Start",
    stop: "Stop",
    restart: "Restart",
    connect: "Connect",
    disconnect: "Disconnect",
    clear: "Clear",
    session: "Session",
    deop: "DeOP",
    tpsTrend: "TPS Trend",
    edit: "Edit",
    save: "Save",
    cancel: "Cancel",
    theme: "Dark / Light",
    language: "中文 / EN",
  },
  zh: {
    title: "MC 面板",
    dashboard: "仪表盘",
    instances: "实例列表",
    logs: "实时日志",
    players: "玩家列表",
    rules: "服务器规则",
    map: "世界地图",
    command: "指令",
    rcon: "RCON",
    control: "控制",
    login: "登录",
    username: "账号",
    password: "密码",
    templates: "常用指令",
    addTemplate: "添加模板",
    start: "启动",
    stop: "停止",
    restart: "重启",
    connect: "连接",
    disconnect: "断开",
    clear: "清空",
    session: "在线时长",
    deop: "取消OP",
    tpsTrend: "TPS 趋势",
    edit: "编辑",
    save: "保存",
    cancel: "取消",
    theme: "深色 / 浅色",
    language: "中文 / EN",
  },
};

function StatCard({ title, value }: { title: string; value: string }) {
  return (
    <div className="card">
      <div className="card-title">{title}</div>
      <div className="card-value">{value}</div>
    </div>
  );
}

function Sparkline({ points }: { points: MetricPoint[] }) {
  if (!points.length) {
    return <div className="sparkline-empty">No data</div>;
  }
  const values = points.map((p) => p.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const width = 260;
  const height = 60;
  const scale = (val: number) => {
    if (max === min) {
      return height / 2;
    }
    return height - ((val - min) / (max - min)) * height;
  };
  const step = width / Math.max(points.length - 1, 1);
  const path = points
    .map((point, index) => {
      const x = index * step;
      const y = scale(point.value);
      return `${index === 0 ? "M" : "L"}${x},${y}`;
    })
    .join(" ");
  return (
    <svg className="sparkline" width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      <path d={path} fill="none" stroke="currentColor" strokeWidth="2" />
    </svg>
  );
}

export function App() {
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [tpsHistory, setTpsHistory] = useState<MetricPoint[]>([]);
  const [instances, setInstances] = useState<InstanceItem[]>([]);
  const [instanceDir, setInstanceDir] = useState("");
  const [players, setPlayers] = useState<Player[]>([]);
  const [rules, setRules] = useState<Rule[]>([]);
  const [rulesDraft, setRulesDraft] = useState<Record<string, string>>({});
  const [rulesEditing, setRulesEditing] = useState(false);
  const [templates, setTemplates] = useState<CommandTemplate[]>([]);
  const [newTemplate, setNewTemplate] = useState({ name: "", command: "" });
  const [token, setToken] = useState("");
  const [role, setRole] = useState("");
  const [lang, setLang] = useState<"en" | "zh">("en");
  const [dark, setDark] = useState(true);
  const [logLines, setLogLines] = useState<string[]>([]);
  const [command, setCommand] = useState("");
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const wsRef = useRef<WebSocket | null>(null);
  const logRef = useRef<HTMLDivElement | null>(null);
  const [logConnected, setLogConnected] = useState(false);
  const [logError, setLogError] = useState("");

  const t = translations[lang];
  const canControl = role === "owner" || role === "admin";
  const canCommand = role === "owner" || role === "admin" || role === "mod";
  const canRcon = role === "owner" || role === "admin";
  const canManagePlayers = role === "owner" || role === "admin" || role === "mod";
  const canTemplateWrite = role === "owner" || role === "admin";
  const canEditRules = role === "owner" || role === "admin";

  useEffect(() => {
    document.body.dataset.theme = dark ? "dark" : "light";
  }, [dark]);

  const authHeader = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token]);

  const refreshData = () => {
    if (!token) {
      return;
    }
    const instanceQuery = instanceDir ? `?instance_dir=${encodeURIComponent(instanceDir)}` : "";
    fetch(`/api/status${instanceQuery}`, { headers: authHeader })
      .then((res) => res.json())
      .then((data) => {
        setMetrics([
          { label: "Players", value: String(data.players ?? 0) },
          { label: "TPS", value: String(data.tps ?? 0) },
          { label: "MSPT", value: String(data.mspt ?? 0) },
          { label: "CPU", value: `${data.cpu_usage ?? 0}%` },
          { label: "Memory", value: `${data.memory_usage ?? 0}%` },
          { label: "Disk", value: `${data.disk_usage ?? 0}%` },
        ]);
      })
      .catch(() => {});
    fetch("/api/instances", { headers: authHeader })
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data.instances)) {
          setInstances(data.instances);
          if (!instanceDir && data.instances.length > 0) {
            setInstanceDir(data.instances[0].path || "");
          }
        }
      })
      .catch(() => {});
    fetch(`/api/players${instanceQuery}`, { headers: authHeader })
      .then((res) => res.json())
      .then((data) => setPlayers(data))
      .catch(() => {});
    fetch(`/api/rules${instanceQuery}`, { headers: authHeader })
      .then((res) => res.json())
      .then((data) => {
        const entries = data.entries || [];
        setRules(entries);
        if (!rulesEditing) {
          const draft: Record<string, string> = {};
          entries.forEach((entry: Rule) => {
            draft[entry.key] = entry.value;
          });
          setRulesDraft(draft);
        }
      })
      .catch(() => {});
    fetch("/api/command-templates", { headers: authHeader })
      .then((res) => res.json())
      .then((data) => setTemplates(data.templates || []))
      .catch(() => {});
    fetch(`/api/metrics?window=60${instanceDir ? `&instance_dir=${encodeURIComponent(instanceDir)}` : ""}`, {
      headers: authHeader,
    })
      .then((res) => res.json())
      .then((data) => setTpsHistory(data || []))
      .catch(() => {});
  };

  useEffect(() => {
    if (token) {
      refreshData();
    }
  }, [token]);

  useEffect(() => {
    if (token) {
      refreshData();
    }
  }, [instanceDir]);

  useEffect(() => {
    if (!token) {
      return;
    }
    const interval = window.setInterval(() => {
      refreshData();
    }, 10000);
    return () => window.clearInterval(interval);
  }, [token, instanceDir]);

  const handleLogin = (event: React.FormEvent) => {
    event.preventDefault();
    const form = event.target as HTMLFormElement;
    const payload = {
      username: (form.elements.namedItem("username") as HTMLInputElement).value,
      password: (form.elements.namedItem("password") as HTMLInputElement).value,
    };
    fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then((res) => res.json())
      .then((data) => {
        setToken(data.token || "");
        setRole(data.role || "");
      })
      .catch(() => {});
  };

  const connectLogs = () => {
    if (!token || wsRef.current) {
      return;
    }
    const query = instanceDir ? `&instance_dir=${encodeURIComponent(instanceDir)}` : "";
    const ws = new WebSocket(
      `ws://localhost:8000/api/logs/ws?token=${token}${query}&max_lines=200&max_per_second=50`
    );
    ws.onmessage = (event) => {
      setLogLines((prev) => [...prev.slice(-200), event.data]);
    };
    ws.onclose = () => {
      wsRef.current = null;
      setLogConnected(false);
    };
    ws.onerror = () => {
      setLogError("Log stream error");
    };
    ws.onopen = () => {
      setLogConnected(true);
      setLogError("");
    };
    wsRef.current = ws;
  };

  const disconnectLogs = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setLogConnected(false);
  };

  const clearLogs = () => {
    setLogLines([]);
  };

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logLines]);

  const sendCommand = (endpoint: string) => {
    if (!command.trim()) {
      return;
    }
    if (endpoint === "/api/rcon" && !canRcon) {
      return;
    }
    if (endpoint === "/api/command" && !canCommand) {
      return;
    }
    fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeader },
      body: JSON.stringify({ command, instance_dir: instanceDir || undefined }),
    })
      .then((res) => res.json())
      .then((data) => {
        const response = data.result || data.response;
        if (response) {
          setLogLines((prev) => [...prev.slice(-200), `> ${command}`, String(response)]);
        }
      })
      .catch(() => {
        setLogError("Command failed");
      });
    setCommandHistory((prev) => [command, ...prev].slice(0, 20));
    setCommand("");
    setHistoryIndex(-1);
  };

  const sendControl = (action: string) => {
    if (!canControl) {
      return;
    }
    fetch("/api/control", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeader },
      body: JSON.stringify({ action, instance_dir: instanceDir || undefined }),
    }).catch(() => {});
  };

  const addTemplate = () => {
    if (!newTemplate.name.trim() || !newTemplate.command.trim()) {
      return;
    }
    if (!canTemplateWrite) {
      return;
    }
    fetch("/api/command-templates", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeader },
      body: JSON.stringify(newTemplate),
    })
      .then((res) => res.json())
      .then(() => {
        setNewTemplate({ name: "", command: "" });
        refreshData();
      })
      .catch(() => {});
  };

  const sendPlayerCommand = (cmd: string) => {
    if (!canManagePlayers) {
      return;
    }
    fetch("/api/command", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeader },
      body: JSON.stringify({ command: cmd, instance_dir: instanceDir || undefined }),
    }).catch(() => {});
  };

  const startEditRules = () => {
    if (!canEditRules) {
      return;
    }
    const draft: Record<string, string> = {};
    rules.forEach((entry) => {
      draft[entry.key] = entry.value;
    });
    setRulesDraft(draft);
    setRulesEditing(true);
  };

  const cancelEditRules = () => {
    setRulesEditing(false);
  };

  const saveRules = () => {
    if (!canEditRules) {
      return;
    }
    const entries = Object.keys(rulesDraft).map((key) => ({ key, value: rulesDraft[key] }));
    fetch("/api/rules", {
      method: "PUT",
      headers: { "Content-Type": "application/json", ...authHeader },
      body: JSON.stringify({ entries, instance_dir: instanceDir || undefined }),
    })
      .then((res) => res.json())
      .then((data) => {
        setRules(data.entries || []);
        setRulesEditing(false);
      })
      .catch(() => {});
  };

  const handleCommandKey = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "ArrowUp") {
      const nextIndex = Math.min(commandHistory.length - 1, historyIndex + 1);
      if (nextIndex >= 0) {
        setCommand(commandHistory[nextIndex]);
        setHistoryIndex(nextIndex);
      }
    }
    if (event.key === "ArrowDown") {
      const nextIndex = Math.max(-1, historyIndex - 1);
      if (nextIndex === -1) {
        setCommand("");
      } else {
        setCommand(commandHistory[nextIndex]);
      }
      setHistoryIndex(nextIndex);
    }
  };

  return (
    <div className="page">
      <header className="header">
        <h1>{t.title}</h1>
        <div className="actions">
          <button className="btn" onClick={() => setDark((value) => !value)}>
            {t.theme}
          </button>
          <button className="btn" onClick={() => setLang((value) => (value === "en" ? "zh" : "en"))}>
            {t.language}
          </button>
        </div>
      </header>

      {!token ? (
        <section className="section">
          <h2>{t.login}</h2>
          <form className="login" onSubmit={handleLogin}>
            <input name="username" placeholder={t.username} />
            <input name="password" type="password" placeholder={t.password} />
            <button className="btn" type="submit">
              {t.login}
            </button>
          </form>
        </section>
      ) : null}

      <section className="section">
        <h2>{t.dashboard}</h2>
        <div className="grid">
          {metrics.map((m) => (
            <StatCard key={m.label} title={m.label} value={m.value} />
          ))}
        </div>
        <div className="sparkline-wrap">
          <div className="card-title">{t.tpsTrend}</div>
          <Sparkline points={tpsHistory} />
        </div>
      </section>

      <section className="section">
        <h2>{t.control}</h2>
        <div className="control-row">
          <button className="btn" disabled={!canControl} onClick={() => sendControl("start")}>
            {t.start}
          </button>
          <button className="btn" disabled={!canControl} onClick={() => sendControl("stop")}>
            {t.stop}
          </button>
          <button className="btn" disabled={!canControl} onClick={() => sendControl("restart")}>
            {t.restart}
          </button>
          <span className="tag">Role: {role || "guest"}</span>
        </div>
      </section>

      <section className="section">
        <h2>{t.logs}</h2>
        <div className="console" ref={logRef}>
          {logLines.map((line, idx) => (
            <div key={`${line}-${idx}`}>{line}</div>
          ))}
        </div>
        {logError ? <div className="console-error">{logError}</div> : null}
        <div className="console-actions">
          <button className="btn" disabled={logConnected} onClick={connectLogs}>
            {t.connect}
          </button>
          <button className="btn" disabled={!logConnected} onClick={disconnectLogs}>
            {t.disconnect}
          </button>
          <button className="btn" onClick={clearLogs}>
            {t.clear}
          </button>
          <span className="tag">{logConnected ? "LIVE" : "OFFLINE"}</span>
          <input
            value={command}
            onChange={(event) => setCommand(event.target.value)}
            onKeyDown={handleCommandKey}
            placeholder={t.command}
          />
          <button className="btn" disabled={!canCommand} onClick={() => sendCommand("/api/command")}>
            {t.command}
          </button>
          <button className="btn" disabled={!canRcon} onClick={() => sendCommand("/api/rcon")}>
            {t.rcon}
          </button>
        </div>
      </section>

      <section className="section">
        <h2>{t.players}</h2>
        <div className="players">
          {players.map((p) => (
            <div key={p.uuid} className="player-card">
              <img src={p.skin_url} alt={p.name} />
              <div>
                <div className="player-name">{p.name}</div>
                <div className="player-meta">
                  {p.position.x},{p.position.y},{p.position.z}
                </div>
                <div className="player-meta">
                  {t.session}: {Math.floor((p as any).session_seconds || 0)}s
                </div>
                <div className="player-actions">
                  <button className="btn" disabled={!canManagePlayers} onClick={() => sendPlayerCommand(`op ${p.name}`)}>
                    OP
                  </button>
                  <button
                    className="btn"
                    disabled={!canManagePlayers}
                    onClick={() => sendPlayerCommand(`deop ${p.name}`)}
                  >
                    {t.deop}
                  </button>
                  <button
                    className="btn"
                    disabled={!canManagePlayers}
                    onClick={() => sendPlayerCommand(`kick ${p.name}`)}
                  >
                    Kick
                  </button>
                  <button
                    className="btn"
                    disabled={!canManagePlayers}
                    onClick={() => sendPlayerCommand(`tp ${p.name} @s`)}
                  >
                    Teleport
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <h2>{t.rules}</h2>
        <div className="rules-actions">
          <button className="btn" disabled={!canEditRules} onClick={startEditRules}>
            {t.edit}
          </button>
          <button className="btn" disabled={!rulesEditing} onClick={saveRules}>
            {t.save}
          </button>
          <button className="btn" disabled={!rulesEditing} onClick={cancelEditRules}>
            {t.cancel}
          </button>
        </div>
        <div className="rules">
          {rules.map((r) => (
            <div key={r.key} className="rule-row">
              <span>{r.key}</span>
              {rulesEditing ? (
                <input
                  value={rulesDraft[r.key] ?? ""}
                  onChange={(event) => setRulesDraft({ ...rulesDraft, [r.key]: event.target.value })}
                />
              ) : (
                <span>{r.value}</span>
              )}
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <h2>{t.map}</h2>
        <div className="map-placeholder">Map module placeholder</div>
      </section>

      <section className="section">
        <h2>{t.templates}</h2>
        <div className="templates">
          <div className="template-form">
            <input
              value={newTemplate.name}
              onChange={(event) => setNewTemplate({ ...newTemplate, name: event.target.value })}
              placeholder="name"
            />
            <input
              value={newTemplate.command}
              onChange={(event) => setNewTemplate({ ...newTemplate, command: event.target.value })}
              placeholder="command"
            />
            <button className="btn" disabled={!canTemplateWrite} onClick={addTemplate}>
              {t.addTemplate}
            </button>
          </div>
          <div className="template-list">
            {templates.map((tpl) => (
              <button key={tpl.name} className="btn" onClick={() => setCommand(tpl.command)}>
                {tpl.name}
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="section">
        <h2>{t.instances}</h2>
        <div className="instance-select">
          <select value={instanceDir} onChange={(event) => setInstanceDir(event.target.value)}>
            <option value="">default</option>
            {instances.map((item) => (
              <option key={item.path || item.name} value={item.path || ""}>
                {item.name || item.path}
              </option>
            ))}
          </select>
          <button className="btn" onClick={refreshData}>
            Refresh
          </button>
        </div>
        <ul>
          {instances.map((item) => (
            <li key={item.path || item.name}>{item.name || item.path}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}
