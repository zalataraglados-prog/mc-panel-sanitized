const $ = (id) => document.getElementById(id);
const output = $('output');
const panelLink = $('panel_link');
const catalogContainer = $('catalog_sections');
const langSelect = $('lang');
const profileSelect = $('profile');
const versionInput = $('version');
const btnApply = $('btn_apply');
const btnPlan = $('btn_plan');
const btnSave = $('btn_save');
let catalogBundle = null;
let progressTimer = null;
let applyHangTimer = null;

const PROFILE_DEFAULTS = {
  beginner: {
    "max-players": "3",
    "view-distance": "4",
    "simulation-distance": "4",
    "docker.env.MEMORY": "2G",
    "online-mode": "true",
    "enable-rcon": "true",
    "enable-query": "false"
  },
  normal: {
    "max-players": "20",
    "view-distance": "8",
    "simulation-distance": "6",
    "docker.env.MEMORY": "2G",
    "online-mode": "true",
    "enable-rcon": "true",
    "enable-query": "false"
  },
  advanced: {
    "max-players": "20",
    "view-distance": "10",
    "simulation-distance": "8",
    "docker.env.MEMORY": "3G",
    "online-mode": "true",
    "enable-rcon": "true",
    "enable-query": "true"
  }
};

const translations = {
  zh: {
    title: 'MCIC 引导向导',
    language: '语言',
    basic: '基础设置',
    versionLabel: '版本（默认 1.21.11）',
    versionPlaceholder: '1.21.11',
    profile: '配置档位',
    profileBeginner: '新手',
    profileNormal: '标准',
    profileAdvanced: '高级',
    otpLabel: '一次性口令（OTP）',
    otpPlaceholder: '',
    otpHint: 'Plan / Apply / 保存需要 OTP。',
    importMode: '导入方式',
    importNone: '不导入',
    importPaste: '粘贴配置串',
    importFile: '从文件路径导入',
    importValue: '配置串 / 文件路径',
    importPlaceholder: '粘贴配置串，或填写文件路径',
    importHint: '若选择“从文件路径导入”，请填写服务器上的文件路径。',
    beginner: '新手选项',
    keepInventory: '死亡不掉落',
    allowCheats: '允许作弊（命令方块）',
    core: '核心参数',
    expectedPlayers: '预期人数',
    expectedPlayersPh: '例如 3',
    maxPlayers: '最大人数',
    maxPlayersPh: '例如 20',
    difficulty: '难度',
    difficultyPeaceful: '和平',
    difficultyEasy: '简单',
    difficultyNormal: '普通',
    difficultyHard: '困难',
    gamemode: '游戏模式',
    gmSurvival: '生存',
    gmCreative: '创造',
    gmAdventure: '冒险',
    gmSpectator: '旁观',
    onlineMode: '在线模式',
    pvp: 'PVP',
    whitelist: '白名单',
    spawnProtection: '出生保护',
    spawnProtectionPh: '例如 16',
    performance: '性能参数',
    memory: '内存（docker.env.MEMORY）',
    memoryPh: '例如 2G / 2048M',
    viewDistance: '视距',
    viewDistancePh: '例如 6',
    simulationDistance: '模拟距离',
    simulationDistancePh: '例如 4',
    randomTick: '随机刻速度',
    randomTickPh: '例如 3',
    maxEntityCramming: '最大实体挤压',
    maxEntityCrammingPh: '例如 24',
    panel: '面板 / 网络 / RCON',
    portCheck: '端口占用检测',
    portCheckBtn: '检测端口',
    portCheckHint: '点击检测常用端口是否被占用。',
    portCheckOk: '可用',
    portCheckBusy: '占用',
    portCheckFail: '检测失败',
    panelEnable: '启用面板',
    panelPort: '面板端口',
    panelPortPh: '15000',
    serverPort: 'MC 端口',
    serverPortPh: '25565',
    rconEnable: '启用 RCON',
    rconPort: 'RCON 端口',
    rconPortPh: '25575',
    map: '地图 / 插件',
    mapPlugin: '地图插件',
    installBluemap: '安装 BlueMap',
    installInvsee: '安装 InvSee++',
    skipInstall: '不安装',
    mapPort: '地图端口',
    mapPortPh: '8100',
    mapInterval: '渲染间隔',
    mapIntervalPh: '5',
    inventoryPlugin: '背包插件',
    advanced: '高级参数（目录）',
    custom: '自定义参数',
    customHint: '额外 key=value（每行一条）',
    customPlaceholder: 'max-players=3\nview-distance=4\nkeepInventory=true',
    customHint2: '将覆盖上方与导入配置中的值。',
    btnPlan: '运行 Plan（评审）',
    btnApply: '执行 Apply',
    btnSave: '保存配置',
    applyNotice: '执行可能需要几分钟到几十分钟，请耐心等待；若长时间无进度会提示日志。',
    output: '输出',
    panelHint: '如已安装主面板：',
    panelLink: '打开面板',
    default: '默认',
    on: '开启',
    off: '关闭',
    catalogLoading: '正在加载参数...',
    applySuccessTitle: '部署已提交',
    applySuccessBody: '服务器已经接收到部署命令。',
    applyFailTitle: '执行失败',
    applyFailBody: '执行失败，请查看输出。',
    applyWarnTitle: '执行超时提醒',
    applyWarnBody: '执行时间过长，请检查输出或 SSH 日志。',
    progressRunning: '执行中',
    progressDone: '已完成',
    progressFailed: '失败'
  },
  en: {
    title: 'MCIC Wizard',
    language: 'Language',
    basic: 'Basics',
    versionLabel: 'Version (default 1.21.11)',
    versionPlaceholder: '1.21.11',
    profile: 'Profile',
    profileBeginner: 'Beginner',
    profileNormal: 'Standard',
    profileAdvanced: 'Advanced',
    otpLabel: 'One-time token (OTP)',
    otpPlaceholder: '',
    otpHint: 'OTP is required for Plan / Apply / Save.',
    importMode: 'Import',
    importNone: 'None',
    importPaste: 'Paste claims string',
    importFile: 'From file path',
    importValue: 'Claims / Path',
    importPlaceholder: 'Paste claims or input file path',
    importHint: 'For file import, use a server-side file path.',
    beginner: 'Beginner',
    keepInventory: 'Keep inventory on death',
    allowCheats: 'Allow cheats (command blocks)',
    core: 'Core',
    expectedPlayers: 'Expected players',
    expectedPlayersPh: 'e.g. 3',
    maxPlayers: 'Max players',
    maxPlayersPh: 'e.g. 20',
    difficulty: 'Difficulty',
    difficultyPeaceful: 'Peaceful',
    difficultyEasy: 'Easy',
    difficultyNormal: 'Normal',
    difficultyHard: 'Hard',
    gamemode: 'Game mode',
    gmSurvival: 'Survival',
    gmCreative: 'Creative',
    gmAdventure: 'Adventure',
    gmSpectator: 'Spectator',
    onlineMode: 'Online mode',
    pvp: 'PVP',
    whitelist: 'Whitelist',
    spawnProtection: 'Spawn protection',
    spawnProtectionPh: 'e.g. 16',
    performance: 'Performance',
    memory: 'Memory (docker.env.MEMORY)',
    memoryPh: 'e.g. 2G / 2048M',
    viewDistance: 'View distance',
    viewDistancePh: 'e.g. 6',
    simulationDistance: 'Simulation distance',
    simulationDistancePh: 'e.g. 4',
    randomTick: 'Random tick speed',
    randomTickPh: 'e.g. 3',
    maxEntityCramming: 'Max entity cramming',
    maxEntityCrammingPh: 'e.g. 24',
    panel: 'Panel / Network / RCON',
    portCheck: 'Port availability',
    portCheckBtn: 'Check ports',
    portCheckHint: 'Check common ports for conflicts.',
    portCheckOk: 'available',
    portCheckBusy: 'in use',
    portCheckFail: 'check failed',
    panelEnable: 'Enable panel',
    panelPort: 'Panel port',
    panelPortPh: '15000',
    serverPort: 'MC port',
    serverPortPh: '25565',
    rconEnable: 'Enable RCON',
    rconPort: 'RCON port',
    rconPortPh: '25575',
    map: 'Map / Plugins',
    mapPlugin: 'Map plugin',
    installBluemap: 'Install BlueMap',
    installInvsee: 'Install InvSee++',
    skipInstall: 'Do not install',
    mapPort: 'Map port',
    mapPortPh: '8100',
    mapInterval: 'Render interval',
    mapIntervalPh: '5',
    inventoryPlugin: 'Inventory plugin',
    advanced: 'Advanced (catalog)',
    custom: 'Custom params',
    customHint: 'Extra key=value lines (one per line)',
    customPlaceholder: 'max-players=3\nview-distance=4\nkeepInventory=true',
    customHint2: 'These override values above and imported claims.',
    btnPlan: 'Run Plan (review)',
    btnApply: 'Run Apply',
    btnSave: 'Save state',
    output: 'Output',
    applyNotice: 'Apply may take minutes to tens of minutes. Please wait.',
    panelHint: 'If panel is installed:',
    panelLink: 'Open panel',
    default: 'Default',
    on: 'On',
    off: 'Off',
    catalogLoading: 'Loading parameters...',
    applySuccessTitle: 'Apply submitted',
    applySuccessBody: 'Server has received the deployment command.',
    applyFailTitle: 'Apply failed',
    applyFailBody: 'Apply failed. Check output for details.',
    applyWarnTitle: 'Apply warning',
    applyWarnBody: 'Apply is taking longer than expected. Check output/logs via SSH.',
    progressRunning: 'Running',
    progressDone: 'Completed',
    progressFailed: 'Failed'
  }
};

