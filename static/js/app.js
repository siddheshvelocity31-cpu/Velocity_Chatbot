// ============================================================
// Gemini AI Chatbot - Frontend App Logic
// ============================================================

const API = {
  chat:       '/api/chat',
  newSession: '/api/session/new',
  history:    '/api/history',
  loadSess:   '/api/history/load',
  deleteSess: '/api/history/delete',
  saveSess:   '/api/history/save',
  testSupa:   '/api/supabase/test',
  models:     '/api/models',
  tools:      '/api/tools',
};

// ─── State ────────────────────────────────────────────────────────────────────
let state = {
  sessionId:    '',
  messages:     [],
  isTyping:     false,
  apiKey:       localStorage.getItem('gemini_api_key') || '',
  model:        localStorage.getItem('gemini_model') || 'gemini-3.5-flash',
  supabaseUrl:  localStorage.getItem('supabase_url') || '',
  supabaseKey:  localStorage.getItem('supabase_key') || '',
};

// ─── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  state.sessionId = 'chat_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);

  // Restore settings to inputs
  document.getElementById('apiKeyInput').value  = state.apiKey;
  document.getElementById('supaUrlInput').value = state.supabaseUrl;
  document.getElementById('supaKeyInput').value = state.supabaseKey;

  await loadModels();
  await loadTools();
  await loadHistory();

  // Input auto-resize
  const inp = document.getElementById('msgInput');
  inp.addEventListener('input', () => {
    inp.style.height = 'auto';
    inp.style.height = Math.min(inp.scrollHeight, 140) + 'px';
  });
  inp.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });

  // Settings change handlers
  document.getElementById('apiKeyInput').addEventListener('change',  e => { state.apiKey = e.target.value.trim(); localStorage.setItem('gemini_api_key', state.apiKey); });
  document.getElementById('supaUrlInput').addEventListener('change', e => { state.supabaseUrl = e.target.value.trim(); localStorage.setItem('supabase_url', state.supabaseUrl); });
  document.getElementById('supaKeyInput').addEventListener('change', e => { state.supabaseKey = e.target.value.trim(); localStorage.setItem('supabase_key', state.supabaseKey); });
  document.getElementById('modelSelect').addEventListener('change',  e => { state.model = e.target.value; localStorage.setItem('gemini_model', state.model); document.getElementById('modelBadge').textContent = state.model; });
});

// ─── API Helpers ──────────────────────────────────────────────────────────────
async function post(url, body) {
  const r = await fetch(url, { method: 'POST', headers: {'Content-Type':'application/json'}, credentials: 'include', body: JSON.stringify(body) });
  const text = await r.text();
  if (!r.ok) {
    throw new Error(`HTTP ${r.status}: ${text.substring(0, 150)}`);
  }
  try {
    return JSON.parse(text);
  } catch(err) {
    throw new Error(`Non-JSON response: ${text.substring(0, 150)}`);
  }
}

// ─── Load Models ─────────────────────────────────────────────────────────────
async function loadModels() {
  try {
    const data = await fetch(API.models).then(r => r.json());
    const sel = document.getElementById('modelSelect');
    sel.innerHTML = '';
    (data.models || []).forEach(m => {
      const opt = document.createElement('option');
      opt.value = m; opt.textContent = m;
      if (m === state.model) opt.selected = true;
      sel.appendChild(opt);
    });
    document.getElementById('modelBadge').textContent = state.model;
  } catch(e) {}
}

// ─── Load Tools ──────────────────────────────────────────────────────────────
async function loadTools() {
  try {
    const data = await fetch(API.tools).then(r => r.json());
    const wrap = document.getElementById('toolsList');
    wrap.innerHTML = '';
    (data.tools || []).forEach(t => {
      const pill = document.createElement('span');
      pill.className = 'tool-pill';
      pill.textContent = (t.icon || '') + ' ' + (t.name || t);
      wrap.appendChild(pill);
    });
  } catch(e) {}
}

