function setDataStatus(text, isError = false) {
  const el = document.getElementById("data-status");
  el.textContent = text;
  el.className = `status-text ${isError ? "error" : ""}`;
}

function fillDataForm(item) {
  document.getElementById("data-id").value = item.id;
  document.getElementById("data-date").value = item.date;
  document.getElementById("data-value").value = item.value;
  document.getElementById("data-memo").value = item.memo;
  document.getElementById("data-submit-btn").textContent = "수정 완료";
  document.getElementById("data-cancel-btn").classList.remove("hidden");
}

function clearDataForm() {
  document.getElementById("data-id").value = "";
  document.getElementById("data-form").reset();
  document.getElementById("data-submit-btn").textContent = "추가";
  document.getElementById("data-cancel-btn").classList.add("hidden");
}

async function refreshDataTable() {
  const tbody = document.getElementById("data-table-body");
  tbody.innerHTML = '<tr><td colspan="4" class="muted">불러오는 중...</td></tr>';

  try {
    const items = await Api.listData();
    if (items.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" class="muted">등록된 데이터가 없습니다.</td></tr>';
      return;
    }

    tbody.innerHTML = "";
    items
      .slice()
      .reverse()
      .forEach((item) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${item.date}</td>
          <td>${item.value}</td>
          <td>${item.memo}</td>
          <td class="row-actions">
            <button data-action="edit">수정</button>
            <button data-action="delete" class="danger">삭제</button>
          </td>
        `;
        tr.querySelector('[data-action="edit"]').addEventListener("click", () => fillDataForm(item));
        tr.querySelector('[data-action="delete"]').addEventListener("click", () => handleDeleteData(item.id));
        tbody.appendChild(tr);
      });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="4" class="status-text error">불러오기 실패: ${err.message}</td></tr>`;
  }
}

async function handleDeleteData(id) {
  if (!confirm("이 데이터를 삭제할까요?")) return;
  try {
    await Api.deleteData(id);
    setDataStatus("삭제되었습니다.");
    await refreshDataTable();
    await loadSummary();
  } catch (err) {
    setDataStatus(`삭제 실패: ${err.message}`, true);
  }
}

function initDataForm() {
  const form = document.getElementById("data-form");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("data-id").value;
    const payload = {
      date: document.getElementById("data-date").value,
      value: Number(document.getElementById("data-value").value),
      memo: document.getElementById("data-memo").value.trim(),
    };

    try {
      if (id) {
        await Api.updateData(id, payload);
        setDataStatus("수정되었습니다.");
      } else {
        await Api.createData(payload);
        setDataStatus("추가되었습니다.");
      }
      clearDataForm();
      await refreshDataTable();
      await loadSummary();
    } catch (err) {
      setDataStatus(`저장 실패: ${err.message}`, true);
    }
  });

  document.getElementById("data-cancel-btn").addEventListener("click", clearDataForm);
  document.getElementById("data-refresh-btn").addEventListener("click", refreshDataTable);
}