function t(key) {
  const lang = langSelect.value || 'zh';
  return (translations[lang] && translations[lang][key]) || translations.zh[key] || key;
}

function applyLang(lang) {
  document.documentElement.lang = lang;
  document.title = t('title');
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    const key = el.getAttribute('data-i18n');
    if (t(key)) el.textContent = t(key);
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
    const key = el.getAttribute('data-i18n-placeholder');
    if (t(key)) el.setAttribute('placeholder', t(key));
  });
}

async function getNonce() {
  const res = await fetch('/api/wizard/nonce');
  if (!res.ok) throw new Error('nonce failed');
  return await res.json();
}

function toHex(buffer) {
  return Array.from(new Uint8Array(buffer)).map(b => b.toString(16).padStart(2, '0')).join('');
}

async function signOtp(otp, nonce, host) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    enc.encode(otp),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  const data = enc.encode(`${nonce}:${host}`);
  const sig = await crypto.subtle.sign('HMAC', key, data);
  return toHex(sig);
}

function applyProfileDefaults(profile, force = false) {
  const defaults = PROFILE_DEFAULTS[profile] || {};
  Object.entries(defaults).forEach(([key, val]) => {
    const el = document.querySelector(`[data-param="${key}"]`);
    if (!el) return;
    if (!force && (el.value || '').trim() !== '') return;
    el.value = val;
  });
}