// ─── Load History ─────────────────────────────────────────────────────────────
async function loadHistory() {
  try {
    const data = await post(API.history, { supabase_url: state.supabaseUrl, supabase_key: state.supabaseKey });
    const list = document.getElementById('historyList');
    list.innerHTML = '';
    const sessions = data.sessions || [];
    if (!sessions.length) {
      list.innerHTML = '<div class="no-history">No previous chats</div>';
      return;
    }
    const badge = document.getElementById('storageBadge');
    if (badge) badge.textContent = data.source === 'supabase' ? '☁️ Supabase' : '💾 Local';
    sessions.forEach(s => {
      const item = document.createElement('div');
      item.className = 'history-item' + (s.session_id === state.sessionId ? ' active' : '');
      item.innerHTML = `
        <span class="hist-title" title="${escHtml(s.title || 'Chat')}">${escHtml((s.title || 'Chat').slice(0,35))}</span>
        <span class="hist-count">${s.message_count || 0}</span>
        <button class="btn-del-hist" onclick="deleteSession('${s.session_id}',event)" title="Delete">✕</button>
      `;
      item.addEventListener('click', () => openSession(s.session_id));
      list.appendChild(item);
    });
  } catch(e) {}
}

// ─── Open Session ─────────────────────────────────────────────────────────────
async function openSession(sessionId) {
  try {
    const data = await post(API.loadSess, { session_id: sessionId, supabase_url: state.supabaseUrl, supabase_key: state.supabaseKey });
    state.sessionId = sessionId;
    state.messages  = data.messages || [];
    renderAllMessages();
    highlightHistory(sessionId);
  } catch(e) {}
}

function highlightHistory(sid) {
  document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.history-item').forEach(el => {
    const btn = el.querySelector('.btn-del-hist');
    if (btn && btn.getAttribute('onclick')?.includes(sid)) el.classList.add('active');
  });
}

// ─── Delete Session ───────────────────────────────────────────────────────────
async function deleteSession(sessionId, e) {
  e.stopPropagation();
  if (!confirm('Delete this chat?')) return;
  await post(API.deleteSess, { session_id: sessionId, supabase_url: state.supabaseUrl, supabase_key: state.supabaseKey });
  if (sessionId === state.sessionId) newChat();
  else loadHistory();
}

// ─── New Chat ─────────────────────────────────────────────────────────────────
async function newChat() {
  // Save current session before clearing
  if (state.messages.length) {
    await post(API.saveSess, { session_id: state.sessionId, messages: state.messages, supabase_url: state.supabaseUrl, supabase_key: state.supabaseKey });
  }
  const data = await post(API.newSession, { session_id: state.sessionId, messages: state.messages, supabase_url: state.supabaseUrl, supabase_key: state.supabaseKey });
  state.sessionId = data.session_id;
  state.messages  = [];
  renderAllMessages();
  loadHistory();
}

// ─── Send Message ─────────────────────────────────────────────────────────────
async function sendMessage(overrideText) {
  const inp = document.getElementById('msgInput');
  const text = (overrideText || inp.value).trim();
  if (!text || state.isTyping) return;

  if (!overrideText) { inp.value = ''; inp.style.height = 'auto'; }

  // Add user message
  const userMsg = { role: 'user', content: text, time: now() };
  state.messages.push(userMsg);
  appendMessage(userMsg);
  hideWelcome();

  // Show typing
  state.isTyping = true;
  showTyping();
  setSendDisabled(true);

  try {
    const data = await post(API.chat, {
      message:       text,
      session_id:    state.sessionId,
      api_key:       state.apiKey,
      model:         state.model,
      supabase_url:  state.supabaseUrl,
      supabase_key:  state.supabaseKey,
    });
    removeTyping();
    if (data.error) {
      const errMsg = { role: 'bot', content: '⚠️ Error: ' + data.error, time: now() };
      state.messages.push(errMsg);
      appendMessage(errMsg);
    } else {
      const botMsg = { role: 'bot', content: data.reply || '', time: now(), tools: data.tool_calls || [] };
      state.messages.push(botMsg);
      appendMessage(botMsg);
    }
    // Auto-save
    post(API.saveSess, { session_id: state.sessionId, messages: state.messages, supabase_url: state.supabaseUrl, supabase_key: state.supabaseKey });
    loadHistory();
  } catch(e) {
    removeTyping();
    const errMsg = { role: 'bot', content: '⚠️ Error: ' + e.message, time: now() };
    state.messages.push(errMsg);
    appendMessage(errMsg);
  } finally {
    state.isTyping = false;
    setSendDisabled(false);
    document.getElementById('msgInput').focus();
  }
}

