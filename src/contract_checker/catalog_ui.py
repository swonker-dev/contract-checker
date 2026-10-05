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
    :root {
      color-scheme:light;
      --bg:#f3f4ef;
      --surface:#fffef9;
      --surface-strong:#fff;
      --text:#19231f;
      --muted:#65706b;
      --line:#d8ddd8;
      --accent:#176b52;
      --accent-dark:#0f4c3a;
      --accent-soft:#edf7f1;
      --warning:#8a5b06;
      --warning-bg:#fff7df;
      --danger:#9a342a;
      --danger-bg:#fff0ed;
      --shadow:0 20px 55px rgba(25,35,31,.09);
    }
    * { box-sizing:border-box; }
    body {
      margin:0;
      min-height:100vh;
      background:radial-gradient(circle at 12% 0,rgba(23,107,82,.11),transparent 34rem),var(--bg);
      color:var(--text);
      font-family:Inter,"Segoe UI",Arial,sans-serif;
    }
    button,input { font:inherit; }
    button,a,.drop { -webkit-tap-highlight-color:transparent; }
    main { width:min(1040px,calc(100% - 32px)); margin:auto; padding:34px 0 72px; }
    a { color:var(--accent); font-weight:750; text-decoration:none; }
    a:hover { color:var(--accent-dark); }
    .back { display:inline-flex; min-height:40px; align-items:center; gap:8px; }
    .hero { max-width:780px; margin-top:22px; }
    .eyebrow { margin:0 0 12px; color:var(--accent); font-size:12px; font-weight:850; letter-spacing:.1em; text-transform:uppercase; }
    h1 { margin:0 0 14px; font:500 clamp(38px,6vw,62px)/1.03 Georgia,serif; letter-spacing:-.035em; }
    .lead { max-width:720px; margin:0; color:var(--muted); font-size:18px; line-height:1.6; }
    .scope { margin:14px 0 0; color:#44504a; font-size:14px; line-height:1.5; }
    .workspace { display:grid; grid-template-columns:minmax(0,1fr) 282px; gap:22px; margin-top:34px; align-items:start; }
    .panel,.guide { border:1px solid var(--line); border-radius:22px; background:rgba(255,254,249,.96); box-shadow:var(--shadow); }
    .panel { padding:24px; }
    .guide { padding:22px; box-shadow:none; }
    .guide h2 { margin:0 0 20px; font-size:17px; }
    .guide-list { display:grid; gap:20px; margin:0; padding:0; list-style:none; }
    .guide-item { display:grid; grid-template-columns:28px 1fr; gap:12px; }
    .guide-number { display:grid; width:28px; height:28px; place-items:center; border-radius:50%; background:var(--accent-soft); color:var(--accent); font-size:13px; font-weight:850; }
    .guide-item strong { display:block; margin:3px 0 4px; font-size:14px; }
    .guide-item span:last-child { color:var(--muted); font-size:13px; line-height:1.45; }
    .privacy { margin:22px 0 0; padding-top:18px; border-top:1px solid var(--line); color:var(--muted); font-size:12px; line-height:1.5; }
    .drop {
      display:grid;
      min-height:230px;
      place-items:center;
      padding:30px;
      border:1.5px dashed #aab5ae;
      border-radius:16px;
      background:#fafbf7;
      text-align:center;
      cursor:pointer;
      outline:none;
      transition:border-color 160ms ease,background 160ms ease,transform 160ms ease,box-shadow 160ms ease;
    }
    .drop:hover,.drop.dragging { border-color:var(--accent); background:#f2faf6; transform:translateY(-1px); }
    .drop:focus-visible { border-color:var(--accent); box-shadow:0 0 0 4px rgba(23,107,82,.14); }
    .file-icon { display:grid; width:58px; height:66px; margin:0 auto 18px; place-items:center; border:2px solid var(--accent); border-radius:9px; color:var(--accent); font-size:12px; font-weight:850; letter-spacing:.05em; }
    .drop strong { display:block; font-size:18px; }
    .drop-hint { display:block; margin-top:8px; color:var(--muted); font-size:14px; line-height:1.45; }
    .choose { color:var(--accent); text-decoration:underline; text-underline-offset:3px; }
    input[type=file] { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap; }
    .file-card { display:flex; align-items:center; gap:13px; margin-top:14px; padding:13px 14px; border:1px solid var(--line); border-radius:13px; background:var(--surface-strong); }
    .file-type { display:grid; width:40px; height:40px; flex:none; place-items:center; border-radius:10px; background:var(--accent-soft); color:var(--accent); font-size:11px; font-weight:850; }
    .file-info { min-width:0; flex:1; }
    .file-name { overflow:hidden; font-size:14px; font-weight:750; text-overflow:ellipsis; white-space:nowrap; }
    .file-meta { margin-top:3px; color:var(--muted); font-size:12px; }
    .remove { min-height:36px; padding:0 10px; border:0; border-radius:9px; background:transparent; color:var(--muted); font-weight:750; cursor:pointer; }
    .remove:hover { background:#f1f2ee; color:var(--text); }
    .actions { display:flex; align-items:center; gap:16px; margin-top:18px; }
    .primary,.download { min-height:48px; padding:0 22px; border:0; border-radius:11px; background:var(--accent); color:#fff; font-weight:780; cursor:pointer; transition:background 160ms ease,transform 160ms ease,opacity 160ms ease; }
    .primary:hover:not(:disabled),.download:hover { background:var(--accent-dark); transform:translateY(-1px); }
    button:focus-visible,a:focus-visible { outline:3px solid rgba(23,107,82,.25); outline-offset:3px; }
    button:disabled { cursor:not-allowed; opacity:.5; }
    .state { display:flex; align-items:center; gap:9px; color:var(--muted); font-size:14px; }
    .spinner { width:17px; height:17px; flex:none; border:2px solid #c9d2cd; border-top-color:var(--accent); border-radius:50%; animation:spin .8s linear infinite; }
    @keyframes spin { to { transform:rotate(360deg); } }
    @media(prefers-reduced-motion:reduce){ * { scroll-behavior:auto!important; transition:none!important; } .spinner { animation:none; border-color:var(--accent); } }
    .error { margin-top:16px; padding:14px 16px; border-radius:11px; background:var(--danger-bg); color:var(--danger); line-height:1.5; }
    .results { margin-top:48px; scroll-margin-top:24px; }
    .results-head { display:flex; align-items:end; justify-content:space-between; gap:20px; }
    .results h2 { margin:0; font:500 clamp(30px,5vw,42px)/1.1 Georgia,serif; }
    .report-file { margin:8px 0 0; color:var(--muted); }
    .download { flex:none; background:var(--surface-strong); color:var(--text); border:1px solid var(--line); }
    .download:hover { background:#f8f9f5; color:var(--text); }
    .summary-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:22px 0; }
    .metric { padding:16px; border:1px solid var(--line); border-radius:14px; background:var(--surface); }
    .metric strong { display:block; font:500 30px/1 Georgia,serif; }
    .metric span { display:block; margin-top:7px; color:var(--muted); font-size:12px; }
    .metric.danger strong { color:var(--danger); }
    .metric.warning strong { color:var(--warning); }
    .filters { display:flex; gap:8px; overflow-x:auto; padding:2px 2px 6px; }
    .filter { min-height:38px; flex:none; padding:0 14px; border:1px solid var(--line); border-radius:99px; background:var(--surface); color:var(--muted); font-weight:750; cursor:pointer; }
    .filter:hover,.filter[aria-pressed=true] { border-color:var(--accent); background:var(--accent-soft); color:var(--accent-dark); }
    .finding { margin-top:14px; padding:21px; border:1px solid var(--line); border-left:5px solid var(--warning); border-radius:13px; background:var(--surface); }
    .finding.violation,.finding.processing-error { border-left-color:var(--danger); }
    .finding-top { display:flex; align-items:center; justify-content:space-between; gap:12px; }
    .badge { display:inline-block; padding:6px 10px; border-radius:99px; background:var(--warning-bg); color:var(--warning); font-size:11px; font-weight:850; letter-spacing:.03em; text-transform:uppercase; }
    .violation .badge,.processing-error .badge { background:var(--danger-bg); color:var(--danger); }
    .chunk { color:var(--muted); font-size:13px; }
    .source { margin:17px 0 8px; font-weight:750; }
    .comment { margin:0; line-height:1.6; }
    blockquote { margin:14px 0 0; padding:12px 15px; border-left:3px solid var(--line); background:#f7f7f3; color:#46514c; line-height:1.55; }
    .law { margin:14px 0 0; color:var(--muted); font-size:14px; line-height:1.5; }
    .empty { margin-top:14px; padding:24px; border:1px solid #bdd8cc; border-radius:13px; background:var(--accent-soft); color:var(--accent-dark); line-height:1.5; }
    .hidden { display:none!important; }
    .disclaimer { margin-top:24px; color:var(--muted); font-size:13px; line-height:1.5; }
    @media(max-width:780px){ .workspace{grid-template-columns:1fr}.guide{order:-1}.guide-list{grid-template-columns:repeat(3,1fr)}.guide-item{grid-template-columns:1fr}.privacy{display:none}.summary-grid{grid-template-columns:repeat(2,1fr)} }
    @media(max-width:600px){ main{padding-top:22px}.hero{margin-top:14px}.panel{padding:15px;border-radius:17px}.guide{display:none}.drop{min-height:205px;padding:24px 16px}.actions,.results-head{align-items:stretch;flex-direction:column}.primary,.download{width:100%}.state{min-height:20px}.summary-grid{gap:8px}.metric{padding:13px}.finding{padding:17px}.finding-top{align-items:flex-start}.chunk{padding-top:4px} }
  </style>
</head>
<body>
<main>
  <a class="back" href="/" aria-label="Вернуться к выбору типа договора">← Все типы договоров</a>
  <header class="hero">
    <p class="eyebrow">Проверка документа</p>
    <h1 id="title">Загрузка профиля…</h1>
    <p class="lead" id="description"></p>
    <p class="scope" id="scope"></p>
  </header>

  <div class="workspace">
    <section class="panel" aria-label="Загрузка документа">
      <label class="drop" id="drop" for="file" tabindex="0" role="button" aria-describedby="drop-hint">
        <span>
          <span class="file-icon" aria-hidden="true">DOC</span>
          <strong><span class="choose">Выберите файл</span> или перетащите его сюда</strong>
          <span class="drop-hint" id="drop-hint">DOCX или PDF с текстовым слоем · до 10 МБ</span>
        </span>
      </label>
      <input id="file" type="file" accept=".docx,.pdf">
      <div class="file-card hidden" id="file-card">
        <span class="file-type" id="file-type" aria-hidden="true"></span>
        <div class="file-info"><div class="file-name" id="filename"></div><div class="file-meta" id="file-meta"></div></div>
        <button class="remove" id="remove" type="button" aria-label="Убрать выбранный файл">Убрать</button>
      </div>
      <div class="actions">
        <button class="primary" id="start" type="button" disabled>Проверить договор</button>
        <span class="state" id="state" aria-live="polite"></span>
      </div>
      <div class="error hidden" id="error" role="alert"></div>
    </section>

    <aside class="guide" aria-label="Как проходит проверка">
      <h2>Как проходит проверка</h2>
      <ol class="guide-list">
        <li class="guide-item"><span class="guide-number">1</span><span><strong>Извлекаем текст</strong><span>Распознаём структуру и пункты документа.</span></span></li>
        <li class="guide-item"><span class="guide-number">2</span><span><strong>Сверяем условия</strong><span>Проверяем их по выбранным нормам ТК РФ.</span></span></li>
        <li class="guide-item"><span class="guide-number">3</span><span><strong>Готовим отчёт</strong><span>Показываем замечания и цитаты из договора.</span></span></li>
      </ol>
      <p class="privacy">Файл обрабатывается временно и удаляется после завершения анализа.</p>
    </aside>
  </div>

  <section class="results hidden" id="results" aria-live="polite">
    <div class="results-head">
      <div><p class="eyebrow">Анализ завершён</p><h2>Результат проверки</h2><p class="report-file" id="report-file"></p></div>
      <button class="download" id="download" type="button">Скачать отчёт</button>
    </div>
    <div class="summary-grid" aria-label="Сводка по проверке">
      <div class="metric"><strong id="total-count">0</strong><span>пунктов проверено</span></div>
      <div class="metric danger"><strong id="violation-count">0</strong><span>нарушений</span></div>
      <div class="metric warning"><strong id="warning-count">0</strong><span>предупреждений</span></div>
      <div class="metric"><strong id="error-count">0</strong><span>не проверено</span></div>
    </div>
    <div class="filters hidden" id="filters" aria-label="Фильтр замечаний">
      <button class="filter" type="button" data-filter="all" aria-pressed="true">Все</button>
      <button class="filter" type="button" data-filter="violation" aria-pressed="false">Нарушения</button>
      <button class="filter" type="button" data-filter="warning" aria-pressed="false">Предупреждения</button>
      <button class="filter" type="button" data-filter="error" aria-pressed="false">Не проверено</button>
    </div>
    <div id="findings"></div>
    <div class="empty hidden" id="filter-empty">В этой категории замечаний нет.</div>
    <p class="disclaimer">Результат MVP не является юридическим заключением. Для решений с правовыми последствиями проконсультируйтесь со специалистом.</p>
  </section>
</main>
<script>
  const typeId=decodeURIComponent(location.pathname.split("/").filter(Boolean).pop());
  const MAX_FILE_SIZE=10*1024*1024;
  const allowedExtensions=["docx","pdf"];
  const fileInput=document.getElementById("file"), drop=document.getElementById("drop"), fileCard=document.getElementById("file-card"), start=document.getElementById("start"), state=document.getElementById("state"), errorBox=document.getElementById("error"), results=document.getElementById("results"), findings=document.getElementById("findings"), filters=document.getElementById("filters"), filterEmpty=document.getElementById("filter-empty");
  let selected=null, markdown="", isAnalyzing=false;

  function add(parent,tag,className,text){const el=document.createElement(tag);if(className)el.className=className;el.textContent=text;parent.appendChild(el);return el}
  function formatBytes(bytes){return bytes<1024*1024?`${Math.max(1,Math.ceil(bytes/1024))} КБ`:`${(bytes/1024/1024).toFixed(1)} МБ`}
  function setState(message,busy=false){state.replaceChildren();if(busy)add(state,"span","spinner","");if(message)add(state,"span","",message)}
  function fail(message){errorBox.textContent=message;errorBox.classList.remove("hidden");setState("")}
  function clearError(){errorBox.classList.add("hidden");errorBox.textContent=""}
  function fileExtension(file){return file?.name.toLowerCase().split(".").pop()||""}
  function clearFile(){selected=null;fileInput.value="";fileCard.classList.add("hidden");start.disabled=true;results.classList.add("hidden");clearError();setState("")}
  function selectFile(file){
    clearError();results.classList.add("hidden");
    const extension=fileExtension(file);
    if(!file||!allowedExtensions.includes(extension)){clearFile();fail("Выберите файл в формате DOCX или PDF.");return}
    if(file.size>MAX_FILE_SIZE){clearFile();fail("Файл больше 10 МБ. Выберите документ меньшего размера.");return}
    selected=file;
    document.getElementById("filename").textContent=file.name;
    document.getElementById("file-meta").textContent=`${extension.toUpperCase()} · ${formatBytes(file.size)}`;
    document.getElementById("file-type").textContent=extension.toUpperCase();
    fileCard.classList.remove("hidden");start.disabled=false;setState("");
  }
  async function loadType(){
    const r=await fetch(`/api/document-types/${typeId}`);
    if(!r.ok){fail("Тип документа не найден.");start.disabled=true;return}
    const type=await r.json();
    document.title=`Проверка: ${type.title}`;
    document.getElementById("title").textContent=type.title;
    document.getElementById("description").textContent=type.description;
    document.getElementById("scope").textContent=`Область проверки: ${type.scope}`;
    if(!type.enabled){fail("Этот тип документа пока недоступен.");drop.setAttribute("aria-disabled","true");fileInput.disabled=true}
  }
  function applyFilter(filter){
    const cards=findings.querySelectorAll(".finding");
    let shown=0;
    cards.forEach(card=>{const visible=filter==="all"||card.dataset.status===filter;card.classList.toggle("hidden",!visible);if(visible)shown++});
    filterEmpty.classList.toggle("hidden",cards.length===0||shown>0);
    filters.querySelectorAll(".filter").forEach(button=>button.setAttribute("aria-pressed",String(button.dataset.filter===filter)));
  }
  function render(report){
    findings.replaceChildren();
    const visible=(report.results||[]).filter(item=>["warning","violation","error"].includes(item.status));
    const counts={violation:0,warning:0,error:0};visible.forEach(item=>counts[item.status]++);
    document.getElementById("report-file").textContent=report.filename||selected?.name||"Проверенный документ";
    document.getElementById("total-count").textContent=report.chunks_total||0;
    document.getElementById("violation-count").textContent=counts.violation;
    document.getElementById("warning-count").textContent=counts.warning;
    document.getElementById("error-count").textContent=counts.error;
    if(!report.supported_document){add(findings,"div","empty",report.message||"Документ не поддерживается.")}
    else if(!visible.length){add(findings,"div","empty","Потенциальные нарушения и неоднозначные формулировки не обнаружены.")}
    visible.forEach(item=>{
      const css=item.status==="error"?"processing-error":item.status;
      const card=document.createElement("article");card.className=`finding ${css}`;card.dataset.status=item.status;
      const top=document.createElement("div");top.className="finding-top";
      add(top,"span","badge",item.status==="violation"?"Нарушение":item.status==="warning"?"Предупреждение":"Не проверено");
      add(top,"span","chunk",`Пункт ${item.chunk_id}`);card.appendChild(top);
      if(item.status!=="error")add(card,"p","source",item.source||"Основание не указано");
      add(card,"p","comment",item.comment||"Комментарий не указан");
      if(item.contract_quote)add(card,"blockquote","",item.contract_quote);
      if(item.law_quote)add(card,"p","law",`Нормативный фрагмент: «${item.law_quote}»`);
      findings.appendChild(card)
    });
    markdown=report.markdown||"";
    filters.classList.toggle("hidden",visible.length<2);
    filterEmpty.classList.add("hidden");applyFilter("all");
    results.classList.remove("hidden");results.scrollIntoView({behavior:"smooth",block:"start"})
  }
  async function poll(id){
    for(;;){
      const r=await fetch(`/api/analyses/${id}`),job=await r.json();
      if(!r.ok)throw new Error(job.detail||"Не удалось получить статус анализа.");
      setState(job.stage||"Проверяем документ…",true);
      if(job.status==="completed"){render(job.report);setState("Готово");return}
      if(job.status==="failed")throw new Error(job.error||"Анализ завершился с ошибкой.");
      await new Promise(resolve=>setTimeout(resolve,1200))
    }
  }
  async function analyze(){
    if(!selected||isAnalyzing)return;
    isAnalyzing=true;start.disabled=true;document.getElementById("remove").disabled=true;results.classList.add("hidden");clearError();setState("Загружаем файл…",true);
    const data=new FormData();data.append("document_type_id",typeId);data.append("file",selected);
    try{const r=await fetch("/api/analyses",{method:"POST",body:data}),job=await r.json();if(!r.ok)throw new Error(job.detail||"Не удалось начать анализ.");await poll(job.analysis_id)}
    catch(reason){fail(reason.message||"Произошла ошибка.")}
    finally{isAnalyzing=false;start.disabled=!selected;document.getElementById("remove").disabled=false}
  }
  fileInput.addEventListener("change",()=>selectFile(fileInput.files[0]));
  document.getElementById("remove").addEventListener("click",clearFile);
  start.addEventListener("click",analyze);
  drop.addEventListener("keydown",event=>{if((event.key==="Enter"||event.key===" ")&&!fileInput.disabled){event.preventDefault();fileInput.click()}});
  ["dragenter","dragover"].forEach(name=>drop.addEventListener(name,event=>{event.preventDefault();if(!fileInput.disabled)drop.classList.add("dragging")}));
  ["dragleave","drop"].forEach(name=>drop.addEventListener(name,event=>{event.preventDefault();drop.classList.remove("dragging")}));
  drop.addEventListener("drop",event=>{if(!fileInput.disabled)selectFile(event.dataTransfer.files[0])});
  filters.addEventListener("click",event=>{const button=event.target.closest(".filter");if(button)applyFilter(button.dataset.filter)});
  document.getElementById("download").addEventListener("click",()=>{const blob=new Blob([markdown],{type:"text/markdown;charset=utf-8"}),link=document.createElement("a");link.href=URL.createObjectURL(blob);link.download=`report-${selected?selected.name.replace(/\.[^.]+$/g,""):"contract"}.md`;link.click();URL.revokeObjectURL(link.href)});
  loadType().catch(error=>fail(error.message||"Не удалось загрузить профиль проверки."));
</script>
</body>
</html>"""
