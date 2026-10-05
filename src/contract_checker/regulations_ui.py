from __future__ import annotations


REGULATIONS_HTML = r"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Нормативная база</title>
  <style>
    :root {
      color-scheme:light;
      --bg:#f3f4ef;
      --surface:#fffef9;
      --surface-strong:#fff;
      --text:#19231f;
      --muted:#65706b;
      --line:#d8ddd8;
      --green:#176b52;
      --green-dark:#0f4c3a;
      --green-soft:#edf7f1;
      --red:#9a342a;
      --red-soft:#fff0ed;
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
    a { color:var(--green); font-weight:750; text-decoration:none; }
    a:hover { color:var(--green-dark); }
    button,a,.drop { -webkit-tap-highlight-color:transparent; }
    button:focus-visible,a:focus-visible,.drop:focus-visible { outline:3px solid rgba(23,107,82,.22); outline-offset:3px; }
    main { width:min(1040px,calc(100% - 32px)); margin:auto; padding:34px 0 72px; }
    .back { display:inline-flex; min-height:40px; align-items:center; gap:8px; }
    .hero { max-width:810px; margin-top:22px; }
    .eyebrow { margin:0 0 12px; color:var(--green); font-size:12px; font-weight:850; letter-spacing:.1em; text-transform:uppercase; }
    h1 { margin:0 0 14px; font:500 clamp(40px,7vw,64px)/1.03 Georgia,serif; letter-spacing:-.035em; }
    .lead { max-width:760px; margin:0; color:var(--muted); font-size:18px; line-height:1.6; }
    .stats { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-top:30px; }
    .stat { padding:17px 18px; border:1px solid var(--line); border-radius:15px; background:rgba(255,254,249,.82); }
    .stat strong { display:block; font:500 31px/1 Georgia,serif; }
    .stat span { display:block; margin-top:7px; color:var(--muted); font-size:12px; }
    .upload-panel { display:grid; grid-template-columns:minmax(0,1fr) 280px; gap:20px; margin-top:20px; padding:22px; border:1px solid var(--line); border-radius:22px; background:rgba(255,254,249,.96); box-shadow:var(--shadow); }
    .panel-head { display:flex; align-items:center; justify-content:space-between; gap:16px; margin-bottom:14px; }
    .panel-head h2 { margin:0; font:750 18px/1.3 Inter,"Segoe UI",sans-serif; }
    .format-badge { padding:5px 9px; border-radius:99px; background:var(--green-soft); color:var(--green-dark); font-size:11px; font-weight:850; letter-spacing:.04em; }
    .drop {
      display:grid;
      min-height:170px;
      place-items:center;
      padding:24px;
      border:1.5px dashed #aab5ae;
      border-radius:15px;
      background:#fafbf7;
      text-align:center;
      cursor:pointer;
      transition:border-color 160ms ease,background 160ms ease,transform 160ms ease;
    }
    .drop:hover,.drop.dragging { border-color:var(--green); background:#f2faf6; transform:translateY(-1px); }
    .upload-icon { display:grid; width:50px; height:58px; margin:0 auto 14px; place-items:center; border:2px solid var(--green); border-radius:8px; color:var(--green); font-size:11px; font-weight:850; }
    .drop strong { display:block; font-size:16px; }
    .drop-link { color:var(--green); text-decoration:underline; text-underline-offset:3px; }
    .drop-hint { display:block; margin-top:7px; color:var(--muted); font-size:13px; line-height:1.45; }
    input[type=file] { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap; }
    .file-card { display:flex; align-items:center; gap:12px; margin-top:12px; padding:12px 13px; border:1px solid var(--line); border-radius:12px; background:var(--surface-strong); }
    .file-type { display:grid; width:38px; height:38px; flex:none; place-items:center; border-radius:9px; background:var(--green-soft); color:var(--green); font-size:10px; font-weight:850; }
    .file-info { min-width:0; flex:1; }
    .file-name { overflow:hidden; font-size:14px; font-weight:750; text-overflow:ellipsis; white-space:nowrap; }
    .file-meta { margin-top:3px; color:var(--muted); font-size:12px; }
    .upload-actions { display:flex; align-items:center; gap:10px; margin-top:14px; }
    button { min-height:44px; padding:0 17px; border:0; border-radius:10px; font-weight:750; cursor:pointer; transition:background 160ms ease,transform 160ms ease,opacity 160ms ease; }
    button:hover:not(:disabled) { transform:translateY(-1px); }
    button:disabled { cursor:not-allowed; opacity:.5; }
    .primary { background:var(--green); color:#fff; }
    .primary:hover:not(:disabled) { background:var(--green-dark); }
    .quiet { min-height:36px; padding:0 10px; background:transparent; color:var(--muted); }
    .quiet:hover:not(:disabled) { background:#f1f2ee; color:var(--text); }
    .requirements { padding:18px; border-radius:15px; background:var(--green-soft); }
    .requirements h3 { margin:0 0 12px; font-size:15px; }
    .requirements ul { display:grid; gap:9px; margin:0; padding:0; list-style:none; }
    .requirements li { position:relative; padding-left:20px; color:#46514c; font-size:13px; line-height:1.45; }
    .requirements li::before { position:absolute; left:0; content:"✓"; color:var(--green); font-weight:850; }
    .requirements code { padding:2px 5px; border-radius:5px; background:rgba(255,255,255,.66); font:12px ui-monospace,SFMono-Regular,Menlo,monospace; }
    .status { display:flex; align-items:flex-start; gap:9px; margin-top:14px; padding:12px 14px; border-radius:11px; background:var(--green-soft); color:var(--green-dark); font-size:14px; line-height:1.45; }
    .status::before { content:"✓"; font-weight:850; }
    .status.error { background:var(--red-soft); color:var(--red); }
    .status.error::before { content:"!"; }
    .status.loading { background:#f0f1ed; color:var(--muted); }
    .status.loading::before { content:"…"; }
    .section { margin-top:42px; }
    .section-head { display:flex; align-items:end; justify-content:space-between; gap:16px; margin-bottom:14px; }
    .section h2 { margin:0; font:500 32px/1.15 Georgia,serif; }
    .section-description { margin:7px 0 0; color:var(--muted); font-size:14px; line-height:1.5; }
    .count { flex:none; padding:6px 10px; border-radius:99px; background:#e9ece8; color:var(--muted); font-size:12px; font-weight:800; }
    .source-list { display:grid; gap:12px; }
    .source { display:grid; grid-template-columns:auto minmax(0,1fr) auto; gap:16px; padding:19px; border:1px solid var(--line); border-radius:15px; background:var(--surface); }
    .source.active { border-left:4px solid var(--green); }
    .source.archived { background:rgba(255,254,249,.62); }
    .source-icon { display:grid; width:42px; height:48px; place-items:center; border-radius:10px; background:var(--green-soft); color:var(--green); font:500 21px Georgia,serif; }
    .archived .source-icon { background:#eceeea; color:#6d715f; }
    .source-title-row { display:flex; align-items:center; flex-wrap:wrap; gap:8px; }
    .source h3 { margin:0; font-size:17px; line-height:1.35; }
    .badge { padding:4px 8px; border-radius:999px; background:var(--green-soft); color:var(--green-dark); font-size:10px; font-weight:850; letter-spacing:.04em; text-transform:uppercase; }
    .archived .badge { background:#eceeea; color:var(--muted); }
    .metadata { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:13px; margin-top:14px; }
    .meta-item span { display:block; color:var(--muted); font-size:11px; }
    .meta-item strong { display:block; margin-top:3px; overflow-wrap:anywhere; font-size:13px; line-height:1.4; }
    .source-link { display:inline-flex; margin-top:13px; align-items:center; gap:5px; font-size:13px; }
    .technical { margin-top:10px; color:var(--muted); font-size:12px; }
    .technical summary { cursor:pointer; }
    .technical code { display:block; margin-top:6px; overflow-wrap:anywhere; }
    .source-action { align-self:center; white-space:nowrap; }
    .archive-button { background:var(--red-soft); color:var(--red); }
    .archive-button:hover:not(:disabled) { background:#fbe2de; }
    .activate-button { border:1px solid #b9d8ca; background:var(--green-soft); color:var(--green-dark); }
    .activate-button:hover:not(:disabled) { background:#dff1e7; }
    .empty { padding:24px; border:1px dashed #c5cbc6; border-radius:14px; background:rgba(255,254,249,.5); color:var(--muted); text-align:center; line-height:1.5; }
    .note { margin-top:32px; padding-top:20px; border-top:1px solid var(--line); color:var(--muted); font-size:13px; line-height:1.55; }
    .hidden { display:none!important; }
    @media(prefers-reduced-motion:reduce){ * { scroll-behavior:auto!important; transition:none!important; } }
    @media(max-width:780px){ .upload-panel{grid-template-columns:1fr}.requirements{display:none}.metadata{grid-template-columns:repeat(2,minmax(0,1fr))} }
    @media(max-width:620px){ main{padding-top:22px}.hero{margin-top:14px}.stats{grid-template-columns:1fr}.stat{display:flex;align-items:center;justify-content:space-between}.stat span{margin:0}.upload-panel{padding:15px;border-radius:17px}.drop{min-height:160px}.upload-actions{align-items:stretch;flex-direction:column}.upload-actions button{width:100%}.section{margin-top:34px}.source{grid-template-columns:auto minmax(0,1fr)}.source-action{grid-column:1/-1;width:100%}.metadata{grid-template-columns:1fr}.section-head{align-items:flex-start}.source-icon{width:38px;height:43px} }
  </style>
</head>
<body>
  <main>
    <a class="back" href="/">← К проверке договора</a>
    <header class="hero">
      <p class="eyebrow">Управление источниками</p>
      <h1>Нормативная база</h1>
      <p class="lead">Здесь хранятся нормы, по которым система проверяет договоры. Активная редакция участвует в анализе, архивные можно восстановить в любой момент.</p>
    </header>

    <section class="stats" aria-label="Состояние нормативной базы">
      <div class="stat"><strong id="active-total">—</strong><span>активных источников</span></div>
      <div class="stat"><strong id="chunks-total">—</strong><span>фрагментов в проверке</span></div>
      <div class="stat"><strong id="archived-total">—</strong><span>редакций в архиве</span></div>
    </section>

    <section class="upload-panel" aria-labelledby="upload-title">
      <div>
        <div class="panel-head"><h2 id="upload-title">Добавить новую редакцию</h2><span class="format-badge">JSON</span></div>
        <label class="drop" id="drop" for="file" tabindex="0" role="button" aria-describedby="drop-hint">
          <span><span class="upload-icon" aria-hidden="true">JSON</span><strong><span class="drop-link">Выберите файл</span> или перетащите его сюда</strong><span class="drop-hint" id="drop-hint">JSON в кодировке UTF-8 · до 2 МБ</span></span>
        </label>
        <input id="file" type="file" accept=".json,application/json">
        <div class="file-card hidden" id="file-card">
          <span class="file-type" aria-hidden="true">JSON</span>
          <div class="file-info"><div class="file-name" id="file-name"></div><div class="file-meta" id="file-meta"></div></div>
          <button class="quiet" id="remove" type="button" aria-label="Убрать выбранный файл">Убрать</button>
        </div>
        <div class="upload-actions"><button class="primary" id="upload" type="button" disabled>Загрузить редакцию</button></div>
        <div class="status hidden" id="status" role="status" aria-live="polite"></div>
      </div>
      <aside class="requirements">
        <h3>Что должно быть в файле</h3>
        <ul>
          <li>Уникальный идентификатор <code>source_id</code></li>
          <li>Название источника и дата редакции</li>
          <li>Непустой список нормативных фрагментов</li>
          <li>Новая редакция заменит текущую с тем же ID</li>
        </ul>
      </aside>
    </section>

    <section class="section" aria-labelledby="active-title">
      <div class="section-head"><div><h2 id="active-title">Активные источники</h2><p class="section-description">Используются при следующей проверке договора.</p></div><span class="count" id="active-count">0</span></div>
      <div class="source-list" id="active" aria-live="polite"></div>
    </section>

    <section class="section" aria-labelledby="archived-title">
      <div class="section-head"><div><h2 id="archived-title">Архив редакций</h2><p class="section-description">Не участвуют в проверке, но доступны для восстановления.</p></div><span class="count" id="archived-count">0</span></div>
      <div class="source-list" id="archived" aria-live="polite"></div>
    </section>

    <p class="note">После изменения источников поисковый индекс автоматически обновится при следующей проверке. Страница не имеет авторизации и предназначена только для локального запуска.</p>
  </main>
  <script>
    const MAX_FILE_SIZE=2*1024*1024;
    const fileInput=document.getElementById("file"),drop=document.getElementById("drop"),fileCard=document.getElementById("file-card"),uploadButton=document.getElementById("upload"),statusNode=document.getElementById("status"),activeNode=document.getElementById("active"),archivedNode=document.getElementById("archived");
    let selectedFile=null;

    async function request(url,options){const response=await fetch(url,options),payload=await response.json();if(!response.ok)throw new Error(payload.detail||"Ошибка запроса");return payload}
    function add(parent,tag,className,text){const element=document.createElement(tag);if(className)element.className=className;element.textContent=text;parent.appendChild(element);return element}
    function formatBytes(bytes){return bytes<1024*1024?`${Math.max(1,Math.ceil(bytes/1024))} КБ`:`${(bytes/1024/1024).toFixed(1)} МБ`}
    function formatDate(value){if(!value)return "Не указана";const date=new Date(`${value}T00:00:00`);return Number.isNaN(date.getTime())?value:new Intl.DateTimeFormat("ru-RU").format(date)}
    function showStatus(message,type="success"){statusNode.textContent=message;statusNode.className=`status ${type}`}
    function hideStatus(){statusNode.className="status hidden";statusNode.textContent=""}
    function resetFile(){selectedFile=null;fileInput.value="";fileCard.classList.add("hidden");uploadButton.disabled=true}
    function selectFile(file){
      hideStatus();resetFile();
      if(!file||!file.name.toLowerCase().endsWith(".json")){showStatus("Выберите файл в формате JSON.","error");return}
      if(file.size>MAX_FILE_SIZE){showStatus("Файл больше 2 МБ. Выберите файл меньшего размера.","error");return}
      selectedFile=file;document.getElementById("file-name").textContent=file.name;document.getElementById("file-meta").textContent=`JSON · ${formatBytes(file.size)}`;fileCard.classList.remove("hidden");uploadButton.disabled=false
    }
    function metaItem(parent,label,value){const item=add(parent,"div","meta-item","");add(item,"span","",label);add(item,"strong","",value);return item}
    function sourceCard(source){
      const card=document.createElement("article");card.className=`source ${source.active?"active":"archived"}`;
      add(card,"span","source-icon","§");
      const body=add(card,"div","source-body","");
      const titleRow=add(body,"div","source-title-row","");add(titleRow,"h3","",source.source_title);add(titleRow,"span","badge",source.active?"Активен":"В архиве");
      const metadata=add(body,"div","metadata","");metaItem(metadata,"Редакция",formatDate(source.edition_date));metaItem(metadata,"Действует с",formatDate(source.effective_from));metaItem(metadata,"Фрагментов",String(source.chunks_count));
      if(source.source_url){const link=add(body,"a","source-link","Открыть первоисточник ↗");link.href=source.source_url;link.target="_blank";link.rel="noreferrer"}
      const details=add(body,"details","technical","");add(details,"summary","","Технические данные");add(details,"code","",`ID: ${source.source_id} · ${source.filename}`);
      const button=add(card,"button",`source-action ${source.active?"archive-button":"activate-button"}`,source.active?"В архив":"Сделать активным");button.type="button";
      button.addEventListener("click",async()=>{
        const question=source.active?`Переместить «${source.source_title}» в архив? Источник перестанет участвовать в проверке.`:`Сделать редакцию «${source.source_title}» активной? Текущая редакция с тем же ID будет архивирована.`;
        if(!window.confirm(question))return;
        button.disabled=true;showStatus(source.active?"Перемещаем источник в архив…":"Активируем редакцию…","loading");
        try{await request(`/api/regulations/${encodeURIComponent(source.filename)}/${source.active?"archive":"activate"}`,{method:"POST"});await loadSources();showStatus(source.active?"Источник перемещён в архив.":"Редакция активирована.")}
        catch(error){showStatus(error.message,"error")}
        finally{button.disabled=false}
      });
      return card
    }
    function renderGroup(node,items,emptyMessage){node.replaceChildren();if(!items.length){add(node,"div","empty",emptyMessage);return}items.forEach(item=>node.appendChild(sourceCard(item)))}
    function renderSummary(active,archived){document.getElementById("active-total").textContent=active.length;document.getElementById("chunks-total").textContent=active.reduce((sum,item)=>sum+item.chunks_count,0);document.getElementById("archived-total").textContent=archived.length;document.getElementById("active-count").textContent=active.length;document.getElementById("archived-count").textContent=archived.length}
    async function loadSources(){
      const sources=await request("/api/regulations"),active=sources.filter(item=>item.active),archived=sources.filter(item=>!item.active);
      renderSummary(active,archived);renderGroup(activeNode,active,"Активных источников пока нет. Загрузите первую редакцию выше.");renderGroup(archivedNode,archived,"Архив пуст — здесь появятся предыдущие редакции.")
    }
    async function upload(){
      if(!selectedFile){showStatus("Сначала выберите JSON-файл.","error");return}
      uploadButton.disabled=true;document.getElementById("remove").disabled=true;showStatus("Проверяем структуру и загружаем редакцию…","loading");
      const form=new FormData();form.append("file",selectedFile);
      try{const source=await request("/api/regulations",{method:"POST",body:form});await loadSources();resetFile();showStatus(`Редакция «${source.source_title}» загружена и активна.`)}
      catch(error){showStatus(error.message,"error")}
      finally{uploadButton.disabled=!selectedFile;document.getElementById("remove").disabled=false}
    }
    fileInput.addEventListener("change",()=>selectFile(fileInput.files[0]));
    uploadButton.addEventListener("click",upload);
    document.getElementById("remove").addEventListener("click",()=>{resetFile();hideStatus()});
    drop.addEventListener("keydown",event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();fileInput.click()}});
    ["dragenter","dragover"].forEach(name=>drop.addEventListener(name,event=>{event.preventDefault();drop.classList.add("dragging")}));
    ["dragleave","drop"].forEach(name=>drop.addEventListener(name,event=>{event.preventDefault();drop.classList.remove("dragging")}));
    drop.addEventListener("drop",event=>selectFile(event.dataTransfer.files[0]));
    loadSources().catch(error=>showStatus(error.message,"error"));
  </script>
</body>
</html>
"""
