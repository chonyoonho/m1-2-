async function loadSummary() {
  const badgeText = document.getElementById("summary-badge-text");
  try {
    const summary = await Api.getSummary();

    document.getElementById("s-period").textContent = summary.period;
    document.getElementById("s-count").textContent = `${summary.count}개`;
    document.getElementById(
      "s-metrics"
    ).textContent = `${summary.metrics.average} / ${summary.metrics.max} / ${summary.metrics.min}`;
    document.getElementById("s-trend").textContent = summary.trend;

    badgeText.textContent = `${summary.count}개 데이터 · ${summary.trend}`;
    return summary;
  } catch (err) {
    badgeText.textContent = "요약 정보를 불러오지 못했습니다.";
    console.error(err);
    return null;
  }
}
