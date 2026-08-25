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

let state = {
  sessionId:   '',
  messages:    [],
  isTyping:    false,
  apiKey:      localStorage.getItem('gemini_api_key') || '',
  model:       localStorage.getItem('gemini_model') || 'gemini-3.5-flash',
  supabaseUrl: localStorage.getItem('supabase_url') || '',
  supabaseKey: localStorage.getItem('supabase_key') || '',
  userEmail:   '',
};

async function initApp(userEmail) {
  state.userEmail = userEmail || '';
  const prefix = 'chat_' + (state.userEmail.replace(/[^a-z0-9]/gi,'_')) + '_';
  state.sessionId = prefix + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
  await loadModels();
  await loadHistory();
  setupInputHandlers();
}

document.addEventListener('DOMContentLoaded', () => {
  setupInputHandlers();
});

function setupInputHandlers() {
  const inp = document.getElementById('msgInput');
  if (!inp) return;
  inp.addEventListener('input', () => {
    inp.style.height = 'auto';
    inp.style.height = Math.min(inp.scrollHeight, 140) + 'px';
  });
  inp.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });
}

async function post(url, body) {
  const r = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    credentials: 'include',
    body: JSON.stringify(body)
  });
  const text = await r.text();
  if (!r.ok) throw new Error(`HTTP ${r.status}: ${text.substring(0, 150)}`);
  try { return JSON.parse(text); }
  catch(err) { throw new Error(`Non-JSON response: ${text.substring(0, 150)}`); }
}

async function loadModels() {
  try {
    const data = await fetch(API.models).then(r => r.json());
    const badge = document.getElementById('modelBadge');
    if (badge) badge.textContent = state.model;
  } catch(e) {}
}

async function loadHistory() {
  try {
    const data = await post(API.history, {
      supabase_url: state.supabaseUrl,
      supabase_key: state.supabaseKey,
      user_email:   state.userEmail,
    });
    const list = document.getElementById('historyList');
    list.innerHTML = '';

    let sessions = (data.sessions || []).filter(s =>
      !state.userEmail ||
      (s.session_id && s.session_id.includes(
        state.userEmail.replace(/[^a-z0-9]/gi,'_')
      ))
    );

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

async function openSession(sessionId) {
  try {
    const data = await post(API.loadSess, {
      session_id:   sessionId,
      supabase_url: state.supabaseUrl,
      supabase_key: state.supabaseKey,
    });
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

async function deleteSession(sessionId, e) {
  e.stopPropagation();
  if (!confirm('Delete this chat?')) return;
  await post(API.deleteSess, {
    session_id:   sessionId,
    supabase_url: state.supabaseUrl,
    supabase_key: state.supabaseKey,
  });
  if (sessionId === state.sessionId) newChat();
  else loadHistory();
}

async function newChat() {
  if (state.messages.length) {
    await post(API.saveSess, {
      session_id:   state.sessionId,
      messages:     state.messages,
      supabase_url: state.supabaseUrl,
      supabase_key: state.supabaseKey,
    });
  }
  const prefix = 'chat_' + (state.userEmail.replace(/[^a-z0-9]/gi,'_')) + '_';
  state.sessionId = prefix + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
  state.messages  = [];
  renderAllMessages();
  loadHistory();
}

async function sendMessage(overrideText) {
  const inp = document.getElementById('msgInput');
  const text = (overrideText || inp.value).trim();
  if (!text || state.isTyping) return;
  if (!overrideText) { inp.value = ''; inp.style.height = 'auto'; }

  const userMsg = { role: 'user', content: text, time: now() };
  state.messages.push(userMsg);
  appendMessage(userMsg);
  hideWelcome();

  state.isTyping = true;
  showTyping();
  setSendDisabled(true);

  try {
    const data = await post(API.chat, {
      message:      text,
      session_id:   state.sessionId,
      api_key:      state.apiKey,
      model:        state.model,
      supabase_url: state.supabaseUrl,
      supabase_key: state.supabaseKey,
      user_email:   state.userEmail,
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
    post(API.saveSess, {
      session_id:   state.sessionId,
      messages:     state.messages,
      supabase_url: state.supabaseUrl,
      supabase_key: state.supabaseKey,
    });
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

function renderAllMessages() {
  const area = document.getElementById('chatArea');
  area.innerHTML = '';
  if (!state.messages.length) { showWelcome(); return; }
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
function showWelcome() { const w = document.getElementById('welcome'); if(w) w.style.display = 'flex'; }
function hideWelcome() { const w = document.getElementById('welcome'); if(w) w.style.display = 'none'; }
function setSendDisabled(v) { document.getElementById('sendBtn').disabled = v; }
function now() { return new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}); }
function escHtml(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
function quickSend(text) { sendMessage(text); }