// ─── Render ───────────────────────────────────────────────────────────────────
function renderAllMessages() {
  const area = document.getElementById('chatArea');
  area.innerHTML = '';
  if (!state.messages.length) {
    showWelcome();
    return;
  }
  hideWelcome();
  state.messages.forEach(m => appendMessage(m));
}

function appendMessage(msg) {
  const area = document.getElementById('chatArea');
  const isUser = msg.role === 'user';

  const row = document.createElement('div');
  row.className = 'msg-row ' + (isUser ? 'user' : 'bot');

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = isUser ? '👤' : '🤖';

  const content = document.createElement('div');
  content.className = 'msg-content';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  if (isUser) {
    bubble.textContent = msg.content;
  } else {
    bubble.innerHTML = renderMarkdown(msg.content);
    // Syntax highlight code blocks
    bubble.querySelectorAll('pre code').forEach(el => { if (window.hljs) hljs.highlightElement(el); });
  }

  const meta = document.createElement('div');
  meta.style.cssText = 'display:flex;gap:8px;align-items:center;';
  const timeEl = document.createElement('span');
  timeEl.className = 'msg-time';
  timeEl.textContent = msg.time || '';
  meta.appendChild(timeEl);

  if (!isUser && msg.tools && msg.tools.length) {
    const toolEl = document.createElement('span');
    toolEl.className = 'tool-used';
    toolEl.textContent = '🔧 ' + msg.tools.join(', ');
    meta.appendChild(toolEl);
  }

  content.appendChild(bubble);
  content.appendChild(meta);
  row.appendChild(avatar);
  row.appendChild(content);
  area.appendChild(row);
  area.scrollTop = area.scrollHeight;
}

function renderMarkdown(text) {
  if (window.marked) {
    marked.setOptions({ breaks: true, gfm: true });
    return marked.parse(text);
  }
  return escHtml(text).replace(/\n/g, '<br>');
}

function showTyping() {
  const area = document.getElementById('chatArea');
  const row = document.createElement('div');
  row.className = 'typing-row'; row.id = 'typingRow';
  const av = document.createElement('div'); av.className = 'msg-avatar'; av.textContent = '🤖';
  const bub = document.createElement('div'); bub.className = 'typing-bubble';
  bub.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
  row.appendChild(av); row.appendChild(bub);
  area.appendChild(row);
  area.scrollTop = area.scrollHeight;
}
function removeTyping() { const el = document.getElementById('typingRow'); if (el) el.remove(); }

function showWelcome() { document.getElementById('welcome').style.display = 'flex'; }
function hideWelcome() { document.getElementById('welcome').style.display = 'none'; }

function setSendDisabled(v) { document.getElementById('sendBtn').disabled = v; }
function now() { return new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}); }
function escHtml(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

// ─── Supabase Test ────────────────────────────────────────────────────────────
async function testSupabase() {
  const el = document.getElementById('connStatus');
  el.textContent = 'Testing...'; el.className = 'conn-status';
  try {
    const data = await post(API.testSupa, { supabase_url: state.supabaseUrl, supabase_key: state.supabaseKey });
    if (data.success) { el.textContent = '✅ ' + data.message; el.className = 'conn-status success'; }
    else { el.textContent = '❌ ' + (data.error || 'Failed'); el.className = 'conn-status error'; }
  } catch(e) { el.textContent = '❌ Network error'; el.className = 'conn-status error'; }
}

// ─── Accordion ───────────────────────────────────────────────────────────────
function toggleAccordion(id) {
  const body = document.getElementById(id);
  const header = body.previousElementSibling;
  body.classList.toggle('open');
  header.classList.toggle('open');
}

// ─── Quick Prompts ───────────────────────────────────────────────────────────
function quickSend(text) { sendMessage(text); }
