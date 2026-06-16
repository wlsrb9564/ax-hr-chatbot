const API_BASE = window.location.origin;

const SUGGESTIONS = [
  "경영비전",
  "인재상",
  "경조사 휴가 규정",
  "업무분장표",
];

async function streamChatbot(question, history, onToken, onDone, onError) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "ngrok-skip-browser-warning": "true" },
    body: JSON.stringify({
      message: question,
      history: history.map((m) => ({
        role: m.role === "bot" ? "assistant" : "user",
        content: m.text,
      })),
    }),
  });
  if (!res.ok) throw new Error(`서버 오류 ${res.status}`);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buf += decoder.decode(value, { stream: true });
    const lines = buf.split("\n");
    buf = lines.pop(); // 마지막 불완전한 줄은 다음 청크와 합침

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const chunk = JSON.parse(line.slice(6));
      if (chunk.type === "token") onToken(chunk.text);
      else if (chunk.type === "done") onDone(chunk.snippets || []);
      else if (chunk.type === "error") onError(chunk.text);
    }
  }
}

let messages = [];
let loading = false;
let sessionId = 0;

const els = {
  main: document.getElementById('main'),
  hero: document.getElementById('hero'),
  chat: document.getElementById('chat'),
  searchwrap: document.getElementById('searchwrap'),
  suggestions: document.getElementById('suggestions'),
  footer: document.getElementById('footer'),
  input: document.getElementById('q'),
  sendBtn: document.getElementById('sendBtn'),
  backBtn: document.getElementById('backBtn'),
};

SUGGESTIONS.forEach((s) => {
  const b = document.createElement('button');
  b.textContent = s;
  b.onclick = () => {
    els.input.value = s;
    updateSendBtn();
    submit();
  };
  els.suggestions.appendChild(b);
});

function escapeHtml(t) {
  const d = document.createElement('div');
  d.textContent = t;
  return d.innerHTML;
}

function renderChat() {
  let html = '';
  messages.forEach((m) => {
    if (m.role === 'user') {
      html += '<div class="row user"><div class="bubble user">' + escapeHtml(m.text) + '</div></div>';
    } else {
      let sourcesHtml = '';
      if (m.snippets && m.snippets.length > 0) {
        const seen = new Set();
        const chips = m.snippets
          .filter(s => { if (seen.has(s.id)) return false; seen.add(s.id); return true; })
          .map(s => `<span class="source-chip">${escapeHtml(s.category)} · ${escapeHtml(s.id)}</span>`)
          .join('');
        sourcesHtml = `<div class="sources"><span class="sources-label">출처</span>${chips}</div>`;
      }
      html += `<div class="row bot"><div class="avatar">시</div><div class="bot-wrap"><div class="bubble bot">${escapeHtml(m.text)}</div>${sourcesHtml}</div></div>`;
    }
  });
  if (loading) {
    html += '<div class="row bot"><div class="avatar">시</div><div class="typing"><span></span><span></span><span></span></div></div>';
  }
  els.chat.innerHTML = html;
  els.chat.scrollTop = els.chat.scrollHeight;
}

function enterChatMode() {
  els.main.classList.add('started');
  els.hero.classList.add('hidden');
  els.suggestions.classList.add('hidden');
  els.footer.classList.add('hidden');
  els.chat.classList.remove('hidden');
  els.searchwrap.classList.add('fixed');
  els.backBtn.classList.remove('hidden');
}

function goHome() {
  sessionId++;
  messages = [];
  loading = false;
  els.main.classList.remove('started');
  els.hero.classList.remove('hidden');
  els.suggestions.classList.remove('hidden');
  els.footer.classList.remove('hidden');
  els.chat.classList.add('hidden');
  els.chat.innerHTML = '';
  els.searchwrap.classList.remove('fixed');
  els.backBtn.classList.add('hidden');
  els.input.value = '';
  updateSendBtn();
  els.input.focus();
}

function updateSendBtn() {
  const has = els.input.value.trim().length > 0;
  els.sendBtn.classList.toggle('active', has && !loading);
}

async function submit(text) {
  const q = (text !== undefined ? text : els.input.value).trim();
  if (!q || loading) return;

  if (messages.length === 0) enterChatMode();

  const mySession = sessionId;
  const historySnapshot = [...messages];

  els.input.value = '';
  updateSendBtn();
  messages.push({ role: 'user', text: q });
  loading = true;
  renderChat();

  try {
    await streamChatbot(
      q,
      historySnapshot,
      (token) => {
        if (mySession !== sessionId) return;
        const last = messages[messages.length - 1];
        if (last.role !== 'bot') {
          // 첫 토큰 도착 시 타이핑 인디케이터 제거 후 빈 bot 메시지 추가
          loading = false;
          messages.push({ role: 'bot', text: token, snippets: [] });
        } else {
          last.text += token;
        }
        renderChat();
      },
      (snippets) => {
        if (mySession !== sessionId) return;
        const last = messages[messages.length - 1];
        if (last.role === 'bot') last.snippets = snippets;
        loading = false;
        renderChat();
        els.input.focus();
      },
      (errText) => {
        if (mySession !== sessionId) return;
        loading = false;
        messages.push({ role: 'bot', text: errText, snippets: [] });
        renderChat();
        els.input.focus();
      },
    );
  } catch (e) {
    if (mySession !== sessionId) return;
    loading = false;
    messages.push({ role: 'bot', text: '답변을 불러오지 못했어요. 잠시 후 다시 시도해 주세요.', snippets: [] });
    renderChat();
    els.input.focus();
  }
}

els.sendBtn.onclick = () => submit();
els.backBtn.onclick = () => goHome();
els.input.addEventListener('input', updateSendBtn);
els.input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    submit();
  }
});
