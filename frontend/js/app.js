const API_BASE = window.location.origin;

const SUGGESTIONS = [
  "경영비전",
  "인재상",
  "경조사 휴가 규정",
  "업무분장표",
];

async function callChatbot(question, history) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: question,
      history: history.map((m) => ({
        role: m.role === "bot" ? "assistant" : "user",
        content: m.text,
      })),
    }),
  });
  if (!res.ok) throw new Error(`서버 오류 ${res.status}`);
  const data = await res.json();
  return data.answer;
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
      html += '<div class="row bot"><div class="avatar">시</div><div class="bubble bot">' + escapeHtml(m.text) + '</div></div>';
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
    const answer = await callChatbot(q, historySnapshot);
    if (mySession !== sessionId) return;
    messages.push({ role: 'bot', text: answer });
  } catch (e) {
    if (mySession !== sessionId) return;
    messages.push({ role: 'bot', text: '답변을 불러오지 못했어요. 잠시 후 다시 시도해 주세요.' });
  } finally {
    if (mySession === sessionId) {
      loading = false;
      renderChat();
      els.input.focus();
    }
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
