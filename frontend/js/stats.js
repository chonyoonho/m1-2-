let monthlyChart = null;
let lastStatistics = null;

function chartColors() {
  const styles = getComputedStyle(document.documentElement);
  return {
    line: styles.getPropertyValue("--navy").trim() || "#1b2a4a",
    fill: styles.getPropertyValue("--gold").trim() || "#c79a3d",
    text: styles.getPropertyValue("--text").trim() || "#1f2430",
    grid: styles.getPropertyValue("--border").trim() || "#e4e0d6",
  };
}

function renderMonthlyChart(monthly) {
  const canvas = document.getElementById("monthly-chart");
  if (!canvas || typeof Chart === "undefined") return;

  const colors = chartColors();
  const labels = monthly.map((m) => m.month);
  const totals = monthly.map((m) => m.total);

  if (monthlyChart) monthlyChart.destroy();
  monthlyChart = new Chart(canvas.getContext("2d"), {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "월별 참가자 수 합계",
          data: totals,
          borderColor: colors.line,
          backgroundColor: colors.fill,
          tension: 0.25,
          pointRadius: 2,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { labels: { color: colors.text } },
      },
      scales: {
        x: { ticks: { color: colors.text, maxRotation: 60, minRotation: 60 }, grid: { color: colors.grid } },
        y: { ticks: { color: colors.text }, grid: { color: colors.grid } },
      },
    },
  });
  window.monthlyChart = monthlyChart;
}

function refreshChartColors() {
  if (lastStatistics) renderMonthlyChart(lastStatistics.monthly);
}

function renderProgramTable(byProgram) {
  const tbody = document.getElementById("program-table-body");
  if (byProgram.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" class="muted">등록된 데이터가 없습니다.</td></tr>';
    return;
  }
  tbody.innerHTML = "";
  byProgram.forEach((p) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${p.program}</td><td>${p.total}</td><td>${p.average}</td><td>${p.count}</td>`;
    tbody.appendChild(tr);
  });
}

async function refreshStats() {
  const tbody = document.getElementById("program-table-body");
  tbody.innerHTML = '<tr><td colspan="4" class="muted">불러오는 중...</td></tr>';
  try {
    const stats = await Api.getStatistics();
    lastStatistics = stats;
    renderMonthlyChart(stats.monthly);
    renderProgramTable(stats.by_program);
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="4" class="status-text error">불러오기 실패: ${err.message}</td></tr>`;
  }
}

function downloadBlob(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function toCsv(items) {
  const header = "date,value,memo";
  const rows = items.map((it) => {
    const memo = `"${String(it.memo).replace(/"/g, '""')}"`;
    return `${it.date},${it.value},${memo}`;
  });
  return [header, ...rows].join("\n");
}

function initStatsTab() {
  document.getElementById("stats-refresh-btn").addEventListener("click", refreshStats);

  document.getElementById("export-csv-btn").addEventListener("click", async () => {
    const items = await Api.listData();
    downloadBlob(toCsv(items), "38demo-data.csv", "text/csv;charset=utf-8");
  });

  document.getElementById("export-json-btn").addEventListener("click", async () => {
    const items = await Api.listData();
    downloadBlob(JSON.stringify(items, null, 2), "38demo-data.json", "application/json;charset=utf-8");
  });
}
