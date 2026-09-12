let currentConversationId = null;

function renderMessage(role, content) {
  const wrap = document.getElementById("chat-messages");
  const empty = wrap.querySelector(".chat-empty");
  if (empty) empty.remove();

  const el = document.createElement("div");
  el.className = `msg ${role}`;
  el.textContent = content;
  wrap.appendChild(el);
  wrap.scrollTop = wrap.scrollHeight;
  return el;
}

function setChatLabel(text) {
  document.getElementById("current-conversation-label").textContent = text;
}

function resetChat() {
  currentConversationId = null;
  setChatLabel("새 대화");
  const wrap = document.getElementById("chat-messages");
  wrap.innerHTML = '<div class="chat-empty">3.8민주의거기념사업회의 교육·행사 프로그램 참가자 수에 대해 무엇이든 물어보세요.</div>';
}

async function loadConversationIntoChat(conversationId) {
  const detail = await Api.getConversation(conversationId);
  currentConversationId = detail.id;
  setChatLabel(detail.title);

  const wrap = document.getElementById("chat-messages");
  wrap.innerHTML = "";
  detail.messages.forEach((m) => renderMessage(m.role, m.content));

  document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
  document.querySelector('.tab-btn[data-tab="chat"]').classList.add("active");
  document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
  document.getElementById("tab-chat").classList.add("active");
}

function initChat() {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send-btn");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    renderMessage("user", message);
    input.value = "";
    sendBtn.disabled = true;

    const loadingEl = renderMessage("assistant loading", "답변을 생각하는 중입니다...");
    loadingEl.classList.add("loading");

    try {
      const res = await Api.sendChat(message, currentConversationId);
      currentConversationId = res.conversation_id;
      loadingEl.remove();
      renderMessage("assistant", res.reply);
      setChatLabel(message.slice(0, 30));
    } catch (err) {
      loadingEl.remove();
      renderMessage("assistant", `오류가 발생했습니다: ${err.message}`);
    } finally {
      sendBtn.disabled = false;
      input.focus();
    }
  });

  document.getElementById("new-chat-btn").addEventListener("click", resetChat);
}
