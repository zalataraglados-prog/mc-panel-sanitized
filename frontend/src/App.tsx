import { useEffect, useMemo, useRef, useState } from "react";
import zhCn from "./assets/zh_cn.json";

type Metric = { label: string; value: string };
type MetricPoint = { timestamp: number; value: number };
type Player = {
  name: string;
  uuid: string;
  skin_url: string;
  position: { x: number; y: number; z: number };
  session_seconds?: number;
  online?: boolean;
  last_seen?: string | null;
};
type BanEntry = {
  name: string;
  uuid?: string | null;
  created?: string | null;
  source?: string | null;
  expires?: string | null;
  reason?: string | null;
};
type Rule = { key: string; value: string };
type CommandTemplate = { name: string; command: string };
type InstanceItem = { name?: string; path?: string };
type MapStatus = { source: string | null; available: Record<string, boolean>; y_min: number; y_max: number; supports_y: boolean };
type MapMeta = {
  source: string | null;
  tile_size: number | null;
  scale: number | null;
  origin: { x: number; z: number } | null;
  start_location?: string | null;
  maps?: { id: string; name?: string }[];
};
type MapConfigFile = { name: string; content: string };
type MapConfig = { plugin: string | null; files: MapConfigFile[] };
type InventoryItem = { slot: number; id: string; count: number };
type UserEntry = { username: string; role: string };
type ResourcePackStatus = { sources: string[]; items: number };

const translations = {
  en: {
    title: "MC Panel",
    dashboard: "Dashboard",
    instances: "Instances",
    deployNewInstance: "Deploy New Instance",
    logs: "Logs",
    players: "Players",
    onlinePlayers: "Online",
    offlinePlayers: "Offline",
    lastSeen: "Last Seen",
    rules: "Server Rules",
    map: "World Map",
    command: "Command",
    commandHint: "Panel: no leading '/' | In-game chat: use '/'",
    commandSuccess: "Command sent",
    commandResponse: "Response",
    commandPlayerOnly: "This command only works in-game. Use /invsee in-game or install OpenInv.",
    commandEmpty: "No response",
    rcon: "RCON",
    control: "Control",
    login: "Login",
    username: "Username",
    password: "Password",
    roleLabel: "Role",
    guest: "guest",
    refreshButton: "Refresh",
    metricsPlayers: "Players",
    metricsTps: "TPS",
    metricsMspt: "MSPT",
    metricsCpu: "CPU",
    metricsMemory: "Memory",
    metricsDisk: "Disk",
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
    opLevel: "OP Level",
    op: "OP",
    kick: "Kick",
    ban: "Ban (Permanent)",
    unban: "Unban",
    teleport: "Teleport",
    teleportTitle: "Teleport Player",
    teleportToCoords: "Teleport to coordinates",
    teleportConfirm: "Teleport",
    teleportCancel: "Cancel",
    coordX: "X",
    coordY: "Y",
    coordZ: "Z",
    tpsTrend: "TPS Trend",
    mapStatus: "Map Status",
    mapView2d: "2D",
    mapView3d: "3D",
    mapSelector: "Map",
    avatarSize: "Avatar Size",
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
    mapHint: "Map preview uses the external viewer (port 8100).",
    mapOpenExternal: "Open Detailed Map (8100)",
    mapPluginMissing: "No map plugin detected.",
    mapPluginMissingDetail: "No map plugin detected. Place tiles in map-tiles/ under the instance directory.",
    mapSourceNone: "none",
    edit: "Edit",
    save: "Save",
    cancel: "Cancel",
    up: "Up",
    down: "Down",
    left: "Left",
    right: "Right",
    theme: "Dark / Light",
    themeDark: "Dark",
    themeLight: "Light",
    themeStyle: "Theme",
    themePixel: "Pixel",
    themeMinimal: "Minimal",
    themeTech: "Tech",
    themeRetro: "Retro",
    language: "\u4e2d\u6587 / EN",
    logout: "Logout",
    inventory: "Inventory",
    inventoryOpen: "Open Inventory",
    inventoryClose: "Close",
    inventoryEmpty: "No inventory data.",
    inventoryEmptyDetail: "Player has no items or data not saved yet.",
    inventoryUnsupported: "Inventory editing requires a compatible plugin.",
    inventoryProvider: "Provider",
    inventoryReadOnly: "Read-only",
    inventoryRequestFailed: "Inventory request failed.",
    inventoryUpdateFailed: "Inventory update failed.",
    inventoryAddItem: "Add Item",
    inventoryRemoveItem: "Remove",
    inventoryTapToAdd: "Click an empty slot to add an item.",
    inventoryCount: "Count",
    resourcePack: "Resource Pack",
    resourcePackUpload: "Upload Pack",
    resourcePackStatus: "Pack Status",
    resourcePackItems: "Items",
    resourcePackSources: "Sources",
    resourcePackEmpty: "No pack detected",
    resourcePackUploadHint: "Upload a zip resource pack to enable mod item icons.",
    bannedPlayers: "Banned",
    banListEmpty: "No banned players",
    users: "Users",
    ownerPanel: "Server Owners",
    ownerSelect: "Select player",
    ownerAdd: "Set Owner",
    ownerRemove: "Remove",
    userName: "Username",
    userRole: "Role",
    userPassword: "Password",
    addUser: "Add User",
    updateUser: "Update",
    deleteUser: "Delete",
    ownerRole: "owner",
    adminRole: "admin",
    modRole: "mod",
    viewerRole: "viewer",
    userDeleteConfirm: "Delete this user?",
    running: "RUNNING",
    stopped: "STOPPED",
    unknown: "UNKNOWN",
    live: "LIVE",
    offline: "OFFLINE",
    loginFailed: "Login failed",
    noData: "No data",
    defaultInstance: "default",
    instancesEmpty: "No instances found or still loading",
    loginRequired: "Please login first",
    logStreamError: "Log stream error",
    logNotFound: "Log file not found",
    logClosed: "Log stream closed",
    logConnected: "Log stream connected",
    logDisconnected: "Log stream disconnected",
    commandFailed: "Command failed",
    controlFailed: "Control request failed",
    mapConfigEmpty: "No config files found.",
    templateName: "name",
    templateCommand: "command",
    exportClaims: "Export Claims",
    exportTitle: "Claims String",
    exportCopy: "Copy",
    rconStatus: "RCON Status",
    rconOk: "RCON OK",
    rconFail: "RCON ERROR",
    tpsUnavailable: "TPS unavailable",
    msptUnavailable: "MSPT unavailable",
  },
  zh: {
    title: "MC \u9762\u677f",
    dashboard: "\u4eea\u8868\u76d8",
    instances: "\u5b9e\u4f8b\u5217\u8868",
    deployNewInstance: "部署新实例",
    logs: "\u5b9e\u65f6\u65e5\u5fd7",
    players: "\u73a9\u5bb6\u5217\u8868",
    onlinePlayers: "\u5728\u7ebf",
    offlinePlayers: "\u79bb\u7ebf",
    lastSeen: "\u4e0a\u6b21\u8bbf\u95ee",
    rules: "\u670d\u52a1\u5668\u89c4\u5219",
    map: "\u4e16\u754c\u5730\u56fe",
    command: "\u6307\u4ee4",
    commandHint: "\u9762\u677f\u6307\u4ee4\u4e0d\u7528\u52a0 / \uff0c\u6e38\u620f\u804a\u5929\u9700\u8981 /",
    commandSuccess: "\u6307\u4ee4\u5df2\u53d1\u9001",
    commandResponse: "\u8fd4\u56de",
    commandPlayerOnly: "\u8be5\u547d\u4ee4\u4ec5\u5728\u6e38\u620f\u5185\u53ef\u7528\uff0c\u8bf7\u6e38\u620f\u5185\u4f7f\u7528 /invsee \uff0c\u6216\u5b89\u88c5 OpenInv\u3002",
    commandEmpty: "\u65e0\u8fd4\u56de",
    rcon: "RCON",
    control: "\u63a7\u5236",
    login: "\u767b\u5f55",
    username: "\u8d26\u53f7",
    password: "\u5bc6\u7801",
    roleLabel: "\u89d2\u8272",
    guest: "\u8bbf\u5ba2",
    refreshButton: "\u5237\u65b0",
    metricsPlayers: "\u73a9\u5bb6",
    metricsTps: "TPS",
    metricsMspt: "MSPT",
    metricsCpu: "CPU",
    metricsMemory: "\u5185\u5b58",
    metricsDisk: "\u78c1\u76d8",
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
    opLevel: "OP \u7b49\u7ea7",
    op: "\u6388\u4e88OP",
    kick: "\u8e22\u51fa",
    ban: "\u6c38\u4e45\u5c01\u7981",
    unban: "\u89e3\u9664\u5c01\u7981",
    teleport: "\u4f20\u9001",
    teleportTitle: "\u4f20\u9001\u73a9\u5bb6",
    teleportToCoords: "\u4f20\u9001\u5230\u5750\u6807",
    teleportConfirm: "\u786e\u8ba4\u4f20\u9001",
    teleportCancel: "\u53d6\u6d88",
    coordX: "X",
    coordY: "Y",
    coordZ: "Z",
    tpsTrend: "TPS \u8d8b\u52bf",
    mapStatus: "\u5730\u56fe\u72b6\u6001",
    mapView2d: "\u4e8c\u7ef4",
    mapView3d: "\u4e09\u7ef4",
    mapSelector: "\u5730\u56fe",
    avatarSize: "\u5934\u50cf\u5927\u5c0f",
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
    mapHint: "\u5730\u56fe\u9884\u89c8\u4f7f\u7528\u5916\u90e8\u5730\u56fe\u9875\uff08\u7aef\u53e3 8100\uff09\u3002",
    mapOpenExternal: "\u6253\u5f00\u8be6\u7ec6\u5730\u56fe\uff088100\uff09",
    mapPluginMissing: "\u672a\u68c0\u6d4b\u5230\u5730\u56fe\u63d2\u4ef6\u3002",
    mapPluginMissingDetail: "\u672a\u68c0\u6d4b\u5230\u5730\u56fe\u63d2\u4ef6\u3002\u8bf7\u5c06\u74e6\u7247\u653e\u5165\u5b9e\u4f8b\u76ee\u5f55 map-tiles/ \u3002",
    mapSourceNone: "\u65e0",
    edit: "\u7f16\u8f91",
    save: "\u4fdd\u5b58",
    cancel: "\u53d6\u6d88",
    up: "\u4e0a",
    down: "\u4e0b",
    left: "\u5de6",
    right: "\u53f3",
    theme: "\u6df1\u8272 / \u6d45\u8272",
    themeDark: "\u6df1\u8272",
    themeLight: "\u6d45\u8272",
    themeStyle: "\u4e3b\u9898",
    themePixel: "\u50cf\u7d20",
    themeMinimal: "\u7b80\u7ea6",
    themeTech: "\u79d1\u6280",
    themeRetro: "\u590d\u53e4",
    language: "\u4e2d\u6587 / EN",
    logout: "\u9000\u51fa\u767b\u5f55",
    inventory: "\u80cc\u5305",
    inventoryOpen: "\u67e5\u770b\u80cc\u5305",
    inventoryClose: "\u5173\u95ed",
    inventoryEmpty: "\u6682\u65e0\u80cc\u5305\u6570\u636e\u3002",
    inventoryEmptyDetail: "\u73a9\u5bb6\u65e0\u7269\u54c1\u6216\u6570\u636e\u5c1a\u672a\u5199\u5165\u3002",
    inventoryUnsupported: "\u80cc\u5305\u7f16\u8f91\u9700\u8981\u76f8\u5bb9\u63d2\u4ef6\u3002",
    inventoryProvider: "\u63d0\u4f9b\u65b9",
    inventoryReadOnly: "\u4ec5\u53ef\u67e5\u770b",
    inventoryRequestFailed: "\u80cc\u5305\u8bf7\u6c42\u5931\u8d25\u3002",
    inventoryUpdateFailed: "\u80cc\u5305\u66f4\u65b0\u5931\u8d25\u3002",
    inventoryAddItem: "\u6dfb\u52a0\u7269\u54c1",
    inventoryRemoveItem: "\u5220\u9664",
    inventoryTapToAdd: "\u70b9\u51fb\u7a7a\u683c\u5b50\u6dfb\u52a0\u7269\u54c1\u3002",
    inventoryCount: "\u6570\u91cf",
    resourcePack: "\u8d44\u6e90\u5305",
    resourcePackUpload: "\u4e0a\u4f20\u8d44\u6e90\u5305",
    resourcePackStatus: "\u8d44\u6e90\u5305\u72b6\u6001",
    resourcePackItems: "\u7269\u54c1\u6570",
    resourcePackSources: "\u6765\u6e90",
    resourcePackEmpty: "\u672a\u68c0\u6d4b\u5230\u8d44\u6e90\u5305",
    resourcePackUploadHint: "\u4e0a\u4f20 zip \u8d44\u6e90\u5305\u4ee5\u517c\u5bb9\u6a21\u7ec4\u7269\u54c1\u56fe\u6807\u3002",
    bannedPlayers: "\u5c01\u7981\u73a9\u5bb6",
    banListEmpty: "\u6682\u65e0\u5c01\u7981\u73a9\u5bb6",
    users: "\u8d26\u53f7\u7ba1\u7406",
    ownerPanel: "\u670d\u4e3b\u680f",
    ownerSelect: "\u9009\u62e9\u73a9\u5bb6",
    ownerAdd: "\u8bbe\u4e3a\u670d\u4e3b",
    ownerRemove: "\u79fb\u9664",
    userName: "\u7528\u6237\u540d",
    userRole: "\u89d2\u8272",
    userPassword: "\u5bc6\u7801",
    addUser: "\u6dfb\u52a0\u7528\u6237",
    updateUser: "\u66f4\u65b0",
    deleteUser: "\u5220\u9664",
    ownerRole: "\u670d\u4e3b",
    adminRole: "\u7ba1\u7406\u5458",
    modRole: "\u7248\u4e3b",
    viewerRole: "\u89c2\u5bdf\u8005",
    userDeleteConfirm: "\u786e\u8ba4\u5220\u9664\u8be5\u7528\u6237\uff1f",
    running: "\u8fd0\u884c\u4e2d",
    stopped: "\u5df2\u505c\u6b62",
    unknown: "\u672a\u77e5",
    live: "\u5728\u7ebf",
    offline: "\u79bb\u7ebf",
    loginFailed: "\u767b\u5f55\u5931\u8d25",
    noData: "\u6682\u65e0\u6570\u636e",
    defaultInstance: "\u9ed8\u8ba4",
    instancesEmpty: "\u672a\u53d1\u73b0\u5b9e\u4f8b\u6216\u4ecd\u5728\u52a0\u8f7d",
    loginRequired: "\u8bf7\u5148\u767b\u5f55",
    logStreamError: "\u5b9e\u65f6\u65e5\u5fd7\u8fde\u63a5\u9519\u8bef",
    logNotFound: "\u672a\u627e\u5230\u65e5\u5fd7\u6587\u4ef6",
    logClosed: "\u5b9e\u65f6\u65e5\u5fd7\u5df2\u5173\u95ed",
    logConnected: "\u5b9e\u65f6\u65e5\u5fd7\u5df2\u8fde\u63a5",
    logDisconnected: "\u5b9e\u65f6\u65e5\u5fd7\u5df2\u65ad\u5f00",
    commandFailed: "\u6307\u4ee4\u53d1\u9001\u5931\u8d25",
    controlFailed: "\u63a7\u5236\u8bf7\u6c42\u5931\u8d25",
    mapConfigEmpty: "\u672a\u627e\u5230\u914d\u7f6e\u6587\u4ef6\u3002",
    templateName: "\u540d\u79f0",
    templateCommand: "\u6307\u4ee4",
    exportClaims: "\u5bfc\u51fa\u914d\u7f6e\u4e32",
    exportTitle: "\u914d\u7f6e\u4e32",
    exportCopy: "\u590d\u5236",
    rconStatus: "RCON\u72b6\u6001",
    rconOk: "RCON\u6b63\u5e38",
    rconFail: "RCON\u5f02\u5e38",
    tpsUnavailable: "TPS\u4e0d\u53ef\u7528",
    msptUnavailable: "MSPT\u4e0d\u53ef\u7528",
  },
};

