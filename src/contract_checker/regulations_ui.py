from __future__ import annotations


REGULATIONS_HTML = r"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Нормативная база</title>
  <style>
    :root { --bg:#f5f4ef; --surface:#fffef9; --text:#1f2925; --muted:#64706a; --line:#d8ddd8; --green:#176b52; --dark:#0f4c3a; --red:#9a342a; }
    * { box-sizing: border-box; }
    body { margin:0; background:var(--bg); color:var(--text); font-family:Inter,"Segoe UI",Arial,sans-serif; }
    main { width:min(960px,calc(100% - 32px)); margin:auto; padding:42px 0 70px; }
    a { color:var(--green); text-decoration:none; font-weight:700; }
    h1 { margin:30px 0 10px; font:500 clamp(36px,6vw,56px)/1.05 Georgia,serif; letter-spacing:-.03em; }
    .lead { max-width:720px; margin:0 0 28px; color:var(--muted); line-height:1.6; }
    .panel { padding:24px; border:1px solid var(--line); border-radius:18px; background:var(--surface); }
    .upload { display:flex; flex-wrap:wrap; align-items:center; gap:12px; }
    input[type=file] { max-width:100%; }
    button { min-height:42px; padding:0 17px; border:0; border-radius:10px; background:var(--green); color:#fff; font:inherit; font-weight:700; cursor:pointer; }
    button:hover { background:var(--dark); }
    button.secondary { border:1px solid var(--line); background:#fff; color:var(--text); }
    button.danger { background:#fff0ed; color:var(--red); }
    button:disabled { opacity:.5; cursor:wait; }
    .status { margin-top:12px; color:var(--muted); font-size:14px; }
    h2 { margin:34px 0 14px; font:500 28px/1.2 Georgia,serif; }
    .source { display:grid; grid-template-columns:1fr auto; gap:18px; margin-top:12px; padding:18px 20px; border:1px solid var(--line); border-radius:14px; background:var(--surface); }
    .source h3 { margin:0 0 7px; font-size:17px; }
    .meta { margin:0; color:var(--muted); font-size:14px; line-height:1.55; }
    .badge { display:inline-block; margin-left:8px; padding:4px 8px; border-radius:999px; background:#e8f5ee; color:var(--dark); font-size:11px; text-transform:uppercase; }
    .empty { color:var(--muted); }
    .note { margin-top:28px; color:var(--muted); font-size:13px; line-height:1.5; }
    @media(max-width:620px) { .source { grid-template-columns:1fr; } .source button { width:100%; } }
  </style>
</head>
<body>
  <main>
    <a href="/">← К проверке договора</a>
    <h1>Нормативная база</h1>
    <p class="lead">Загрузите проверенную редакцию в JSON. Новая редакция того же источника станет активной, а предыдущая будет перемещена в архив.</p>
    <section class="panel">
      <div class="upload">
        <input id="file" type="file" accept=".json,application/json">
        <button id="upload" type="button">Загрузить редакцию</button>
      </div>
      <div class="status" id="status" aria-live="polite"></div>
    </section>
    <h2>Активные источники</h2>
    <div id="active"></div>
    <h2>Архив</h2>
    <div id="archived"></div>
    <p class="note">Индекс будет перестроен автоматически при следующей проверке договора. Административная страница MVP не имеет авторизации и предназначена для локального запуска.</p>
  </main>
  <script>
    const fileInput = document.getElementById("file");
    const uploadButton = document.getElementById("upload");
    const statusNode = document.getElementById("status");
    const activeNode = document.getElementById("active");
    const archivedNode = document.getElementById("archived");

    async function request(url, options) {
      const response = await fetch(url, options);
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || "Ошибка запроса");
      return payload;
    }

    function sourceCard(source) {
      const card = document.createElement("article"); card.className = "source";
      const body = document.createElement("div");
      const title = document.createElement("h3"); title.textContent = source.source_title;
      if (source.active) { const badge = document.createElement("span"); badge.className="badge"; badge.textContent="активен"; title.appendChild(badge); }
      body.appendChild(title);
      const meta = document.createElement("p"); meta.className="meta";
      meta.textContent = `ID: ${source.source_id} · редакция: ${source.edition_date || "не указана"} · фрагментов: ${source.chunks_count} · ${source.filename}`;
      body.appendChild(meta); card.appendChild(body);
      const button = document.createElement("button"); button.type="button";
      button.className = source.active ? "danger" : "secondary";
      button.textContent = source.active ? "Архивировать" : "Сделать активным";
      button.addEventListener("click", async () => {
        button.disabled = true;
        try {
          await request(`/api/regulations/${encodeURIComponent(source.filename)}/${source.active ? "archive" : "activate"}`, {method:"POST"});
          await loadSources(); statusNode.textContent = "Набор норм обновлён.";
        } catch (error) { statusNode.textContent = error.message; } finally { button.disabled = false; }
      });
      card.appendChild(button); return card;
    }

    function renderGroup(node, items) {
      node.replaceChildren();
      if (!items.length) { const empty=document.createElement("p"); empty.className="empty"; empty.textContent="Источников нет."; node.appendChild(empty); return; }
      items.forEach(item => node.appendChild(sourceCard(item)));
    }

    async function loadSources() {
      const sources = await request("/api/regulations");
      renderGroup(activeNode, sources.filter(item => item.active));
      renderGroup(archivedNode, sources.filter(item => !item.active));
    }

    uploadButton.addEventListener("click", async () => {
      const file = fileInput.files[0];
      if (!file) { statusNode.textContent = "Выберите JSON-файл."; return; }
      uploadButton.disabled = true; statusNode.textContent = "Проверяем и загружаем…";
      const form = new FormData(); form.append("file", file);
      try { await request("/api/regulations", {method:"POST", body:form}); await loadSources(); statusNode.textContent="Редакция загружена."; fileInput.value=""; }
      catch (error) { statusNode.textContent=error.message; }
      finally { uploadButton.disabled=false; }
    });

    loadSources().catch(error => { statusNode.textContent=error.message; });
  </script>
</body>
</html>
"""
