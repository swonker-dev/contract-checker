from __future__ import annotations


INDEX_HTML = r"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Проверка трудового договора</title>
  <style>
    :root {
      color-scheme: light;
      --background: #f5f4ef;
      --surface: #fffef9;
      --text: #1f2925;
      --muted: #64706a;
      --border: #d8ddd8;
      --accent: #176b52;
      --accent-dark: #0f4c3a;
      --warning: #93640a;
      --warning-bg: #fff8e5;
      --danger: #9a342a;
      --danger-bg: #fff0ed;
      --shadow: 0 18px 50px rgba(31, 41, 37, 0.09);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at 10% 0%, rgba(23, 107, 82, 0.10), transparent 33rem),
        var(--background);
      color: var(--text);
      font-family: Inter, "Segoe UI", Arial, sans-serif;
    }

    .page {
      width: min(960px, calc(100% - 32px));
      margin: 0 auto;
      padding: 56px 0 72px;
    }

    .eyebrow {
      margin: 0 0 12px;
      color: var(--accent);
      font-size: 13px;
      font-weight: 750;
      letter-spacing: 0.09em;
      text-transform: uppercase;
    }

    h1 {
      max-width: 720px;
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(36px, 7vw, 64px);
      font-weight: 500;
      line-height: 1.03;
      letter-spacing: -0.035em;
    }

    .lead {
      max-width: 670px;
      margin: 22px 0 34px;
      color: var(--muted);
      font-size: 18px;
      line-height: 1.6;
    }

    .admin-link { display: inline-block; margin: -14px 0 28px; color: var(--accent); font-weight: 700; text-decoration: none; }

    .panel {
      padding: 26px;
      border: 1px solid var(--border);
      border-radius: 22px;
      background: rgba(255, 254, 249, 0.94);
      box-shadow: var(--shadow);
    }

    .drop-zone {
      display: grid;
      min-height: 230px;
      place-items: center;
      padding: 34px;
      border: 1.5px dashed #aeb9b2;
      border-radius: 16px;
      background: #fbfcf8;
      text-align: center;
      cursor: pointer;
      transition: border-color 160ms ease, background 160ms ease, transform 160ms ease;
    }

    .drop-zone:hover,
    .drop-zone.dragging {
      border-color: var(--accent);
      background: #f2faf6;
      transform: translateY(-1px);
    }

    .file-icon {
      display: grid;
      width: 52px;
      height: 64px;
      margin: 0 auto 18px;
      place-items: center;
      border: 2px solid var(--accent);
      border-radius: 8px;
      color: var(--accent);
      font-size: 13px;
      font-weight: 800;
    }

    .drop-title { margin: 0; font-size: 19px; font-weight: 700; }
    .drop-hint { margin: 9px 0 0; color: var(--muted); line-height: 1.5; }
    input[type="file"] { display: none; }

    .file-row {
      display: none;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-top: 18px;
      padding: 14px 16px;
      border: 1px solid var(--border);
      border-radius: 12px;
      background: #fff;
    }

    .file-row.visible { display: flex; }
    .file-name { overflow: hidden; font-weight: 650; text-overflow: ellipsis; white-space: nowrap; }
    .file-size { flex: none; color: var(--muted); font-size: 14px; }

    .actions {
      display: flex;
      align-items: center;
      gap: 14px;
      margin-top: 20px;
    }

    button {
      min-height: 48px;
      padding: 0 22px;
      border: 0;
      border-radius: 12px;
      background: var(--accent);
      color: white;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
      transition: background 160ms ease, transform 160ms ease, opacity 160ms ease;
    }

    button:hover:not(:disabled) { background: var(--accent-dark); transform: translateY(-1px); }
    button:disabled { cursor: not-allowed; opacity: 0.5; }
    button.secondary { border: 1px solid var(--border); background: var(--surface); color: var(--text); }

    .status { color: var(--muted); font-size: 14px; }
    .error { margin-top: 18px; padding: 14px 16px; border-radius: 12px; background: var(--danger-bg); color: var(--danger); }
    .hidden { display: none !important; }

    .results { margin-top: 38px; }
    .results-header { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; margin-bottom: 18px; }
    .results h2 { margin: 0; font-family: Georgia, "Times New Roman", serif; font-size: 34px; font-weight: 500; }
    .summary { margin: 8px 0 0; color: var(--muted); }

    .finding {
      margin-top: 14px;
      padding: 22px;
      border: 1px solid var(--border);
      border-left-width: 5px;
      border-radius: 14px;
      background: var(--surface);
    }

    .finding.violation { border-left-color: var(--danger); }
    .finding.warning { border-left-color: var(--warning); }
    .finding.processing-error { border-left-color: var(--danger); }
    .finding-top { display: flex; align-items: center; justify-content: space-between; gap: 14px; }
    .badge { padding: 6px 10px; border-radius: 999px; font-size: 12px; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; }
    .violation .badge { background: var(--danger-bg); color: var(--danger); }
    .warning .badge { background: var(--warning-bg); color: var(--warning); }
    .processing-error .badge { background: var(--danger-bg); color: var(--danger); }
    .chunk { color: var(--muted); font-size: 14px; }
    .source { margin: 16px 0 8px; font-weight: 700; }
    .comment { margin: 0; line-height: 1.6; }
    blockquote { margin: 16px 0 0; padding: 12px 16px; border-left: 3px solid var(--border); background: #f7f7f3; color: #46514c; line-height: 1.55; }
    .law { margin: 14px 0 0; color: var(--muted); font-size: 14px; line-height: 1.55; }
    .empty { padding: 28px; border: 1px solid #b9d8ca; border-radius: 14px; background: #f1faf5; color: var(--accent-dark); }
    .disclaimer { margin-top: 28px; color: var(--muted); font-size: 13px; line-height: 1.5; }

    @media (max-width: 640px) {
      .page { padding-top: 34px; }
      .panel { padding: 16px; border-radius: 16px; }
      .drop-zone { min-height: 200px; padding: 24px 16px; }
      .actions, .results-header { align-items: stretch; flex-direction: column; }
      button { width: 100%; }
    }
  </style>
</head>
<body>
  <main class="page">
    <p class="eyebrow">Демонстрационный MVP</p>
    <h1>Проверка трудового договора</h1>
    <p class="lead">Загрузите договор, чтобы найти потенциальные противоречия и неоднозначные формулировки по выбранным статьям ТК РФ.</p>
    <a class="admin-link" href="/regulations">Управление нормативной базой →</a>

    <section class="panel" aria-label="Загрузка договора">
      <label class="drop-zone" id="drop-zone" for="file-input">
        <div>
          <div class="file-icon">DOC</div>
          <p class="drop-title">Выберите файл или перетащите его сюда</p>
          <p class="drop-hint">DOCX или PDF с текстовым слоем, до 10 МБ</p>
        </div>
      </label>
      <input id="file-input" type="file" accept=".docx,.pdf,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document">
      <div class="file-row" id="file-row">
        <span class="file-name" id="file-name"></span>
        <span class="file-size" id="file-size"></span>
      </div>
      <div class="actions">
        <button id="analyze-button" type="button" disabled>Проверить договор</button>
        <span class="status" id="status" aria-live="polite"></span>
      </div>
      <div class="error hidden" id="error" role="alert"></div>
    </section>

    <section class="results hidden" id="results" aria-live="polite">
      <div class="results-header">
        <div>
          <h2>Результат проверки</h2>
          <p class="summary" id="summary"></p>
        </div>
        <button class="secondary" id="download-button" type="button">Скачать отчёт</button>
      </div>
      <div id="findings"></div>
      <p class="disclaimer">Результат MVP не является юридическим заключением. Загруженный файл обрабатывается временно и удаляется после проверки.</p>
    </section>
  </main>

  <script>
    const input = document.getElementById("file-input");
    const dropZone = document.getElementById("drop-zone");
    const fileRow = document.getElementById("file-row");
    const fileName = document.getElementById("file-name");
    const fileSize = document.getElementById("file-size");
    const analyzeButton = document.getElementById("analyze-button");
    const status = document.getElementById("status");
    const error = document.getElementById("error");
    const results = document.getElementById("results");
    const summary = document.getElementById("summary");
    const findings = document.getElementById("findings");
    const downloadButton = document.getElementById("download-button");
    let selectedFile = null;
    let markdownReport = "";

    function formatBytes(bytes) {
      if (bytes < 1024 * 1024) return `${Math.ceil(bytes / 1024)} КБ`;
      return `${(bytes / 1024 / 1024).toFixed(1)} МБ`;
    }

    function showError(message) {
      error.textContent = message;
      error.classList.remove("hidden");
    }

    function selectFile(file) {
      error.classList.add("hidden");
      results.classList.add("hidden");
      const extension = file ? file.name.toLowerCase().split(".").pop() : "";
      if (!file || !["docx", "pdf"].includes(extension)) {
        selectedFile = null;
        fileRow.classList.remove("visible");
        analyzeButton.disabled = true;
        showError("Выберите файл в формате DOCX или PDF.");
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        selectedFile = null;
        fileRow.classList.remove("visible");
        analyzeButton.disabled = true;
        showError("Файл больше 10 МБ.");
        return;
      }
      selectedFile = file;
      fileName.textContent = file.name;
      fileSize.textContent = formatBytes(file.size);
      fileRow.classList.add("visible");
      analyzeButton.disabled = false;
      status.textContent = "";
    }

    function appendText(parent, tag, className, text) {
      const element = document.createElement(tag);
      if (className) element.className = className;
      element.textContent = text;
      parent.appendChild(element);
      return element;
    }

    function renderReport(report) {
      findings.replaceChildren();
      const visible = report.results.filter(item => ["warning", "violation", "error"].includes(item.status));
      const violations = visible.filter(item => item.status === "violation").length;
      const warnings = visible.filter(item => item.status === "warning").length;
      const processingErrors = visible.filter(item => item.status === "error").length;
      summary.textContent = `${report.filename} · пунктов: ${report.chunks_total} · нарушений: ${violations} · предупреждений: ${warnings} · не проверено: ${processingErrors}`;

      if (!report.supported_document) {
        appendText(findings, "div", "empty", report.message);
      } else if (!visible.length) {
        appendText(findings, "div", "empty", "Потенциальные нарушения и неоднозначные формулировки не обнаружены.");
      } else {
        visible.forEach(item => {
          const card = document.createElement("article");
          const statusClass = item.status === "error" ? "processing-error" : item.status;
          card.className = `finding ${statusClass}`;
          const top = document.createElement("div");
          top.className = "finding-top";
          const badge = item.status === "violation"
            ? "Нарушение"
            : item.status === "warning"
              ? "Предупреждение"
              : "Ошибка обработки";
          appendText(top, "span", "badge", badge);
          appendText(top, "span", "chunk", `Пункт ${item.chunk_id}`);
          card.appendChild(top);
          if (item.status !== "error") {
            appendText(card, "p", "source", item.source || "Основание не указано");
          }
          appendText(card, "p", "comment", item.comment || "Комментарий не указан");
          if (item.contract_quote) appendText(card, "blockquote", "", item.contract_quote);
          if (item.law_quote) appendText(card, "p", "law", `Нормативный фрагмент: «${item.law_quote}»`);
          findings.appendChild(card);
        });
      }
      markdownReport = report.markdown || "";
      results.classList.remove("hidden");
      results.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    async function analyze() {
      if (!selectedFile) return;
      analyzeButton.disabled = true;
      error.classList.add("hidden");
      results.classList.add("hidden");
      status.textContent = "Анализируем договор…";
      const formData = new FormData();
      formData.append("file", selectedFile);
      try {
        const response = await fetch("/analyze", { method: "POST", body: formData });
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.detail || "Не удалось проверить договор.");
        renderReport(payload);
        status.textContent = "Готово";
      } catch (reason) {
        showError(reason.message || "Произошла ошибка.");
        status.textContent = "";
      } finally {
        analyzeButton.disabled = false;
      }
    }

    input.addEventListener("change", () => selectFile(input.files[0]));
    analyzeButton.addEventListener("click", analyze);
    ["dragenter", "dragover"].forEach(eventName => dropZone.addEventListener(eventName, event => {
      event.preventDefault();
      dropZone.classList.add("dragging");
    }));
    ["dragleave", "drop"].forEach(eventName => dropZone.addEventListener(eventName, event => {
      event.preventDefault();
      dropZone.classList.remove("dragging");
    }));
    dropZone.addEventListener("drop", event => selectFile(event.dataTransfer.files[0]));
    downloadButton.addEventListener("click", () => {
      const blob = new Blob([markdownReport], { type: "text/markdown;charset=utf-8" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `report-${selectedFile ? selectedFile.name.replace(/\.[^.]+$/, "") : "contract"}.md`;
      link.click();
      URL.revokeObjectURL(link.href);
    });
  </script>
</body>
</html>
"""
