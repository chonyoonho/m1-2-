function formatDateTime(iso) {
  try {
    return new Date(iso).toLocaleString("ko-KR");
  } catch (_) {
    return iso;
  }
}

async function refreshConversationList() {
  const list = document.getElementById("conversation-list");
  list.innerHTML = '<li class="muted">불러오는 중...</li>';

  try {
    const items = await Api.listConversations();
    if (items.length === 0) {
      list.innerHTML = '<li class="muted">저장된 대화가 없습니다.</li>';
      return;
    }

    list.innerHTML = "";
    items.forEach((item) => {
      const li = document.createElement("li");
      li.className = "conversation-item";
      li.innerHTML = `
        <div>
          <div>${item.title}</div>
          <div class="conv-meta">${item.message_count}개 메시지 · ${formatDateTime(item.updated_at)}</div>
        </div>
        <div class="conv-actions">
          <button class="btn-ghost" data-action="load">불러오기</button>
          <button class="btn-ghost" data-action="delete">삭제</button>
        </div>
      `;
      li.querySelector('[data-action="load"]').addEventListener("click", () =>
        loadConversationIntoChat(item.id)
      );
      li.querySelector('[data-action="delete"]').addEventListener("click", async () => {
        if (!confirm("이 대화를 삭제할까요?")) return;
        await Api.deleteConversation(item.id);
        await refreshConversationList();
      });
      list.appendChild(li);
    });
  } catch (err) {
    list.innerHTML = `<li class="status-text error">불러오기 실패: ${err.message}</li>`;
  }
}

function initHistoryTab() {
  document.getElementById("history-refresh-btn").addEventListener("click", refreshConversationList);
}