function sensitivityAllowed(sensitivity, profile) {
  if (!sensitivity) return true;
  const s = String(sensitivity).toLowerCase();
  if (profile === 'beginner') return s === 'novice';
  if (profile === 'normal') return s !== 'expert';
  return true;
}

function buildFieldHtml(key, meta, hint, taxonomy) {
  const type = (meta && meta.type) || 'string';
  const desc = taxonomy ? `${taxonomy.category || ''} ${taxonomy.risk ? '· ' + taxonomy.risk : ''}`.trim() : '';
  if (type === 'bool' || type === 'boolean') {
    return `\n      <div class="field">\n        <label>${key}</label>\n        <select data-param="${key}">\n          <option value="">${t('default')}</option>\n          <option value="true">${t('on')}</option>\n          <option value="false">${t('off')}</option>\n        </select>\n        ${desc ? `<small>${desc}</small>` : ''}\n      </div>`;
  }
  const ph = hint !== undefined && hint !== null ? String(hint) : '';
  return `\n    <div class="field">\n      <label>${key}</label>\n      <input data-param="${key}" placeholder="${ph}" />\n      ${desc ? `<small>${desc}</small>` : ''}\n    </div>`;
}

function renderCatalog() {
  if (!catalogContainer) return;
  catalogContainer.innerHTML = '';
  if (!catalogBundle || !catalogBundle.catalog) {
    catalogContainer.innerHTML = `<div class="hint">${t('catalogLoading')}</div>`;
    return;
  }
  const catalog = catalogBundle.catalog || {};
  const taxonomy = catalogBundle.taxonomy || {};
  const usability = catalogBundle.usability || {};
  const profile = profileSelect.value || 'normal';
  const baseKeys = new Set();
  document.querySelectorAll('[data-param]').forEach((el) => {
    if (el.closest('#catalog_sections')) return;
    baseKeys.add(el.getAttribute('data-param'));
  });

  const sectionOrder = ['server_properties', 'gamerule'];
  sectionOrder.forEach((sectionKey) => {
    const section = catalog[sectionKey];
    if (!section || !section.entries) return;
    const entries = section.entries;
    const rows = [];
    Object.keys(entries).forEach((key) => {
      if (baseKeys.has(key)) return;
      const entryMeta = entries[key] || {};
      const use = (((usability[sectionKey] || {}).entries || {})[key] || {}).usability || {};
      if (use.exposed === false) return;
      const tax = ((taxonomy[sectionKey] || {}).entries || {})[key] || {};
      if (!sensitivityAllowed(tax.sensitivity, profile)) return;
      const hint = (use.default_hint !== undefined ? use.default_hint : entryMeta.default);
      rows.push(buildFieldHtml(key, entryMeta, hint, tax));
    });
    if (!rows.length) return;
    const title = sectionKey;
    const html = `<details open><summary>${title}</summary><div class="grid">${rows.join('')}</div></details>`;
    catalogContainer.innerHTML += html;
  });
}