const ruleLabelMapZh: Record<string, string> = {
  "accepts-transfers": "接受转移",
  "allow-flight": "允许飞行",
  "allow-nether": "允许地狱",
  "broadcast-console-to-ops": "控制台消息广播给OP",
  "broadcast-rcon-to-ops": "RCON消息广播给OP",
  "bug-report-link": "错误报告链接",
  debug: "调试模式",
  difficulty: "难度",
  "enable-command-block": "允许命令方块",
  "enable-jmx-monitoring": "启用JMX监控",
  "enable-query": "启用查询",
  "enable-rcon": "启用RCON",
  "enforce-whitelist": "强制白名单",
  gamemode: "默认游戏模式",
  hardcore: "极限模式",
  "max-players": "最大玩家数",
  motd: "服务器描述",
  "online-mode": "正版验证",
  pvp: "玩家对战",
  "server-ip": "服务器绑定IP",
  "server-port": "服务器端口",
  "simulation-distance": "模拟距离",
  "view-distance": "视距",
  "white-list": "白名单",
  "spawn-monsters": "生成怪物",
  "spawn-protection": "出生点保护",
  "keepInventory": "死亡不掉落",
  "doDaylightCycle": "昼夜循环",
  "doMobSpawning": "生物生成",
  "mobGriefing": "生物破坏方块",
  "randomTickSpeed": "随机刻速度",
  "forgiveDeadPlayers": "死亡玩家不被追杀",
  "doImmediateRespawn": "死亡立即重生",
};

const ruleWordMapZh: Record<string, string> = {
  accept: "接受",
  allow: "允许",
  enable: "启用",
  disable: "禁用",
  max: "最大",
  min: "最小",
  player: "玩家",
  players: "玩家",
  server: "服务器",
  port: "端口",
  online: "在线",
  mode: "模式",
  difficulty: "难度",
  view: "视距",
  distance: "距离",
  simulation: "模拟",
  tick: "刻",
  random: "随机",
  spawn: "生成",
  monsters: "怪物",
  monster: "怪物",
  mob: "生物",
  griefing: "破坏",
  whitelist: "白名单",
  white: "白",
  list: "名单",
  pvp: "PVP",
  rcon: "RCON",
  query: "查询",
  debug: "调试",
  broadcast: "广播",
  console: "控制台",
  ops: "OP",
  bug: "错误",
  report: "报告",
  link: "链接",
  command: "指令",
  block: "方块",
  flight: "飞行",
  nether: "地狱",
  overworld: "主世界",
  end: "末地",
  world: "世界",
  keep: "保留",
  inventory: "背包",
  immediate: "立即",
  respawn: "重生",
  forgive: "宽恕",
  dead: "死亡",
  transfer: "转移",
};


