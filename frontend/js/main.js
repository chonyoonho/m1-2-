function initTabs() {
  const buttons = document.querySelectorAll(".tab-btn");
  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      buttons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
      document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");

      if (btn.dataset.tab === "data") refreshDataTable();
      if (btn.dataset.tab === "history") refreshConversationList();
      if (btn.dataset.tab === "stats") refreshStats();
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initTabs();
  initChat();
  initDataForm();
  initHistoryTab();
  initStatsTab();
  loadSummary();
  refreshDataTable();
});