async function loadCatalog(force = false) {
  const version = (versionInput.value || '1.21.11').trim();
  if (!force && catalogBundle && catalogBundle.version === version) {
    renderCatalog();
    return;
  }
  catalogContainer.innerHTML = `<div class="hint">${t('catalogLoading')}</div>`;
  try {
    const res = await fetch(`/api/wizard/catalog?version=${encodeURIComponent(version)}`);
    if (res.ok) {
      catalogBundle = await res.json();
    } else {
      catalogBundle = null;
    }
  } catch (_) {
    catalogBundle = null;
  }
  renderCatalog();
}

async function loadState() {
  const res = await fetch('/api/wizard/state');
  if (!res.ok) return;
  const data = await res.json();
  versionInput.value = data.version || '1.21.11';
  profileSelect.value = data.profile || 'normal';
  $('import_mode').value = data.import_mode || 'none';
  $('import_value').value = data.import_value || '';
  $('params_extra').value = data.params_text || '';
  if (data.panel_url) panelLink.href = data.panel_url;
  if (data.lang) {
    langSelect.value = data.lang;
  }
  applyLang(langSelect.value || 'zh');
  await loadCatalog(true);
  applyProfileDefaults(profileSelect.value, false);
}

function gather() {
  const params = {};
  document.querySelectorAll('[data-param]').forEach((el) => {
    const key = el.getAttribute('data-param');
    const val = (el.value || '').trim();
    if (val !== '') params[key] = val;
  });
  return {
    version: (versionInput.value || '1.21.11').trim(),
    profile: profileSelect.value,
    otp: $('otp').value.trim(),
    import_mode: $('import_mode').value,
    import_value: $('import_value').value.trim(),
    params: params,
    params_text: $('params_extra').value,
    lang: langSelect.value
  };
}

async function buildHeaders(otp) {
  const headers = { 'Content-Type': 'application/json' };
  const cleanOtp = (otp || '').trim();
  if (!cleanOtp) return headers;
  try {
    const meta = await getNonce();
    const sig = await signOtp(cleanOtp, meta.nonce, meta.host || location.host);
    headers['X-MCIC-NONCE'] = meta.nonce;
    headers['X-MCIC-OTP-SIG'] = sig;
  } catch (_) {
    headers['X-MCIC-OTP'] = cleanOtp;
  }
  return headers;
}

function showModal(title, body) {
  const modal = $('modal');
  $('modal_title').textContent = title;
  $('modal_body').textContent = body;
  $('modal_close').textContent = langSelect.value === 'zh' ? '知道了' : 'OK';
  modal.classList.remove('hidden');
}

$('modal_close').onclick = () => $('modal').classList.add('hidden');

async function saveState() {
  const payload = gather();
  const otp = payload.otp;
  delete payload.otp;
  const headers = await buildHeaders(otp);
  await fetch('/api/wizard/state', { method: 'POST', headers, body: JSON.stringify(payload) });
}

async function runAction(path) {
  output.textContent = langSelect.value === 'zh' ? '运行中...' : 'Running...';
  const payload = gather();
  const otp = payload.otp;
  delete payload.otp;
  const headers = await buildHeaders(otp);
  const res = await fetch(path, { method: 'POST', headers, body: JSON.stringify(payload) });
  const txt = await res.text();
  let data = null;
  try {
    data = JSON.parse(txt);
  } catch (_) {
    data = { error: txt };
  }
  output.textContent = data.output || data.error || txt;
  return { res, data };
}