function StatCard({ title, value }: { title: string; value: string }) {
  return (
    <div className="card">
      <div className="card-title">{title}</div>
      <div className="card-value">{value}</div>
    </div>
  );
}

function Sparkline({ points, emptyLabel }: { points: MetricPoint[]; emptyLabel: string }) {
  if (!points.length) {
    return <div className="sparkline-empty">{emptyLabel}</div>;
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
  const [bans, setBans] = useState<BanEntry[]>([]);
  const [rules, setRules] = useState<Rule[]>([]);
  const [rulesDraft, setRulesDraft] = useState<Record<string, string>>({});
  const [rulesEditing, setRulesEditing] = useState(false);
  const [templates, setTemplates] = useState<CommandTemplate[]>([]);
  const [newTemplate, setNewTemplate] = useState({ name: "", command: "" });
  const [token, setToken] = useState("");
  const [role, setRole] = useState("");
  const [authError, setAuthError] = useState("");
  const [lang, setLang] = useState<"en" | "zh">("zh");
  const [dark, setDark] = useState(true);
  const [skin, setSkin] = useState<"pixel" | "minimal" | "tech" | "retro">("minimal");
  const [rconOk, setRconOk] = useState(false);
  const [rconMessage, setRconMessage] = useState("");
  const [logLines, setLogLines] = useState<string[]>([]);
  const [command, setCommand] = useState("");
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [commandStatus, setCommandStatus] = useState("");
  const [commandStatusType, setCommandStatusType] = useState<"" | "ok" | "error">("");
  const [opLevels, setOpLevels] = useState<Record<string, string>>({});
  const [exportOpen, setExportOpen] = useState(false);
  const [exportClaims, setExportClaims] = useState("");
  const [exportParams, setExportParams] = useState<Record<string, unknown> | null>(null);
  const mapImageRef = useRef<HTMLImageElement | null>(null);
  const [mapImageScale, setMapImageScale] = useState(1);
  const wsRef = useRef<WebSocket | null>(null);
  const logRef = useRef<HTMLDivElement | null>(null);
  const [logConnected, setLogConnected] = useState(false);
  const [logError, setLogError] = useState("");
  const [serverRunning, setServerRunning] = useState<boolean | null>(null);
  const [controlStatus, setControlStatus] = useState("");
  const [mapStatus, setMapStatus] = useState<MapStatus | null>(null);
  const [mapMeta, setMapMeta] = useState<MapMeta | null>(null);
  const [mapConfig, setMapConfig] = useState<MapConfig | null>(null);
  const [mapConfigOpen, setMapConfigOpen] = useState(false);
  const [mapConfigEditing, setMapConfigEditing] = useState(false);
  const [mapConfigDraft, setMapConfigDraft] = useState<Record<string, string>>({});
  const [mapDimension, setMapDimension] = useState<"overworld" | "nether" | "end">("overworld");
  const [mapId, setMapId] = useState("");
  const [mapZoom, setMapZoom] = useState(0);
  const [mapX, setMapX] = useState(0);
  const [mapZ, setMapZ] = useState(0);
  const [mapY, setMapY] = useState(64);
  const [mapView, setMapView] = useState<"2d" | "3d">("2d");
  const [mapAvatarSize, setMapAvatarSize] = useState(18);
  const [mapRefreshSec, setMapRefreshSec] = useState(5);
  const [mapTick, setMapTick] = useState(0);
  const [inventoryOpen, setInventoryOpen] = useState(false);
  const [inventoryPlayer, setInventoryPlayer] = useState("");
  const [inventoryItems, setInventoryItems] = useState<InventoryItem[]>([]);
  const [inventoryMessage, setInventoryMessage] = useState("");
  const [inventorySupported, setInventorySupported] = useState(false);
  const [inventoryProvider, setInventoryProvider] = useState("");
  const [inventoryEditable, setInventoryEditable] = useState(false);
  const [inventoryEditing, setInventoryEditing] = useState(false);
  const [inventoryDraft, setInventoryDraft] = useState<InventoryItem[]>([]);
  const [inventorySelectedSlot, setInventorySelectedSlot] = useState<number | null>(null);
  const [resourcePackStatus, setResourcePackStatus] = useState<ResourcePackStatus | null>(null);
  const [resourcePackMessage, setResourcePackMessage] = useState("");
  const [resourcePackUploading, setResourcePackUploading] = useState(false);
  const resourcePackInputRef = useRef<HTMLInputElement | null>(null);
  const [teleportOpen, setTeleportOpen] = useState(false);
  const [teleportTarget, setTeleportTarget] = useState<Player | null>(null);
  const [teleportPos, setTeleportPos] = useState({ x: "", y: "", z: "" });
  const [users, setUsers] = useState<UserEntry[]>([]);
  const [userForm, setUserForm] = useState({ username: "", password: "", role: "viewer" });
  const [owners, setOwners] = useState<string[]>([]);
  const [ownerDraft, setOwnerDraft] = useState("");

  const t = translations[lang];
  const canControl = role === "owner" || role === "admin";
  const canCommand = role === "owner" || role === "admin" || role === "mod";
  const canRcon = role === "owner" || role === "admin";
  const canManagePlayers = role === "owner" || role === "admin" || role === "mod";
  const canTemplateWrite = role === "owner" || role === "admin";
  const fixMojibake = (value: string) => {
    try {
      if (!/[\u00c0-\u00ff]/.test(value)) {
        return value;
      }
      return decodeURIComponent(escape(value));
    } catch {
      return value;
    }
  };
  const formatCoord = (value: number) => {
    if (!Number.isFinite(value)) {
      return "0";
    }
    return Math.round(value).toString();
  };
  const canEditRules = role === "owner" || role === "admin";
  const canEditMapConfig = role === "owner" || role === "admin";
  const canEditUsers = role === "owner";
  const canEditOwners = role === "owner";
  const canViewOwners = role === "owner";
  const canBanPlayers = role === "owner" || role === "admin";
  const canManageResourcePack = role === "owner" || role === "admin";
  const roleLabels: Record<string, string> = {
    owner: t.ownerRole,
    admin: t.adminRole,
    mod: t.modRole,
    viewer: t.viewerRole,
  };
  const mapSupported = mapStatus?.source === "bluemap" || mapStatus?.source === "dynmap";
  const mapSupports3d = mapStatus?.source === "bluemap";
  const inventoryViewItems = inventoryEditing ? inventoryDraft : inventoryItems;
  const inventoryArmorSlots = useMemo(() => [103, 102, 101, 100, -106], []);
  const inventoryBaseRows = useMemo(
    () => [
      Array.from({ length: 9 }, (_, index) => index + 9),
      Array.from({ length: 9 }, (_, index) => index + 18),
      Array.from({ length: 9 }, (_, index) => index + 27),
      Array.from({ length: 9 }, (_, index) => index),
    ],
    []
  );
  const inventoryDisplayRows = useMemo(() => {
    const armorRow: Array<number | null> = [...inventoryArmorSlots, null, null, null, null];
    return [armorRow, ...inventoryBaseRows];
  }, [inventoryArmorSlots, inventoryBaseRows]);
  const inventoryAllowedSlots = useMemo(() => {
    const slots = Array.from({ length: 36 }, (_, index) => index);
    inventoryArmorSlots.forEach((slot) => slots.push(slot));
    return slots;
  }, [inventoryArmorSlots]);
  const inventorySlots = useMemo(() => {
    const slots = new Map<number, InventoryItem>();
    for (const item of inventoryViewItems) {
      slots.set(item.slot, item);
    }
    return slots;
  }, [inventoryViewItems]);
  const inventorySlotLabels: Record<number, string> = {
    103: lang === "zh" ? "头" : "Head",
    102: lang === "zh" ? "胸" : "Chest",
    101: lang === "zh" ? "腿" : "Legs",
    100: lang === "zh" ? "靴" : "Feet",
    [-106]: lang === "zh" ? "副" : "Off",
  };
  const itemNameMapZh = useMemo(() => {
    const map: Record<string, string> = {};
    const source = zhCn as Record<string, string>;
    for (const [key, value] of Object.entries(source)) {
      if (key.startsWith("item.minecraft.")) {
        const id = key.replace("item.minecraft.", "");
        map[id] = value;
      } else if (key.startsWith("block.minecraft.")) {
        const id = key.replace("block.minecraft.", "");
        if (!map[id]) {
          map[id] = value;
        }
      }
    }
    return map;
  }, []);
  const formatItemId = (value: string) => {
    if (!value) {
      return "";
    }
    return value.replace(/^minecraft:/, "");
  };
  const formatItemName = (value: string) => {
    const id = formatItemId(value);
    if (lang === "zh" && itemNameMapZh[id]) {
      return fixMojibake(itemNameMapZh[id]);
    }
    return id.replace(/_/g, " ");
  };
  const resourcePackItemUrl = (value: string) => {
    const name = formatItemId(value);
    if (!name) {
      return "";
    }
    const itemId = value.includes(":") ? value : `minecraft:${name}`;
    const params = new URLSearchParams({ item_id: itemId });
    if (instanceDir) {
      params.set("instance_dir", instanceDir);
    }
    return `/api/resourcepacks/item?${params.toString()}`;
  };
  const itemFallbackUrl = (value: string) => {
    const name = formatItemId(value);
    if (!name) {
      return "";
    }
    return `https://fastly.jsdelivr.net/gh/InventivetalentDev/minecraft-assets@1.21.11/assets/minecraft/textures/item/${name}.png`;
  };
  const itemPlaceholder = `data:image/svg+xml;utf8,${encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32">
      <rect width="100%" height="100%" fill="#1f2937"/>
      <rect x="4" y="4" width="24" height="24" fill="#374151"/>
    </svg>`
  )}`;
  const handleItemIconError = (event: React.SyntheticEvent<HTMLImageElement>, id: string) => {
    const img = event.currentTarget;
    if (img.dataset.fallback === "1") {
      img.dataset.fallback = "2";
      img.src = itemPlaceholder;
      return;
    }
    img.dataset.fallback = "1";
    img.src = itemFallbackUrl(id);
  };
  const avatarPlaceholder = `data:image/svg+xml;utf8,${encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64">
      <rect width="100%" height="100%" fill="#2b3444"/>
      <circle cx="32" cy="26" r="12" fill="#5a6c86"/>
      <rect x="12" y="42" width="40" height="14" rx="7" fill="#3a4b64"/>
    </svg>`
  )}`;
  const buildAvatarUrl = (name: string, uuid: string, size: number, preferred: "minotar" | "crafatar") => {
    if (preferred === "minotar") {
      if (name) {
        return `https://minotar.net/avatar/${encodeURIComponent(name)}/${size}`;
      }
      return `https://minotar.net/avatar/steve/${size}`;
    }
    if (uuid && uuid.includes("-")) {
      return `https://crafatar.com/avatars/${uuid}?size=${size}&overlay`;
    }
    return name ? `https://minotar.net/avatar/${encodeURIComponent(name)}/${size}` : `https://minotar.net/avatar/steve/${size}`;
  };
  const handleAvatarError = (
    event: React.SyntheticEvent<HTMLImageElement>,
    name: string,
    uuid: string,
    size: number
  ) => {
    const img = event.currentTarget;
    const step = Number(img.dataset.fallbackStep || "0");
    if (step === 0) {
      img.dataset.fallbackStep = "1";
      img.src = buildAvatarUrl(name, uuid, size, "minotar");
      return;
    }
    if (step === 1) {
      img.dataset.fallbackStep = "2";
      img.src = buildAvatarUrl(name, uuid, size, "crafatar");
      return;
    }
    img.dataset.fallbackStep = "3";
    img.src = avatarPlaceholder;
  };
  const formatRuleKey = (key: string) => {
    if (lang !== "zh") {
      return key;
    }
    if (ruleLabelMapZh[key]) {
      return fixMojibake(ruleLabelMapZh[key]);
    }
    const tokens = key
      .replace(/[._-]/g, " ")
      .replace(/([a-z])([A-Z])/g, "$1 $2")
      .split(/\s+/)
      .filter(Boolean);
    const translated = tokens.map((token) => {
      const mapped = ruleWordMapZh[token.toLowerCase()] || token;
      return fixMojibake(mapped);
    });
    const unchanged = translated.every((value, index) => value === tokens[index]);
    return unchanged ? key : translated.join("");
  };

  const mapOrigin = mapMeta?.origin;
  const mapTileSize = mapMeta?.tile_size ?? 512;
  const mapScale = mapMeta?.scale ?? 1;
  const mapZoomScale = Math.pow(2, mapZoom);
  const mapTileScale = mapScale * mapZoomScale;
  const mapExternalUrl = useMemo(() => {
    const host = window.location.hostname || "127.0.0.1";
    return `http://${host}:8100/`;
  }, []);
  const mapHash = useMemo(() => {
    const raw = mapMeta?.start_location;
    if (!raw) {
      return "";
    }
    const hash = raw.startsWith("#") ? raw : `#${raw}`;
    const parts = hash.slice(1).split(":");
    if (parts.length === 10) {
      if (mapId) {
        parts[0] = mapId;
      }
      parts[9] = mapView === "2d" ? "flat" : "perspective";
      return `#${parts.join(":")}`;
    }
    return hash;
  }, [mapMeta?.start_location, mapView, mapId]);
  const mapMarkers =
    mapView === "2d" && mapStatus?.source !== "bluemap" && mapOrigin && mapMeta?.tile_size && mapMeta?.scale
      ? players
          .filter((player) => player.online !== false)
          .map((player) => {
            const px = (player.position.x - mapOrigin.x) / mapTileScale - mapX * mapTileSize;
            const pz = (player.position.z - mapOrigin.z) / mapTileScale - mapZ * mapTileSize;
            if (px < 0 || pz < 0 || px > mapTileSize || pz > mapTileSize) {
              return null;
            }
            const size = Math.max(12, mapAvatarSize);
            const left = px * mapImageScale - size / 2;
            const top = pz * mapImageScale - size / 2;
            return (
              <img
                key={`marker-${player.uuid}`}
                className="map-marker"
                src={player.skin_url || buildAvatarUrl(player.name, player.uuid, size, "minotar")}
                title={player.name}
                style={{ left: `${left}px`, top: `${top}px`, width: `${size}px`, height: `${size}px` }}
                alt={player.name}
                referrerPolicy="no-referrer"
                onError={(event) => handleAvatarError(event, player.name, player.uuid, size)}
              />
            );
          })
          .filter((item): item is JSX.Element => Boolean(item))
      : null;

  const appendLogLine = (message: string) => {
    setLogLines((prev) => [...prev.slice(-200), message]);
  };

  useEffect(() => {
    document.body.dataset.theme = dark ? "dark" : "light";
  }, [dark]);

  useEffect(() => {
    document.body.dataset.skin = skin;
  }, [skin]);

  useEffect(() => {
    const storedToken = localStorage.getItem("mc_panel_token") || "";
    const storedRole = localStorage.getItem("mc_panel_role") || "";
    const storedSkin = localStorage.getItem("mc_panel_skin") || "";
    const storedTheme = localStorage.getItem("mc_panel_theme") || "";
    if (storedToken) {
      setToken(storedToken);
      setRole(storedRole);
    }
    if (storedSkin === "pixel" || storedSkin === "minimal" || storedSkin === "tech" || storedSkin === "retro") {
      setSkin(storedSkin);
    }
    if (storedTheme === "light") {
      setDark(false);
    } else if (storedTheme === "dark") {
      setDark(true);
    }
  }, []);

  useEffect(() => {
    if (token) {
      localStorage.setItem("mc_panel_token", token);
      localStorage.setItem("mc_panel_role", role || "");
    } else {
      localStorage.removeItem("mc_panel_token");
      localStorage.removeItem("mc_panel_role");
    }
  }, [token, role]);

  useEffect(() => {
    localStorage.setItem("mc_panel_skin", skin);
  }, [skin]);

  useEffect(() => {
    localStorage.setItem("mc_panel_theme", dark ? "dark" : "light");
  }, [dark]);

  const authHeader = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token]);

  const refreshPrimaryData = () => {
    if (!token) {
      return;
    }
    const instanceQuery = instanceDir ? `?instance_dir=${encodeURIComponent(instanceDir)}` : "";
    fetch(`/api/summary${instanceQuery}`, { headers: authHeader })
      .then((res) => res.json())
      .then((data) => {
        const status = data?.status || {};
        const running = typeof status.running === "boolean" ? status.running : null;
        const tpsValue =
          running && (status.tps ?? 0) > 0 ? String(status.tps) : `${t.noData} (${t.tpsUnavailable})`;
        const msptValue =
          running && (status.mspt ?? 0) > 0 ? String(status.mspt) : `${t.noData} (${t.msptUnavailable})`;
        setMetrics([
          { label: t.metricsPlayers, value: String(status.players ?? 0) },
          { label: t.metricsTps, value: tpsValue },
          { label: t.metricsMspt, value: msptValue },
          { label: t.metricsCpu, value: `${status.cpu_usage ?? 0}%` },
          { label: t.metricsMemory, value: `${status.memory_usage ?? 0}%` },
          { label: t.metricsDisk, value: `${status.disk_usage ?? 0}%` },
        ]);
        setServerRunning(running);
        setRconOk(Boolean(status.rcon_ok));
        setRconMessage(typeof status.rcon_message === "string" ? status.rcon_message : "");
        if (Array.isArray(data?.players)) {
          setPlayers(data.players);
        }
        if (data?.map_status) {
          const mapData = data.map_status;
          setMapStatus(mapData);
          if (mapData.available) {
            if (!mapData.available[mapDimension]) {
              const fallback = mapData.available.overworld
                ? "overworld"
                : mapData.available.nether
                  ? "nether"
                  : mapData.available.end
                    ? "end"
                    : "overworld";
              setMapDimension(fallback as "overworld" | "nether" | "end");
            }
          }
          if (mapData.supports_y) {
            setMapY((prev) => Math.min(mapData.y_max, Math.max(mapData.y_min, prev)));
          }
        }
      })
      .catch(() => {});
    fetch(`/api/map/meta${instanceQuery}`, { headers: authHeader })
      .then((res) => res.json())
      .then((data) => setMapMeta(data))
      .catch(() => {
        setMapMeta(null);
      });
    fetch(`/api/metrics?window=60${instanceDir ? `&instance_dir=${encodeURIComponent(instanceDir)}` : ""}`, {
      headers: authHeader,
    })
      .then((res) => res.json())
      .then((data) => setTpsHistory(data || []))
      .catch(() => {});
  };

  const refreshInstances = () => {
    if (!token) {
      return;
    }
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
  };

  const refreshTemplates = () => {
    if (!token) {
      return;
    }
    fetch("/api/command-templates", { headers: authHeader })
      .then((res) => res.json())
      .then((data) => setTemplates(data.templates || []))
      .catch(() => {});
  };

  const refreshRules = () => {
    if (!token) {
      return;
    }
    const instanceQuery = instanceDir ? `?instance_dir=${encodeURIComponent(instanceDir)}` : "";
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
  };

  const refreshMapConfig = () => {
    if (!token || !mapConfigOpen) {
      return;
    }
    const instanceQuery = instanceDir ? `?instance_dir=${encodeURIComponent(instanceDir)}` : "";
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

  const refreshUsers = () => {
    if (!token) {
      return;
    }
    fetch("/api/users", { headers: authHeader })
      .then((res) => res.json())
      .then((data) => setUsers(data.users || []))
      .catch(() => {});
  };

  const refreshOwners = () => {
    if (!token) {
      return;
    }
    const query = instanceDir ? `?instance_dir=${encodeURIComponent(instanceDir)}` : "";
    fetch(`/api/owners${query}`, { headers: authHeader })
      .then((res) => res.json())
      .then((data) => {
        setOwners(Array.isArray(data.owners) ? data.owners : []);
      })
      .catch(() => {});
  };

  const refreshBans = () => {
    if (!token) {
      return;
    }
    const query = instanceDir ? `?instance_dir=${encodeURIComponent(instanceDir)}` : "";
    fetch(`/api/bans${query}`, { headers: authHeader })
      .then((res) => res.json())
      .then((data) => setBans(data.bans || []))
      .catch(() => {});
  };

  const refreshResourcePacks = () => {
    if (!token) {
      return;
    }
    const query = instanceDir ? `?instance_dir=${encodeURIComponent(instanceDir)}` : "";
    fetch(`/api/resourcepacks/status${query}`, { headers: authHeader })
      .then((res) => res.json())
      .then((data) => setResourcePackStatus(data))
      .catch(() => {});
  };

  const uploadResourcePack = (file: File) => {
    if (!token) {
      return;
    }
    const form = new FormData();
    form.append("file", file);
    const query = instanceDir ? `?instance_dir=${encodeURIComponent(instanceDir)}` : "";
    setResourcePackUploading(true);
    setResourcePackMessage("");
    fetch(`/api/resourcepacks/upload${query}`, {
      method: "POST",
      headers: { ...authHeader },
      body: form,
    })
      .then((res) => res.json())
      .then(() => {
        setResourcePackMessage("");
        refreshResourcePacks();
      })
      .catch(() => setResourcePackMessage(t.controlFailed))
      .finally(() => setResourcePackUploading(false));
  };

  const refreshAll = () => {
    refreshPrimaryData();
    refreshInstances();
    refreshTemplates();
    refreshRules();
    refreshMapConfig();
    refreshUsers();
    refreshOwners();
    refreshBans();
    refreshResourcePacks();
  };

  useEffect(() => {
    if (token) {
      refreshPrimaryData();
      refreshInstances();
      refreshTemplates();
      refreshRules();
      refreshUsers();
      refreshOwners();
      refreshBans();
      refreshResourcePacks();
    }
  }, [token]);

  useEffect(() => {
    if (token) {
      refreshPrimaryData();
      refreshRules();
      refreshOwners();
      refreshBans();
      refreshResourcePacks();
    }
  }, [instanceDir]);

  useEffect(() => {
    if (!mapMeta?.maps?.length) {
      return;
    }
    if (mapId && mapMeta.maps.some((entry) => entry.id === mapId)) {
      return;
    }
    const fallback = mapMeta.maps[0];
    if (fallback) {
      setMapId(fallback.id);
    }
  }, [mapMeta?.maps, mapId]);

  useEffect(() => {
    if (!token) {
      return;
    }
    const interval = window.setInterval(() => {
      refreshPrimaryData();
    }, 10000);
    return () => window.clearInterval(interval);
  }, [token, instanceDir]);

  useEffect(() => {
    if (!token) {
      return;
    }
    const interval = window.setInterval(() => {
      if (!rulesEditing) {
        refreshRules();
      }
    }, 30000);
    return () => window.clearInterval(interval);
  }, [token, instanceDir, rulesEditing]);

  useEffect(() => {
    if (token && mapConfigOpen) {
      refreshMapConfig();
    }
  }, [token, instanceDir, mapConfigOpen]);

  useEffect(() => {
    if (!mapSupports3d && mapView === "3d") {
      setMapView("2d");
    }
  }, [mapSupports3d, mapView]);

  useEffect(() => {
    if (!mapImageRef.current) {
      return;
    }
    const image = mapImageRef.current;
    const updateScale = () => {
      const width = image.clientWidth || 1;
      const natural = image.naturalWidth || width;
      setMapImageScale(width / natural);
    };
    updateScale();
    const observer = new ResizeObserver(updateScale);
    observer.observe(image);
    return () => observer.disconnect();
  }, [mapView, mapTick, mapZoom]);

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
    setAuthError("");
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
        if (!data.token) {
          setAuthError("Login failed");
          return;
        }
        setToken(data.token);
        setRole(data.role || "");
      })
      .catch(() => setAuthError("Login failed"));
  };

  const handleLogout = () => {
    setToken("");
    setRole("");
    setAuthError("");
    setUsers([]);
    setOwners([]);
    setInstances([]);
    setInstanceDir("");
    setPlayers([]);
    setMetrics([]);
    setRules([]);
  };

  const connectLogs = () => {
    if (!token || wsRef.current) {
      return;
    }
    const query = instanceDir ? `&instance_dir=${encodeURIComponent(instanceDir)}` : "";
    const scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const host = window.location.host;
    const ws = new WebSocket(
      `${scheme}://${host}/api/logs/ws?token=${token}${query}&max_lines=200&max_per_second=50`
    );
    ws.onmessage = (event) => {
      const line = String(event.data);
      if (line.toLowerCase().includes("logs not found")) {
        setLogError(t.logNotFound);
      }
      appendLogLine(line);
    };
    ws.onclose = (event) => {
      wsRef.current = null;
      setLogConnected(false);
      if (event) {
        const reason = event.reason ? ` ${event.reason}` : "";
        const detail = `${t.logClosed}: ${event.code}${reason}`;
        setLogError(detail);
        appendLogLine(detail);
      }
    };
    ws.onerror = () => {
      setLogError(t.logStreamError);
      appendLogLine(t.logStreamError);
    };
    ws.onopen = () => {
      setLogConnected(true);
      setLogError("");
      appendLogLine(t.logConnected);
    };
    wsRef.current = ws;
  };

  const disconnectLogs = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setLogConnected(false);
    appendLogLine(t.logDisconnected);
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
    setCommandStatus("");
    setCommandStatusType("");
    fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeader },
      body: JSON.stringify({ command, instance_dir: instanceDir || undefined }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data?.ok === false || data?.error) {
          const message = data.error || t.commandFailed;
          setLogError(message);
          appendLogLine(message);
          setCommandStatus(message);
          setCommandStatusType("error");
          return;
        }
        const response = data.result || data.response;
        const responseText = response ? String(response) : t.commandEmpty;
        if (responseText.includes("only be used by players")) {
          setCommandStatus(t.commandPlayerOnly);
          setCommandStatusType("error");
        } else {
          setCommandStatus(`${t.commandResponse}: ${responseText}`);
          setCommandStatusType("ok");
        }
        if (response) {
          appendLogLine(`> ${command}`);
          appendLogLine(responseText);
        }
      })
      .catch(() => {
        setLogError(t.commandFailed);
        appendLogLine(t.commandFailed);
        setCommandStatus(t.commandFailed);
        setCommandStatusType("error");
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
        setControlStatus(t.controlFailed);
        appendLogLine(`Control: ${t.controlFailed}`);
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
        refreshTemplates();
      })
      .catch(() => {});
  };

  const sendPlayerCommand = (cmd: string) => {
    if (!canManagePlayers) {
      return;
    }
    setCommandStatus("");
    setCommandStatusType("");
    fetch("/api/rcon", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeader },
      body: JSON.stringify({ command: cmd, instance_dir: instanceDir || undefined }),
    })
      .then((res) => res.json())
      .then((data) => {
        const responseText = String(data?.response || "");
        if (data?.ok === false || data?.error) {
          setCommandStatus(data.error || t.commandFailed);
          setCommandStatusType("error");
          appendLogLine(data.error || t.commandFailed);
          return;
        }
        if (responseText) {
          setCommandStatus(`${t.commandResponse}: ${responseText}`);
          setCommandStatusType("ok");
        }
      })
      .catch(() => {});
  };

  const banPlayer = (name: string) => {
    if (!canBanPlayers) {
      return;
    }
    fetch("/api/bans", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeader },
      body: JSON.stringify({ name, instance_dir: instanceDir || undefined }),
    })
      .then((res) => res.json())
      .then((data) => setBans(data.bans || []))
      .catch(() => {});
  };

  const unbanPlayer = (name: string) => {
    if (!canBanPlayers) {
      return;
    }
    const params = new URLSearchParams({ name });
    if (instanceDir) {
      params.set("instance_dir", instanceDir);
    }
    fetch(`/api/bans?${params.toString()}`, {
      method: "DELETE",
      headers: { ...authHeader },
    })
      .then((res) => res.json())
      .then((data) => setBans(data.bans || []))
      .catch(() => {});
  };

  const updateOpLevel = (uuid: string, value: string) => {
    setOpLevels((prev) => ({ ...prev, [uuid]: value }));
  };

  const bannedNames = useMemo(() => {
    return new Set(bans.map((entry) => entry.name.toLowerCase()));
  }, [bans]);
  const ownerPlayers = useMemo(() => {
    if (!owners.length) {
      return [];
    }
    return owners
      .map((name) => players.find((player) => player.name === name) || { name, uuid: name, skin_url: "", online: false })
      .filter(Boolean) as Player[];
  }, [owners, players]);
  const onlinePlayers = useMemo(
    () =>
      players.filter(
        (player) =>
          player.online !== false &&
          !owners.includes(player.name) &&
          !bannedNames.has(player.name.toLowerCase())
      ),
    [players, owners, bannedNames]
  );
  const offlinePlayers = useMemo(
    () =>
      players.filter(
        (player) =>
          player.online === false &&
          !owners.includes(player.name) &&
          !bannedNames.has(player.name.toLowerCase())
      ),
    [players, owners, bannedNames]
  );

  const ownerCandidates = useMemo(() => {
    const names = players.map((player) => player.name);
    return names.filter((name) => !owners.includes(name) && !bannedNames.has(name.toLowerCase()));
  }, [players, owners, bannedNames]);

  const updateOwners = (nextOwners: string[]) => {
    if (!canEditOwners) {
      return;
    }
    fetch("/api/owners", {
      method: "PUT",
      headers: { "Content-Type": "application/json", ...authHeader },
      body: JSON.stringify({ owners: nextOwners, instance_dir: instanceDir || undefined }),
    })
      .then((res) => res.json())
      .then((data) => setOwners(Array.isArray(data.owners) ? data.owners : nextOwners))
      .catch(() => {});
  };

  const addOwner = () => {
    if (!ownerDraft || owners.includes(ownerDraft)) {
      return;
    }
    updateOwners([...owners, ownerDraft]);
    setOwnerDraft("");
  };

  const removeOwner = (name: string) => {
    updateOwners(owners.filter((owner) => owner !== name));
  };

  const openTeleport = (player: Player) => {
    setTeleportTarget(player);
    setTeleportPos({
      x: String(player.position.x),
      y: String(player.position.y),
      z: String(player.position.z),
    });
    setTeleportOpen(true);
  };

  const submitTeleport = () => {
    if (!teleportTarget || !canManagePlayers) {
      return;
    }
    const x = teleportPos.x.trim();
    const y = teleportPos.y.trim();
    const z = teleportPos.z.trim();
    if (!x || !y || !z) {
      return;
    }
    sendPlayerCommand(`tp ${teleportTarget.name} ${x} ${y} ${z}`);
    setTeleportOpen(false);
  };

  const renderPlayerCard = (p: Player, metaPrimary?: string, metaSecondary?: string) => (
    <div key={p.uuid} className="player-card">
      <img
        src={p.skin_url || buildAvatarUrl(p.name, p.uuid, 64, "minotar")}
        alt={p.name}
        referrerPolicy="no-referrer"
        onError={(event) => handleAvatarError(event, p.name, p.uuid, 64)}
      />
      <div>
        <div className="player-name">{p.name}</div>
        {metaPrimary ? <div className="player-meta">{metaPrimary}</div> : null}
        {metaSecondary ? <div className="player-meta">{metaSecondary}</div> : null}
        <div className="player-actions">
          <label className="op-level">
            <span>{t.opLevel}</span>
            <select
              value={opLevels[p.uuid] || "4"}
              onChange={(event) => updateOpLevel(p.uuid, event.target.value)}
              disabled={!canManagePlayers}
            >
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
            </select>
          </label>
          <button className="btn" disabled={!canManagePlayers} onClick={() => sendPlayerCommand(`op ${p.name}`)}>
            {t.op}
          </button>
          <button className="btn" disabled={!canManagePlayers} onClick={() => sendPlayerCommand(`deop ${p.name}`)}>
            {t.deop}
          </button>
          <button className="btn" disabled={!canManagePlayers} onClick={() => sendPlayerCommand(`kick ${p.name}`)}>
            {t.kick}
          </button>
          <button className="btn" disabled={!canBanPlayers} onClick={() => banPlayer(p.name)}>
            {t.ban}
          </button>
          <button className="btn" disabled={!canManagePlayers} onClick={() => openTeleport(p)}>
            {t.teleport}
          </button>
          <button className="btn" disabled={!canManagePlayers} onClick={() => openInventory(p.name)}>
            {t.inventory}
          </button>
        </div>
      </div>
    </div>
  );

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

  const handleExportClaims = () => {
    if (!token) {
      return;
    }
    const query = new URLSearchParams({ format: "min" });
    if (instanceDir) {
      query.set("instance_dir", instanceDir);
    }
    fetch(`/api/claims/export?${query.toString()}`, { headers: authHeader })
      .then((res) => res.json())
      .then((data) => {
        setExportClaims(data.claims_string || "");
        setExportParams(data.params || null);
        setExportOpen(true);
      })
      .catch(() => {});
  };

  const openInventory = (name: string) => {
    if (!canManagePlayers) {
      return;
    }
    const query = new URLSearchParams({ name });
    if (instanceDir) {
      query.set("instance_dir", instanceDir);
    }
    fetch(`/api/players/inventory?${query.toString()}`, { headers: authHeader })
      .then((res) => res.json())
      .then((data) => {
        setInventoryPlayer(name);
        setInventoryItems(data.items || []);
        setInventoryDraft(data.items || []);
        setInventorySupported(Boolean(data.supported));
        setInventoryProvider(data.provider || "");
        setInventoryEditable(Boolean(data.editable));
        setInventoryMessage(data.message || "");
        setInventoryEditing(false);
        setInventoryOpen(true);
      })
      .catch(() => {
        setInventoryPlayer(name);
        setInventoryItems([]);
        setInventoryDraft([]);
        setInventorySupported(false);
        setInventoryProvider("");
        setInventoryEditable(false);
        setInventoryMessage(t.inventoryRequestFailed);
        setInventoryEditing(false);
        setInventoryOpen(true);
      });
  };

  const updateInventoryDraft = (index: number, field: keyof InventoryItem, value: string) => {
    setInventoryDraft((prev) =>
      prev.map((item, idx) => {
        if (idx !== index) {
          return item;
        }
        if (field === "slot" || field === "count") {
          return { ...item, [field]: Number(value) };
        }
        return { ...item, [field]: value };
      })
    );
  };

  const addInventoryItem = () => {
    setInventoryDraft((prev) => {
      const used = new Set(prev.map((item) => item.slot));
      const nextSlot = inventoryAllowedSlots.find((candidate) => !used.has(candidate));
      const slot = nextSlot ?? 0;
      return [...prev, { slot, id: "minecraft:stone", count: 1 }];
    });
  };

  const removeInventoryItem = (index: number) => {
    setInventoryDraft((prev) => prev.filter((_, idx) => idx !== index));
  };

  const getDraftItem = (slot: number) => inventoryDraft.find((item) => item.slot === slot) || null;

  const setDraftItem = (slot: number, next: InventoryItem | null) => {
    setInventoryDraft((prev) => {
      const without = prev.filter((item) => item.slot !== slot);
      if (!next) {
        return without;
      }
      return [...without, next].sort((a, b) => a.slot - b.slot);
    });
  };

  const handleSlotClick = (slot: number) => {
    const existing = getDraftItem(slot);
    if (!existing) {
      const next = { slot, id: "minecraft:stone", count: 1 };
      setDraftItem(slot, next);
    }
    setInventorySelectedSlot(slot);
  };

  const saveInventory = () => {
    if (!inventoryEditable) {
      return;
    }
    fetch("/api/players/inventory", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeader },
      body: JSON.stringify({
        player: inventoryPlayer,
        items: inventoryDraft,
        instance_dir: instanceDir || undefined,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        setInventoryMessage(data.message || "Inventory updated.");
        setInventoryItems(inventoryDraft);
        setInventoryEditing(false);
      })
      .catch(() => {
        setInventoryMessage(t.inventoryUpdateFailed);
      });
  };

  const createUser = () => {
    if (!canEditUsers || !userForm.username.trim() || !userForm.password.trim()) {
      return;
    }
    fetch("/api/users", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeader },
      body: JSON.stringify(userForm),
    })
      .then((res) => res.json())
      .then(() => {
        setUserForm({ username: "", password: "", role: "viewer" });
        refreshUsers();
      })
      .catch(() => {});
  };

  const updateUser = (username: string, roleValue: string) => {
    if (!canEditUsers) {
      return;
    }
    fetch(`/api/users/${encodeURIComponent(username)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json", ...authHeader },
      body: JSON.stringify({ role: roleValue }),
    })
      .then((res) => res.json())
      .then(() => refreshUsers())
      .catch(() => {});
  };

  const deleteUser = (username: string) => {
    if (!canEditUsers) {
      return;
    }
    if (!window.confirm(t.userDeleteConfirm)) {
      return;
    }
    fetch(`/api/users/${encodeURIComponent(username)}`, {
      method: "DELETE",
      headers: { ...authHeader },
    })
      .then(() => refreshUsers())
      .catch(() => {});
  };

  return (
    <div className="page">
      <header className="header">
        <h1>{t.title}</h1>
        <div className="actions">
          <label className="select-inline">
            <span>{t.themeStyle}</span>
            <select value={skin} onChange={(event) => setSkin(event.target.value as typeof skin)}>
              <option value="pixel">{t.themePixel}</option>
              <option value="minimal">{t.themeMinimal}</option>
              <option value="tech">{t.themeTech}</option>
              <option value="retro">{t.themeRetro}</option>
            </select>
          </label>
          <button className="btn" onClick={() => setDark((value) => !value)}>
            {dark ? t.themeDark : t.themeLight}
          </button>
          <button className="btn" onClick={() => setLang((value) => (value === "en" ? "zh" : "en"))}>
            {t.language}
          </button>
          {token ? (
            <button className="btn" onClick={handleLogout}>
              {t.logout}
            </button>
          ) : null}
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
          {authError ? <div className="tag">{t.loginFailed}</div> : null}
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
          <Sparkline points={tpsHistory} emptyLabel={t.noData} />
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
          <span className="tag">
            {t.roleLabel}: {role || t.guest}
          </span>
          <span className={`tag ${serverRunning ? "status-live" : "status-offline"}`}>
            {serverRunning === null ? t.unknown : serverRunning ? t.running : t.stopped}
          </span>
          <span className={`tag ${rconOk ? "status-live" : "status-offline"}`}>
            {rconOk ? t.rconOk : t.rconFail}
          </span>
          {controlStatus ? <span className="tag">{controlStatus}</span> : null}
        </div>
        {rconOk ? null : (
          <div className="subtle">
            {t.rconStatus}: {rconMessage || t.rconFail}
          </div>
        )}
      </section>
      <section className="section">
        <h2>{t.players}</h2>
        {ownerPlayers.length || canEditOwners ? (
          <div className="player-owners">
            <span className="player-owners-label">{t.ownerPanel}</span>
            {ownerPlayers.length ? (
              canViewOwners ? (
                ownerPlayers.map((owner) => (
                  <span key={owner.uuid} className="tag owner-tag">
                    {owner.name}
                    {canEditOwners ? (
                      <button
                        type="button"
                        className="owner-remove"
                        onClick={() => removeOwner(owner.name)}
                      >
                        {t.ownerRemove}
                      </button>
                    ) : null}
                  </span>
                ))
              ) : (
                ownerPlayers.map((owner) => (
                  <span
                    key={owner.uuid}
                    className={`tag ${owner.online === false ? "status-offline" : "status-live"}`}
                  >
                    {owner.name} · {owner.online === false ? t.offline : t.live}
                  </span>
                ))
              )
            ) : (
              <span className="tag">{t.noData}</span>
            )}
            {canEditOwners ? (
              <div className="player-owners-controls">
                <select
                  value={ownerDraft}
                  onChange={(event) => setOwnerDraft(event.target.value)}
                >
                  <option value="">{t.ownerSelect}</option>
                  {ownerCandidates.map((name) => (
                    <option key={name} value={name}>
                      {name}
                    </option>
                  ))}
                </select>
                <button className="btn" disabled={!ownerDraft} onClick={addOwner}>
                  {t.ownerAdd}
                </button>
              </div>
            ) : null}
          </div>
        ) : null}
        {canViewOwners ? (
          <div className="players owners-list">
            {ownerPlayers.map((p) =>
              renderPlayerCard(
                p,
                p.online === false ? `${t.lastSeen}: ${p.last_seen || "-"}` : `${formatCoord(p.position.x)},${formatCoord(p.position.y)},${formatCoord(p.position.z)}`,
                p.online === false ? undefined : `${t.session}: ${Math.floor(p.session_seconds || 0)}s`
              )
            )}
            {!ownerPlayers.length ? <div className="subtle">{t.noData}</div> : null}
          </div>
        ) : null}
        <div className="players-split">
          <div className="players-column">
            <div className="players-heading">
              <span>{t.onlinePlayers}</span>
              <span className="players-heading-meta">{t.session}</span>
            </div>
            <div className="players">
              {onlinePlayers.map((p) =>
                renderPlayerCard(
                  p,
                  `${formatCoord(p.position.x)},${formatCoord(p.position.y)},${formatCoord(p.position.z)}`,
                  `${t.session}: ${Math.floor(p.session_seconds || 0)}s`
                )
              )}
              {!onlinePlayers.length ? <div className="subtle">{t.noData}</div> : null}
            </div>
          </div>
          <div className="players-column">
            <div className="players-heading">
              <span>{t.offlinePlayers}</span>
              <span className="players-heading-meta">{t.lastSeen}</span>
            </div>
            <div className="players">
              {offlinePlayers.map((p) => renderPlayerCard(p, `${t.lastSeen}: ${p.last_seen || "-"}`))}
              {!offlinePlayers.length ? <div className="subtle">{t.noData}</div> : null}
            </div>
          </div>
          <div className="players-column">
            <div className="players-heading">
              <span>{t.bannedPlayers}</span>
              <span className="players-heading-meta">{canBanPlayers ? t.unban : ""}</span>
            </div>
            <div className="players">
              {bans.map((entry) => {
                const related = players.find((player) => player.name === entry.name);
                return (
                  <div key={`ban-${entry.name}`} className="player-card">
                    {related ? (
                      <img
                        src={related.skin_url || buildAvatarUrl(related.name, related.uuid, 64, "minotar")}
                        alt={entry.name}
                        referrerPolicy="no-referrer"
                        onError={(event) => handleAvatarError(event, related.name, related.uuid, 64)}
                      />
                    ) : null}
                    <div>
                      <div className="player-name">{entry.name}</div>
                      {entry.reason ? <div className="player-meta">{entry.reason}</div> : null}
                      <div className="player-actions">
                        <button className="btn" disabled={!canBanPlayers} onClick={() => unbanPlayer(entry.name)}>
                          {t.unban}
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
              {!bans.length ? <div className="subtle">{t.banListEmpty}</div> : null}
            </div>
          </div>
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
          <button className="btn" onClick={handleExportClaims}>
            {t.exportClaims}
          </button>
        </div>
        <div className="rules">
          {rules.map((r) => (
            <div key={r.key} className="rule-row">
              <div className="rule-key">
                <div>{formatRuleKey(r.key)}</div>
                {lang === "zh" && ruleLabelMapZh[r.key] ? <div className="rule-key-sub">{r.key}</div> : null}
              </div>
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
          <div className="map-panel map-external-panel">
            <div className="map-canvas map-external-canvas">
              <iframe
                className="map-iframe"
                title="map-preview"
                src={mapExternalUrl}
                loading="lazy"
              />
            </div>
            <div className="map-hint">
              {mapStatus?.source ? t.mapHint : t.mapPluginMissingDetail}
            </div>
            <div className="map-config-actions">
              <a className="btn" href={mapExternalUrl} target="_blank" rel="noreferrer">
                {t.mapOpenExternal}
              </a>
            </div>
            <div className="resourcepack-panel">
              <div className="resourcepack-header">
                <div className="resourcepack-title">{t.resourcePack}</div>
                <div className="resourcepack-actions">
                  <button
                    className="btn"
                    disabled={!canManageResourcePack || resourcePackUploading}
                    onClick={() => resourcePackInputRef.current?.click()}
                  >
                    {t.resourcePackUpload}
                  </button>
                  <input
                    ref={resourcePackInputRef}
                    type="file"
                    accept=".zip"
                    style={{ display: "none" }}
                    onChange={(event) => {
                      const file = event.target.files?.[0];
                      if (file) {
                        uploadResourcePack(file);
                      }
                      event.currentTarget.value = "";
                    }}
                  />
                </div>
              </div>
              <div className="resourcepack-meta">
                {resourcePackStatus ? (
                  <>
                    <span className="tag">
                      {t.resourcePackItems}: {resourcePackStatus.items}
                    </span>
                    <span className="tag">
                      {t.resourcePackSources}: {resourcePackStatus.sources.length}
                    </span>
                  </>
                ) : (
                  <span className="tag">{t.resourcePackEmpty}</span>
                )}
              </div>
              {resourcePackMessage ? <div className="console-error">{resourcePackMessage}</div> : null}
              <div className="subtle">{t.resourcePackUploadHint}</div>
            </div>
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
              {logConnected ? t.live : t.offline}
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
            <div className="command-hint">{t.commandHint}</div>
            {commandStatus ? (
              <div className={`command-feedback ${commandStatusType}`}>{commandStatus}</div>
            ) : null}
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
              placeholder={t.templateName}
            />
            <input
              value={newTemplate.command}
              onChange={(event) => setNewTemplate({ ...newTemplate, command: event.target.value })}
              placeholder={t.templateCommand}
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
        {!token ? <div className="tag">{t.loginRequired}</div> : null}
        {token && instances.length === 0 ? <div className="tag">{t.instancesEmpty}</div> : null}
        <div className="instance-select">
          <select value={instanceDir} onChange={(event) => setInstanceDir(event.target.value)}>
            <option value="">{t.defaultInstance}</option>
            {instances.map((item) => (
              <option key={item.path || item.name} value={item.path || ""}>
                {item.name || item.path}
              </option>
            ))}
          </select>
          <button className="btn" onClick={refreshAll}>
            {t.refreshButton}
          </button>
          <button className="btn secondary" onClick={() => {
            const host = window.location.hostname;
            const protocol = window.location.protocol || 'http:';
            const wizardUrl = `${protocol}//${host}:15001/`;
            window.open(wizardUrl, '_blank', 'noopener,noreferrer');
          }}>
            {t.deployNewInstance}
          </button>
        </div>
        <ul>
          {instances.map((item) => (
            <li key={item.path || item.name}>{item.name || item.path}</li>
          ))}
        </ul>
      </section>

      <section className="section">
        <h2>{t.users}</h2>
        <div className="users-panel">
          <div className="user-form">
            <input
              value={userForm.username}
              onChange={(event) => setUserForm({ ...userForm, username: event.target.value })}
              placeholder={t.userName}
            />
            <input
              value={userForm.password}
              onChange={(event) => setUserForm({ ...userForm, password: event.target.value })}
              placeholder={t.userPassword}
              type="password"
            />
            <select
              value={userForm.role}
              onChange={(event) => setUserForm({ ...userForm, role: event.target.value })}
            >
              <option value="owner">{t.ownerRole}</option>
              <option value="admin">{t.adminRole}</option>
              <option value="mod">{t.modRole}</option>
              <option value="viewer">{t.viewerRole}</option>
            </select>
            <button className="btn" disabled={!canEditUsers} onClick={createUser}>
              {t.addUser}
            </button>
          </div>
          <div className="user-list">
            {users.map((entry) => (
              <div key={entry.username} className="user-row">
                <span>{entry.username}</span>
                <select
                  value={entry.role}
                  disabled={!canEditUsers}
                  onChange={(event) => updateUser(entry.username, event.target.value)}
                >
                  <option value="owner">{t.ownerRole}</option>
                  <option value="admin">{t.adminRole}</option>
                  <option value="mod">{t.modRole}</option>
                  <option value="viewer">{t.viewerRole}</option>
                </select>
                <span className="tag">{roleLabels[entry.role] || entry.role}</span>
                <button className="btn" disabled={!canEditUsers} onClick={() => deleteUser(entry.username)}>
                  {t.deleteUser}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {inventoryOpen ? (
        <div className="modal-overlay" onClick={() => setInventoryOpen(false)}>
          <div className="modal" onClick={(event) => event.stopPropagation()}>
            <div className="modal-header">
              <h3>
                {t.inventory} - {inventoryPlayer}
              </h3>
              <button className="btn" onClick={() => setInventoryOpen(false)}>
                {t.inventoryClose}
              </button>
            </div>
            <div className="rules-actions">
              {inventoryProvider ? (
                <span className="tag">
                  {t.inventoryProvider}: {inventoryProvider}
                </span>
              ) : null}
              {!inventoryEditable ? <span className="tag">{t.inventoryReadOnly}</span> : null}
              {inventoryEditable ? (
                <button className="btn" onClick={() => setInventoryEditing((value) => !value)}>
                  {t.edit}
                </button>
              ) : null}
              {inventoryEditable ? (
                <button className="btn" disabled={!inventoryEditing} onClick={saveInventory}>
                  {t.save}
                </button>
              ) : null}
              {inventoryEditing ? (
                <button className="btn" onClick={addInventoryItem}>
                  {t.inventoryAddItem}
                </button>
              ) : null}
            </div>
            {!inventorySupported ? (
              <p>{inventoryMessage || t.inventoryUnsupported}</p>
            ) : inventoryItems.length ? (
              inventoryEditing ? (
                <div className="inventory-edit">
                  <div className="subtle">{t.inventoryTapToAdd}</div>
                  <div className="inventory-grid inventory-grid-slots">
                    {inventoryDisplayRows.map((row, rowIndex) => (
                      <div key={`inv-row-${rowIndex}`} className="inventory-row">
                        {row.map((slot, slotIndex) => {
                          if (slot === null) {
                            return (
                              <div
                                key={`slot-null-${rowIndex}-${slotIndex}`}
                                className="inventory-slot-cell disabled"
                              />
                            );
                          }
                          const item = inventorySlots.get(slot) || null;
                          const selected = inventorySelectedSlot === slot;
                          const label = inventorySlotLabels[slot] ?? String(slot);
                          return (
                            <div
                              key={`slot-${slot}`}
                              className={`inventory-slot-cell${item ? " filled" : ""}${selected ? " selected" : ""}`}
                              onClick={() => handleSlotClick(slot)}
                            >
                              <div className="inventory-slot-index">{label}</div>
                              {item ? (
                                <div className="inventory-slot-content">
                                  <img
                                    className="inventory-slot-icon"
                                    src={resourcePackItemUrl(item.id)}
                                    alt={formatItemId(item.id)}
                                    onError={(event) => handleItemIconError(event, item.id)}
                                  />
                                  <div className="inventory-slot-id">{formatItemName(item.id)}</div>
                                  <div className="inventory-slot-count">{item.count > 1 ? `x${item.count}` : ""}</div>
                                </div>
                              ) : null}
                            </div>
                          );
                        })}
                      </div>
                    ))}
                  </div>
                  {inventorySelectedSlot !== null ? (
                    (() => {
                      const slot = inventorySelectedSlot;
                      const item = getDraftItem(slot);
                      if (!item) {
                        return null;
                      }
                      return (
                        <div className="inventory-editor">
                          <div className="inventory-editor-title">
                            {t.inventory} #{slot}
                          </div>
                          <label>
                            ID
                            <input
                              value={item.id}
                              onChange={(event) => setDraftItem(slot, { ...item, id: event.target.value })}
                            />
                          </label>
                          <label>
                            {t.inventoryCount}
                            <input
                              type="number"
                              value={item.count}
                              onChange={(event) => setDraftItem(slot, { ...item, count: Number(event.target.value) })}
                            />
                          </label>
                          <div className="inventory-editor-actions">
                            <button className="btn" onClick={() => setDraftItem(slot, null)}>
                              {t.inventoryRemoveItem}
                            </button>
                          </div>
                        </div>
                      );
                    })()
                  ) : null}
                </div>
              ) : (
                <div className="inventory-grid inventory-grid-slots">
                  {inventoryDisplayRows.map((row, rowIndex) => (
                    <div key={`inv-row-${rowIndex}`} className="inventory-row">
                      {row.map((slot, slotIndex) => {
                        if (slot === null) {
                          return (
                            <div
                              key={`slot-null-view-${rowIndex}-${slotIndex}`}
                              className="inventory-slot-cell disabled"
                            />
                          );
                        }
                        const item = inventorySlots.get(slot) || null;
                        const label = inventorySlotLabels[slot] ?? String(slot);
                        return (
                          <div key={`slot-${slot}`} className={`inventory-slot-cell${item ? " filled" : ""}`}>
                            <div className="inventory-slot-index">{label}</div>
                            {item ? (
                              <div className="inventory-slot-content">
                                <img
                                  className="inventory-slot-icon"
                                  src={resourcePackItemUrl(item.id)}
                                  alt={formatItemId(item.id)}
                                  onError={(event) => handleItemIconError(event, item.id)}
                                />
                                <div className="inventory-slot-id">{formatItemName(item.id)}</div>
                                <div className="inventory-slot-count">{item.count > 1 ? `x${item.count}` : ""}</div>
                              </div>
                            ) : null}
                          </div>
                        );
                      })}
                    </div>
                  ))}
                </div>
              )
            ) : (
              <p>{inventoryMessage || t.inventoryEmptyDetail}</p>
            )}
          </div>
        </div>
      ) : null}

      {teleportOpen && teleportTarget ? (
        <div className="modal-overlay" onClick={() => setTeleportOpen(false)}>
          <div className="modal" onClick={(event) => event.stopPropagation()}>
            <div className="modal-header">
              <h3>{t.teleportTitle}</h3>
              <button className="btn" onClick={() => setTeleportOpen(false)}>
                {t.teleportCancel}
              </button>
            </div>
            <div className="modal-subtitle">
              {teleportTarget.name} · {t.teleportToCoords}
            </div>
            <div className="modal-grid">
              <label>
                {t.coordX}
                <input
                  value={teleportPos.x}
                  onChange={(event) => setTeleportPos({ ...teleportPos, x: event.target.value })}
                />
              </label>
              <label>
                {t.coordY}
                <input
                  value={teleportPos.y}
                  onChange={(event) => setTeleportPos({ ...teleportPos, y: event.target.value })}
                />
              </label>
              <label>
                {t.coordZ}
                <input
                  value={teleportPos.z}
                  onChange={(event) => setTeleportPos({ ...teleportPos, z: event.target.value })}
                />
              </label>
            </div>
            <div className="modal-actions">
              <button className="btn" onClick={() => setTeleportOpen(false)}>
                {t.teleportCancel}
              </button>
              <button className="btn" disabled={!canManagePlayers} onClick={submitTeleport}>
                {t.teleportConfirm}
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {exportOpen ? (
        <div className="modal-overlay" onClick={() => setExportOpen(false)}>
          <div className="modal" onClick={(event) => event.stopPropagation()}>
            <div className="modal-header">
              <h3>{t.exportTitle}</h3>
              <button className="btn" onClick={() => setExportOpen(false)}>
                {t.close}
              </button>
            </div>
            <div className="modal-subtitle">{instanceDir || t.defaultInstance}</div>
            <div className="modal-grid">
              <label>
                {t.exportTitle}
                <textarea
                  rows={4}
                  value={exportClaims}
                  readOnly
                  onFocus={(event) => event.currentTarget.select()}
                />
              </label>
            </div>
            {exportParams ? (
              <pre className="modal-pre">{JSON.stringify(exportParams, null, 2)}</pre>
            ) : null}
            <div className="modal-actions">
              <button className="btn" onClick={() => setExportOpen(false)}>
                {t.close}
              </button>
              <button
                className="btn"
                onClick={() => {
                  if (exportClaims) {
                    navigator.clipboard.writeText(exportClaims).catch(() => {});
                  }
                }}
              >
                {t.exportCopy}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
