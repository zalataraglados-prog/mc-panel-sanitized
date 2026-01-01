import { useEffect, useMemo, useRef, useState } from "react";

type Metric = { label: string; value: string };
type MetricPoint = { timestamp: number; value: number };
type Player = { name: string; uuid: string; skin_url: string; position: { x: number; y: number; z: number } };
type Rule = { key: string; value: string };
type CommandTemplate = { name: string; command: string };
type InstanceItem = { name?: string; path?: string };
type MapStatus = { source: string | null; available: Record<string, boolean>; y_min: number; y_max: number; supports_y: boolean };
type MapConfigFile = { name: string; content: string };
type MapConfig = { plugin: string | null; files: MapConfigFile[] };

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
    mapStatus: "Map Status",
    mapSettings: "Map Settings",
    open: "Open",
    close: "Close",
    reload: "Reload",
    overworld: "Overworld",
    nether: "Nether",
    end: "End",
    zoom: "Zoom",
    height: "Y Level",
    refresh: "Refresh (s)",
    mapHint: "Tiles are read-only. Provide tiles via map-tiles/ in instance dir.",
    edit: "Edit",
    save: "Save",
    cancel: "Cancel",
    theme: "Dark / Light",
    language: "\u4e2d\u6587 / EN",
  },
  zh: {
    title: "MC \u9762\u677f",
    dashboard: "\u4eea\u8868\u76d8",
    instances: "\u5b9e\u4f8b\u5217\u8868",
    logs: "\u5b9e\u65f6\u65e5\u5fd7",
    players: "\u73a9\u5bb6\u5217\u8868",
    rules: "\u670d\u52a1\u5668\u89c4\u5219",
    map: "\u4e16\u754c\u5730\u56fe",
    command: "\u6307\u4ee4",
    rcon: "RCON",
    control: "\u63a7\u5236",
    login: "\u767b\u5f55",
    username: "\u8d26\u53f7",
    password: "\u5bc6\u7801",
    templates: "\u5e38\u7528\u6307\u4ee4",
    addTemplate: "\u6dfb\u52a0\u6a21\u677f",
    start: "\u542f\u52a8",
    stop: "\u505c\u6b62",
    restart: "\u91cd\u542f",
    connect: "\u8fde\u63a5",
    disconnect: "\u65ad\u5f00",
    clear: "\u6e05\u7a7a",
    session: "\u5728\u7ebf\u65f6\u957f",
    deop: "\u53d6\u6d88OP",
    tpsTrend: "TPS \u8d8b\u52bf",
    mapStatus: "\u5730\u56fe\u72b6\u6001",
    mapSettings: "\u5730\u56fe\u8bbe\u7f6e",
    open: "\u5c55\u5f00",
    close: "\u6536\u8d77",
    reload: "\u91cd\u8f7d",
    overworld: "\u4e3b\u4e16\u754c",
    nether: "\u5730\u72f1",
    end: "\u672b\u5730",
    zoom: "\u7f29\u653e",
    height: "\u9ad8\u5ea6",
    refresh: "\u5237\u65b0\u95f4\u9694(\u79d2)",
    mapHint: "\u53ea\u8bfb\u74e6\u7247\u3002\u5c06\u74e6\u7247\u653e\u5165\u5b9e\u4f8b\u76ee\u5f55 map-tiles/ \u3002",
    edit: "\u7f16\u8f91",
    save: "\u4fdd\u5b58",
    cancel: "\u53d6\u6d88",
    theme: "\u6df1\u8272 / \u6d45\u8272",
    language: "\u4e2d\u6587 / EN",
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
  const [serverRunning, setServerRunning] = useState<boolean | null>(null);
  const [controlStatus, setControlStatus] = useState("");
  const [mapStatus, setMapStatus] = useState<MapStatus | null>(null);
  const [mapConfig, setMapConfig] = useState<MapConfig | null>(null);
  const [mapConfigOpen, setMapConfigOpen] = useState(false);
  const [mapConfigEditing, setMapConfigEditing] = useState(false);
  const [mapConfigDraft, setMapConfigDraft] = useState<Record<string, string>>({});
  const [mapDimension, setMapDimension] = useState<"overworld" | "nether" | "end">("overworld");
  const [mapZoom, setMapZoom] = useState(0);
  const [mapX, setMapX] = useState(0);
  const [mapZ, setMapZ] = useState(0);
  const [mapY, setMapY] = useState(64);
  const [mapRefreshSec, setMapRefreshSec] = useState(5);
  const [mapTick, setMapTick] = useState(0);

  const t = translations[lang];
  const canControl = role === "owner" || role === "admin";
  const canCommand = role === "owner" || role === "admin" || role === "mod";
  const canRcon = role === "owner" || role === "admin";
  const canManagePlayers = role === "owner" || role === "admin" || role === "mod";
  const canTemplateWrite = role === "owner" || role === "admin";
  const canEditRules = role === "owner" || role === "admin";
  const canEditMapConfig = role === "owner" || role === "admin";

  const formatTimestamp = () => {
    const now = new Date();
    return now.toLocaleTimeString();
  };

  const appendLogLine = (message: string) => {
    const line = `[${formatTimestamp()}] ${message}`;
    setLogLines((prev) => [...prev.slice(-200), line]);
  };

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
        setServerRunning(typeof data.running === "boolean" ? data.running : null);
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
    fetch(`/api/map/status${instanceQuery}`, { headers: authHeader })
      .then((res) => res.json())
      .then((data) => {
        setMapStatus(data);
        if (data && data.available) {
          if (!data.available[mapDimension]) {
            const fallback = data.available.overworld
              ? "overworld"
              : data.available.nether
                ? "nether"
                : data.available.end
                  ? "end"
                  : "overworld";
            setMapDimension(fallback as "overworld" | "nether" | "end");
          }
        }
        if (data && data.supports_y) {
          setMapY((prev) => Math.min(data.y_max, Math.max(data.y_min, prev)));
        }
      })
      .catch(() => {});
    fetch(`/api/map/config${instanceQuery}`, { headers: authHeader })
      .then((res) => res.json())
      .then((data) => {
        setMapConfig(data);
        if (!mapConfigEditing && data?.files) {
          const draft: Record<string, string> = {};
          data.files.forEach((file: MapConfigFile) => {
            draft[file.name] = file.content;
          });
          setMapConfigDraft(draft);
        }
      })
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

  useEffect(() => {
    if (!token) {
      return;
    }
    const interval = window.setInterval(() => {
      setMapTick((tick) => tick + 1);
    }, Math.max(1, mapRefreshSec) * 1000);
    return () => window.clearInterval(interval);
  }, [token, instanceDir, mapRefreshSec]);

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
      appendLogLine(event.data);
    };
    ws.onclose = () => {
      wsRef.current = null;
      setLogConnected(false);
    };
    ws.onerror = () => {
      setLogError("Log stream error");
      appendLogLine("Log stream error");
    };
    ws.onopen = () => {
      setLogConnected(true);
      setLogError("");
      appendLogLine("Log stream connected");
    };
    wsRef.current = ws;
  };

  const disconnectLogs = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setLogConnected(false);
    appendLogLine("Log stream disconnected");
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
          appendLogLine(`> ${command}`);
          appendLogLine(String(response));
        }
      })
      .catch(() => {
        setLogError("Command failed");
        appendLogLine("Command failed");
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
    })
      .then((res) => res.json())
      .then((data) => {
        if (data?.status) {
          setControlStatus(String(data.status));
          appendLogLine(`Control: ${data.status}`);
        }
      })
      .catch(() => {
        setControlStatus("control failed");
        appendLogLine("Control: request failed");
      });
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

  const toggleMapConfig = () => {
    setMapConfigOpen((value) => !value);
  };

  const startEditMapConfig = () => {
    if (!canEditMapConfig) {
      return;
    }
    const draft: Record<string, string> = {};
    mapConfig?.files?.forEach((file) => {
      draft[file.name] = file.content;
    });
    setMapConfigDraft(draft);
    setMapConfigEditing(true);
    setMapConfigOpen(true);
  };

  const cancelEditMapConfig = () => {
    setMapConfigEditing(false);
  };

  const saveMapConfig = () => {
    if (!canEditMapConfig || !mapConfig?.plugin) {
      return;
    }
    const files = Object.keys(mapConfigDraft).map((name) => ({ name, content: mapConfigDraft[name] }));
    fetch("/api/map/config", {
      method: "PUT",
      headers: { "Content-Type": "application/json", ...authHeader },
      body: JSON.stringify({ plugin: mapConfig.plugin, files, instance_dir: instanceDir || undefined }),
    })
      .then((res) => res.json())
      .then((data) => {
        setMapConfig(data);
        setMapConfigEditing(false);
      })
      .catch(() => {});
  };

  const reloadMapPlugin = () => {
    if (!canEditMapConfig) {
      return;
    }
    const query = instanceDir ? `?instance_dir=${encodeURIComponent(instanceDir)}` : "";
    fetch(`/api/map/reload${query}`, { method: "POST", headers: authHeader }).catch(() => {});
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
          <span className={`tag ${serverRunning ? "status-live" : "status-offline"}`}>
            {serverRunning === null ? "UNKNOWN" : serverRunning ? "RUNNING" : "STOPPED"}
          </span>
          {controlStatus ? <span className="tag">{controlStatus}</span> : null}
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

      <section className="section runtime-grid">
        <div className="map-area">
          <h2>{t.map}</h2>
          <div className="map-panel">
            <div className="map-toolbar">
              <div className="map-tabs">
                <button
                  className="btn"
                  disabled={!mapStatus?.available?.overworld}
                  onClick={() => setMapDimension("overworld")}
                >
                  {t.overworld}
                </button>
                <button
                  className="btn"
                  disabled={!mapStatus?.available?.nether}
                  onClick={() => setMapDimension("nether")}
                >
                  {t.nether}
                </button>
                <button className="btn" disabled={!mapStatus?.available?.end} onClick={() => setMapDimension("end")}>
                  {t.end}
                </button>
              </div>
              <div className="map-controls">
                <label>
                  {t.zoom}
                  <input
                    type="range"
                    min="0"
                    max="6"
                    value={mapZoom}
                    onChange={(event) => setMapZoom(Number(event.target.value))}
                  />
                </label>
                <label>
                  {t.height}
                  <input
                    type="range"
                    min={mapStatus?.y_min ?? -64}
                    max={mapStatus?.y_max ?? 320}
                    value={mapY}
                    onChange={(event) => setMapY(Number(event.target.value))}
                  />
                </label>
                <label>
                  {t.refresh}
                  <input
                    type="range"
                    min="1"
                    max="30"
                    value={mapRefreshSec}
                    onChange={(event) => setMapRefreshSec(Number(event.target.value))}
                  />
                  <span>{mapRefreshSec}s</span>
                </label>
              </div>
            </div>
            <div className="map-canvas">
              <img
                alt="map"
                src={`/api/map/tile?dimension=${mapDimension}&x=${mapX}&z=${mapZ}&zoom=${mapZoom}&y=${mapY}&instance_dir=${encodeURIComponent(
                  instanceDir || ""
                )}&tick=${mapTick}`}
              />
            </div>
            <div className="map-pan">
              <button className="btn" onClick={() => setMapZ((value) => value - 1)}>
                Up
              </button>
              <div className="map-pan-row">
                <button className="btn" onClick={() => setMapX((value) => value - 1)}>
                  Left
                </button>
                <button className="btn" onClick={() => setMapX((value) => value + 1)}>
                  Right
                </button>
              </div>
              <button className="btn" onClick={() => setMapZ((value) => value + 1)}>
                Down
              </button>
            </div>
            <div className="map-hint">
              {t.mapStatus}: {mapStatus?.source ?? "none"} - {t.mapHint}
            </div>
            <div className="map-config-actions">
              <button className="btn" onClick={toggleMapConfig}>
                {mapConfigOpen ? t.close : t.open}
              </button>
              <button className="btn" disabled={!canEditMapConfig} onClick={startEditMapConfig}>
                {t.edit}
              </button>
              <button className="btn" disabled={!mapConfigEditing} onClick={saveMapConfig}>
                {t.save}
              </button>
              <button className="btn" disabled={!mapConfigEditing} onClick={cancelEditMapConfig}>
                {t.cancel}
              </button>
              <button className="btn" disabled={!canEditMapConfig} onClick={reloadMapPlugin}>
                {t.reload}
              </button>
            </div>
            {mapConfigOpen ? (
              <div className="map-config">
                <div className="map-config-title">
                  {t.mapSettings} {mapConfig?.plugin ? `(${mapConfig.plugin})` : ""}
                </div>
                {mapConfig?.files?.length ? (
                  mapConfig.files.map((file) => (
                    <div key={file.name} className="map-config-file">
                      <div className="map-config-name">{file.name}</div>
                      {mapConfigEditing ? (
                        <textarea
                          value={mapConfigDraft[file.name] ?? ""}
                          onChange={(event) =>
                            setMapConfigDraft({ ...mapConfigDraft, [file.name]: event.target.value })
                          }
                        />
                      ) : (
                        <pre>{file.content}</pre>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="map-config-empty">No config files found.</div>
                )}
              </div>
            ) : null}
          </div>
        </div>
        <div className="log-area">
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
            <span className={`tag status ${logConnected ? "status-live" : "status-offline"}`}>
              {logConnected ? "LIVE" : "OFFLINE"}
            </span>
          </div>
          <div className="command-bar">
            <input
              value={command}
              onChange={(event) => setCommand(event.target.value)}
              onKeyDown={handleCommandKey}
              placeholder={t.command}
            />
            <div className="command-actions">
              <button className="btn" disabled={!canCommand} onClick={() => sendCommand("/api/command")}>
                {t.command}
              </button>
              <button className="btn" disabled={!canRcon} onClick={() => sendCommand("/api/rcon")}>
                {t.rcon}
              </button>
            </div>
          </div>
        </div>
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