async function checkPorts() {
  const pick = (el) => {
    const v = (el.value || '').trim();
    if (v) return v;
    const ph = (el.getAttribute('placeholder') || '').trim();
    return ph || '';
  };
  const ports = [];
  document.querySelectorAll('input[data-param="panel.port"],input[data-param="server-port"],input[data-param="rcon.port"],input[data-param="map.plugin_port"]').forEach((el) => {
    const v = pick(el);
    if (v) ports.push(v);
  });
  const resultEl = $('port_check_result');
  if (!ports.length) {
    resultEl.textContent = langSelect.value === 'zh' ? '未填写端口' : 'No ports';
    return;
  }
  const res = await fetch(`/api/wizard/ports?ports=${encodeURIComponent(ports.join(','))}`);
  if (!res.ok) {
    resultEl.textContent = t('portCheckFail');
    return;
  }
  const data = await res.json();
  const free = [];
  const busy = [];
  Object.entries(data.ports || {}).forEach(([p, info]) => {
    if (info && info.free) free.push(p); else busy.push(p);
  });
  resultEl.textContent = `${t('portCheckOk')} ${free.length ? free.join(', ') : '-'} | ${t('portCheckBusy')} ${busy.length ? busy.join(', ') : '-'}`;
}

async function fetchProgress() {
  try {
    const res = await fetch('/api/wizard/progress');
    if (!res.ok) return null;
    return await res.json();
  } catch (_) {
    return null;
  }
}

function startProgress() {
  const wrap = $('apply_progress');
  const fill = $('apply_progress_fill');
  const pct = $('apply_progress_pct');
  const label = $('apply_progress_label');
  wrap.classList.remove('hidden');
  label.textContent = t('progressRunning');
  fill.style.width = '1%';
  pct.textContent = '1%';

  const tick = async () => {
    const data = await fetchProgress();
    if (!data) return;
    const percent = typeof data.percent === 'number' ? data.percent : null;
    if (percent !== null) {
      fill.style.width = `${percent}%`;
      pct.textContent = `${percent}%`;
    }
    const detail = data.detail || data.message;
    if (detail) label.textContent = detail;
  };
  tick();
  progressTimer = setInterval(tick, 1200);
  return {
    stop: (ok) => {
      clearInterval(progressTimer);
      const final = ok ? 100 : 95;
      fill.style.width = `${final}%`;
      pct.textContent = `${final}%`;
      label.textContent = ok ? t('progressDone') : t('progressFailed');
    }
  };
}

async function showHangAlert() {
  let body = t('applyWarnBody');
  try {
    const res = await fetch('/api/wizard/logs?tail=80');
    if (res.ok) {
      const data = await res.json();
      const lines = data.lines || [];
      if (lines.length) body = body + '\n\n' + lines.join('\n');
    }
  } catch (_) {
  }
  showModal(t('applyWarnTitle'), body);
}

$('port_check_btn').onclick = async () => { await checkPorts(); };
btnPlan.onclick = async () => { await runAction('/api/wizard/plan'); };
btnApply.onclick = async () => {
  btnApply.disabled = true;
  btnApply.classList.add('btn-disabled');
  const original = btnApply.textContent;
  btnApply.textContent = langSelect.value === 'zh' ? '???...' : 'Applying...';
  const progress = startProgress();
  if (applyHangTimer) clearTimeout(applyHangTimer);
  applyHangTimer = setTimeout(showHangAlert, 180000);
  try {
    const result = await runAction('/api/wizard/apply');
    const data = result ? result.data : null;
    const ok = data && (data.ok === true || data.ok === 'true');
    if (applyHangTimer) {
      clearTimeout(applyHangTimer);
      applyHangTimer = null;
    }
    progress.stop(ok);
    if (ok) {
      showModal(t('applySuccessTitle'), t('applySuccessBody'));
    } else {
      showModal(t('applyFailTitle'), t('applyFailBody'));
    }
  } catch (_) {
    if (applyHangTimer) {
      clearTimeout(applyHangTimer);
      applyHangTimer = null;
    }
    progress.stop(false);
    showModal(t('applyFailTitle'), t('applyFailBody'));
  } finally {
    btnApply.disabled = false;
    btnApply.classList.remove('btn-disabled');
    btnApply.textContent = original;
  }
};
btnSave.onclick = async () => { await saveState(); output.textContent = 'OK'; };

langSelect.onchange = () => { applyLang(langSelect.value); renderCatalog(); };
profileSelect.onchange = () => { applyProfileDefaults(profileSelect.value, true); renderCatalog(); };
versionInput.onchange = async () => { await loadCatalog(true); };

applyLang('zh');
loadState();

