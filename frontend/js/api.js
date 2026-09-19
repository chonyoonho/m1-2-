const API_BASE_URL = window.APP_CONFIG.API_BASE_URL;

async function apiRequest(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch (_) {
      // 응답 본문이 없는 경우(204 등) 무시
    }
    throw new Error(detail || `요청 실패 (${res.status})`);
  }

  if (res.status === 204) return null;
  return res.json();
}

const Api = {
  getSummary: () => apiRequest("/api/data/summary"),
  getStatistics: () => apiRequest("/api/data/statistics"),
  listData: () => apiRequest("/api/data"),
  createData: (payload) =>
    apiRequest("/api/data", { method: "POST", body: JSON.stringify(payload) }),
  updateData: (id, payload) =>
    apiRequest(`/api/data/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteData: (id) => apiRequest(`/api/data/${id}`, { method: "DELETE" }),

  listConversations: () => apiRequest("/api/conversations"),
  getConversation: (id) => apiRequest(`/api/conversations/${id}`),
  deleteConversation: (id) => apiRequest(`/api/conversations/${id}`, { method: "DELETE" }),

  sendChat: (message, conversationId) =>
    apiRequest("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message, conversation_id: conversationId || null }),
    }),
};
