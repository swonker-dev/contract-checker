from __future__ import annotations


CATALOG_HTML = r"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Проверка договоров</title>
  <style>
    :root { --bg:#f3f4ef; --surface:#fffef9; --text:#19231f; --muted:#65706b; --line:#d8ddd8; --accent:#176b52; --soft:#edf7f1; --shadow:0 20px 55px rgba(25,35,31,.09); }
    * { box-sizing:border-box; }
    body { margin:0; min-height:100vh; color:var(--text); background:radial-gradient(circle at 12% 0,rgba(23,107,82,.12),transparent 34rem),var(--bg); font-family:Inter,"Segoe UI",Arial,sans-serif; }
    main { width:min(1080px,calc(100% - 32px)); margin:auto; padding:64px 0 80px; }
    .top { display:flex; justify-content:space-between; align-items:center; gap:24px; }
    .admin { color:var(--accent); font-weight:700; text-decoration:none; }
    .eyebrow { color:var(--accent); font-size:13px; font-weight:800; letter-spacing:.1em; text-transform:uppercase; }
    h1 { max-width:800px; margin:14px 0 18px; font:500 clamp(40px,7vw,70px)/1.02 Georgia,serif; letter-spacing:-.04em; }
    .lead { max-width:720px; margin:0; color:var(--muted); font-size:19px; line-height:1.6; }
    .catalog { display:grid; grid-template-columns:repeat(3,1fr); gap:18px; margin-top:42px; }
    .card { display:flex; min-height:310px; flex-direction:column; padding:26px; border:1px solid var(--line); border-radius:20px; background:var(--surface); box-shadow:var(--shadow); }
    .card.disabled { box-shadow:none; opacity:.72; }
    .status { align-self:flex-start; padding:6px 10px; border-radius:99px; background:var(--soft); color:var(--accent); font-size:12px; font-weight:800; text-transform:uppercase; }
    .disabled .status { background:#f0f0ec; color:var(--muted); }
    h2 { margin:28px 0 12px; font:500 29px/1.15 Georgia,serif; }
    .description { margin:0; color:var(--muted); line-height:1.55; }
    .scope { margin:18px 0 24px; color:#44504a; font-size:14px; line-height:1.5; }
    .action { display:inline-flex; min-height:46px; margin-top:auto; align-items:center; justify-content:center; border-radius:11px; background:var(--accent); color:#fff; font-weight:750; text-decoration:none; }
    .disabled .action { background:#e4e6e2; color:#747c78; cursor:not-allowed; }
    .error { margin-top:32px; padding:16px; border-radius:12px; background:#fff0ed; color:#98382e; }
    @media(max-width:850px){ .catalog{grid-template-columns:1fr;} .card{min-height:250px;} }
  </style>
</head>
<body>
  <main>
    <div class="top"><span class="eyebrow">Юридический анализ документов</span><a class="admin" href="/regulations">Нормативная база →</a></div>
    <h1>Какой договор нужно проверить?</h1>
    <p class="lead">Выберите тип документа. Для каждого типа используется свой набор норм, правил и инструкций для модели.</p>
    <section class="catalog" id="catalog" aria-live="polite"></section>
    <div class="error" id="error" hidden></div>
  </main>
  <script>
    const catalog = document.getElementById("catalog");
    const errorBox = document.getElementById("error");
    function add(parent, tag, className, text) { const el=document.createElement(tag); el.className=className; el.textContent=text; parent.appendChild(el); return el; }
    async function loadTypes() {
      try {
        const response = await fetch("/api/document-types");
        if (!response.ok) throw new Error("Не удалось загрузить каталог типов документов.");
        const types = await response.json();
        types.forEach(type => {
          const card=document.createElement("article"); card.className=`card${type.enabled ? "" : " disabled"}`;
          add(card,"span","status",type.enabled ? "Доступно" : "В разработке");
          add(card,"h2","",type.title); add(card,"p","description",type.description); add(card,"p","scope",type.scope);
          if (type.enabled) { const link=add(card,"a","action","Перейти к проверке"); link.href=`/check/${type.id}`; }
          else { const button=add(card,"span","action","Скоро"); button.setAttribute("aria-disabled","true"); }
          catalog.appendChild(card);
        });
      } catch (reason) { errorBox.textContent=reason.message; errorBox.hidden=false; }
    }
    loadTypes();
  </script>
</body>
</html>"""


CHECK_HTML = r"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Проверка договора</title>
  <style>
    :root { --bg:#f3f4ef; --surface:#fffef9; --text:#19231f; --muted:#65706b; --line:#d8ddd8; --accent:#176b52; --warning:#93640a; --warning-bg:#fff8e5; --danger:#9a342a; --danger-bg:#fff0ed; --shadow:0 18px 50px rgba(31,41,37,.09); }
    * { box-sizing:border-box; } body { margin:0; min-height:100vh; background:var(--bg); color:var(--text); font-family:Inter,"Segoe UI",Arial,sans-serif; }
    main { width:min(900px,calc(100% - 32px)); margin:auto; padding:44px 0 72px; }
    a { color:var(--accent); font-weight:700; text-decoration:none; } h1 { margin:28px 0 10px; font:500 clamp(36px,6vw,58px)/1.05 Georgia,serif; }
    .scope,.lead { color:var(--muted); line-height:1.55; } .panel { margin-top:30px; padding:26px; border:1px solid var(--line); border-radius:20px; background:var(--surface); box-shadow:var(--shadow); }
    .drop { display:grid; min-height:210px; place-items:center; padding:28px; border:1.5px dashed #aeb9b2; border-radius:15px; background:#fafbf7; text-align:center; cursor:pointer; }
    input[type=file]{display:none}.file{margin-top:14px;font-weight:700}.actions{display:flex;align-items:center;gap:16px;margin-top:20px}button{min-height:48px;padding:0 22px;border:0;border-radius:11px;background:var(--accent);color:#fff;font:inherit;font-weight:750;cursor:pointer}button:disabled{opacity:.5;cursor:not-allowed}.state{color:var(--muted)}
    .error{margin-top:16px;padding:14px;border-radius:11px;background:var(--danger-bg);color:var(--danger)}.results{margin-top:36px}.summary{color:var(--muted)}.finding{margin-top:14px;padding:21px;border:1px solid var(--line);border-left:5px solid var(--warning);border-radius:13px;background:var(--surface)}.finding.violation,.finding.processing-error{border-left-color:var(--danger)}.badge{display:inline-block;padding:6px 10px;border-radius:99px;background:var(--warning-bg);color:var(--warning);font-size:12px;font-weight:800;text-transform:uppercase}.violation .badge,.processing-error .badge{background:var(--danger-bg);color:var(--danger)}.chunk{float:right;color:var(--muted);font-size:14px}.source{font-weight:700}.comment{line-height:1.55}blockquote{margin:14px 0 0;padding:11px 15px;border-left:3px solid var(--line);background:#f7f7f3}.law{color:var(--muted);font-size:14px;line-height:1.5}.empty{padding:24px;border-radius:13px;background:#edf7f1;color:#0f4c3a}.download{margin-top:20px}.hidden{display:none!important}.disclaimer{margin-top:24px;color:var(--muted);font-size:13px}
    @media(max-width:600px){.panel{padding:16px}.actions{align-items:stretch;flex-direction:column}button{width:100%}}
  </style>
</head>
<body>
<main>
  <a href="/">← Все типы договоров</a>
  <h1 id="title">Загрузка профиля…</h1><p class="lead" id="description"></p><p class="scope" id="scope"></p>
  <section class="panel">
    <label class="drop" for="file"><span><strong>Выберите DOCX или PDF</strong><br><span class="scope">Файл до 10 МБ</span></span></label>
    <input id="file" type="file" accept=".docx,.pdf"><div class="file" id="filename"></div>
    <div class="actions"><button id="start" disabled>Начать проверку</button><span class="state" id="state"></span></div>
    <div class="error hidden" id="error"></div>
  </section>
  <section class="results hidden" id="results"><h2>Результат проверки</h2><p class="summary" id="summary"></p><div id="findings"></div><button class="download" id="download">Скачать отчёт</button><p class="disclaimer">Результат MVP не является юридическим заключением.</p></section>
</main>
<script>
  const typeId=decodeURIComponent(location.pathname.split("/").filter(Boolean).pop());
  const fileInput=document.getElementById("file"), start=document.getElementById("start"), state=document.getElementById("state"), errorBox=document.getElementById("error"), results=document.getElementById("results"), findings=document.getElementById("findings"), summary=document.getElementById("summary"); let selected=null, markdown="";
  function add(parent,tag,className,text){const el=document.createElement(tag);if(className)el.className=className;el.textContent=text;parent.appendChild(el);return el}
  function fail(message){errorBox.textContent=message;errorBox.classList.remove("hidden");state.textContent=""}
  async function loadType(){const r=await fetch(`/api/document-types/${typeId}`);if(!r.ok){fail("Тип документа не найден.");return}const t=await r.json();document.title=`Проверка: ${t.title}`;document.getElementById("title").textContent=t.title;document.getElementById("description").textContent=t.description;document.getElementById("scope").textContent=`Область проверки: ${t.scope}`;if(!t.enabled)fail("Этот тип документа пока недоступен.")}
  fileInput.addEventListener("change",()=>{selected=fileInput.files[0]||null;document.getElementById("filename").textContent=selected?selected.name:"";start.disabled=!selected;errorBox.classList.add("hidden");results.classList.add("hidden")});
  function render(report){findings.replaceChildren();const visible=report.results.filter(x=>["warning","violation","error"].includes(x.status));const counts={violation:0,warning:0,error:0};visible.forEach(x=>counts[x.status]++);summary.textContent=`Пунктов: ${report.chunks_total} · нарушений: ${counts.violation} · предупреждений: ${counts.warning} · не проверено: ${counts.error}`;if(!visible.length)add(findings,"div","empty","Потенциальные нарушения и неоднозначные формулировки не обнаружены.");visible.forEach(item=>{const css=item.status==="error"?"processing-error":item.status;const card=document.createElement("article");card.className=`finding ${css}`;add(card,"span","badge",item.status==="violation"?"Нарушение":item.status==="warning"?"Предупреждение":"Ошибка обработки");add(card,"span","chunk",`Пункт ${item.chunk_id}`);if(item.status!=="error")add(card,"p","source",item.source||"Основание не указано");add(card,"p","comment",item.comment||"Комментарий не указан");if(item.contract_quote)add(card,"blockquote","",item.contract_quote);if(item.law_quote)add(card,"p","law",`Нормативный фрагмент: «${item.law_quote}»`);findings.appendChild(card)});markdown=report.markdown||"";results.classList.remove("hidden")}
  async function poll(id){for(;;){const r=await fetch(`/api/analyses/${id}`);const job=await r.json();if(!r.ok)throw new Error(job.detail||"Не удалось получить статус анализа.");state.textContent=job.stage;if(job.status==="completed"){render(job.report);state.textContent="Готово";return}if(job.status==="failed")throw new Error(job.error||"Анализ завершился с ошибкой.");await new Promise(resolve=>setTimeout(resolve,1200))}}
  start.addEventListener("click",async()=>{if(!selected)return;start.disabled=true;results.classList.add("hidden");errorBox.classList.add("hidden");state.textContent="Загружаем файл…";const data=new FormData();data.append("document_type_id",typeId);data.append("file",selected);try{const r=await fetch("/api/analyses",{method:"POST",body:data});const job=await r.json();if(!r.ok)throw new Error(job.detail||"Не удалось начать анализ.");await poll(job.analysis_id)}catch(reason){fail(reason.message||"Произошла ошибка.")}finally{start.disabled=false}});
  document.getElementById("download").addEventListener("click",()=>{const blob=new Blob([markdown],{type:"text/markdown;charset=utf-8"});const link=document.createElement("a");link.href=URL.createObjectURL(blob);link.download=`report-${selected?selected.name.replace(/\.[^.]+$/g,""):"contract"}.md`;link.click();URL.revokeObjectURL(link.href)});loadType().catch(e=>fail(e.message));
</script>
</body>
</html>"""
