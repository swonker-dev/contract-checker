from __future__ import annotations

from .ui_layout import render_page


CATALOG_HTML = render_page(
    "Проверка договоров",
    r"""<header class="hero in-panel">
    <h1>Какой договор нужно проверить?</h1>
    <p class="lead">Выберите тип документа. Для каждого типа используется свой набор норм и правил проверки.</p>
  </header>
  <section class="panel" aria-labelledby="catalog-title">
    <div class="panel-head"><h2 id="catalog-title">Типы договоров</h2><span class="count">3 профиля</span></div>
    <div class="catalog" id="catalog" aria-live="polite"></div>
    <p class="description-note">Сейчас доступна проверка трудового договора. Остальные профили появятся после подготовки нормативной базы.</p>
    <div class="error hidden" id="error" role="alert"></div>
  </section>""",
    r"""const catalog = document.getElementById("catalog");
    const errorBox = document.getElementById("error");
    function add(parent, tag, className, text) { const el=document.createElement(tag); el.className=className; el.textContent=text; parent.appendChild(el); return el; }
    async function loadTypes() {
      try {
        const response = await fetch("/api/document-types");
        if (!response.ok) throw new Error("Не удалось загрузить каталог типов документов.");
        const types = await response.json();
        types.forEach(type => {
          const card=document.createElement("article"); card.className=`document-card${type.enabled ? "" : " disabled"}`;
          add(card,"span","catalog-status",type.enabled ? "Доступно" : "В разработке");
          add(card,"h3","",type.title); add(card,"p","description",type.description); add(card,"p","scope",type.scope);
          if (type.enabled) { const link=add(card,"a","action","Перейти к проверке"); link.href=`/check/${type.id}`; }
          else { const button=add(card,"button","action","Скоро"); button.type="button"; button.disabled=true; }
          catalog.appendChild(card);
        });
      } catch (reason) { errorBox.textContent=reason.message; errorBox.classList.remove("hidden"); }
    }
    loadTypes();""",
    active="catalog",
)


CHECK_HTML = render_page(
    "Проверка договора",
    r"""<a class="back" href="/" aria-label="Вернуться к выбору типа договора">← Все типы договоров</a>
  <header class="hero">
    <h1 id="title">Загрузка профиля…</h1>
    <p class="lead" id="description"></p>
    <p class="scope" id="scope"></p>
  </header>

  <div class="workspace">
    <section class="panel" aria-label="Загрузка документа">
      <h2>Загрузите договор</h2>
      <button class="drop" id="drop" type="button" aria-describedby="drop-hint" disabled>
        <span>
          <span class="file-icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 16V4m-4 4 4-4 4 4M4 16v4h16v-4"/></svg></span>
          <strong><span class="choose">Выберите файл</span> или перетащите его сюда</strong>
          <span class="drop-hint" id="drop-hint">DOCX или PDF с текстовым слоем · до 10 МБ</span>
        </span>
      </button>
      <input class="file-input" id="file" type="file" accept=".docx,.pdf" aria-label="Выберите договор" disabled>
      <div class="file-card hidden" id="file-card">
        <span class="file-type" id="file-type" aria-hidden="true"></span>
        <div class="file-info"><div class="file-name" id="filename"></div><div class="file-meta" id="file-meta"></div></div>
        <button class="remove" id="remove" type="button" aria-label="Убрать выбранный файл">Убрать</button>
      </div>
      <div class="actions">
        <button class="primary" id="start" type="button" aria-describedby="start-hint" disabled>Проверить договор</button>
        <span class="button-hint" id="start-hint">Выберите файл, чтобы начать</span>
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
      <div class="metric"><strong id="total-count">0</strong><span>пунктов в документе</span></div>
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
  </section>""",
    r"""const typeId=decodeURIComponent(location.pathname.split("/").filter(Boolean).pop());
  const MAX_FILE_SIZE=10*1024*1024;
  const allowedExtensions=["docx","pdf"];
  const fileInput=document.getElementById("file"), drop=document.getElementById("drop"), fileCard=document.getElementById("file-card"), start=document.getElementById("start"), state=document.getElementById("state"), errorBox=document.getElementById("error"), results=document.getElementById("results"), findings=document.getElementById("findings"), filters=document.getElementById("filters"), filterEmpty=document.getElementById("filter-empty");
  let selected=null, markdown="", isAnalyzing=false, profileEnabled=false;

  function add(parent,tag,className,text){const el=document.createElement(tag);if(className)el.className=className;el.textContent=text;parent.appendChild(el);return el}
  function formatBytes(bytes){return bytes<1024*1024?`${new Intl.NumberFormat("ru-RU").format(Math.max(1,Math.ceil(bytes/1024)))} КБ`:`${new Intl.NumberFormat("ru-RU",{maximumFractionDigits:1}).format(bytes/1024/1024)} МБ`}
  function updateControls(){
    fileInput.disabled=!profileEnabled||isAnalyzing;drop.disabled=fileInput.disabled;
    start.disabled=!profileEnabled||!selected||isAnalyzing;document.getElementById("remove").disabled=isAnalyzing;
    const hint=document.getElementById("start-hint");hint.classList.toggle("hidden",Boolean(selected)&&profileEnabled&&!isAnalyzing);
    hint.textContent=isAnalyzing?"Проверка выполняется":profileEnabled?"Выберите файл, чтобы начать":"Профиль проверки недоступен";
  }
  function setState(message,busy=false){state.replaceChildren();state.classList.toggle("busy",busy);if(busy)add(state,"span","spinner","");if(message)add(state,"span","",message)}
  function fail(message){errorBox.textContent=message;errorBox.classList.remove("hidden");setState("")}
  function clearError(){errorBox.classList.add("hidden");errorBox.textContent=""}
  function fileExtension(file){return file?.name.toLowerCase().split(".").pop()||""}
  function clearFile(){selected=null;fileInput.value="";fileCard.classList.add("hidden");results.classList.add("hidden");clearError();setState("");updateControls()}
  function selectFile(file){
    if(isAnalyzing||!profileEnabled)return;
    clearError();results.classList.add("hidden");
    const extension=fileExtension(file);
    if(!file||!allowedExtensions.includes(extension)){clearFile();fail("Выберите файл в формате DOCX или PDF.");return}
    if(file.size>MAX_FILE_SIZE){clearFile();fail("Файл больше 10 МБ. Выберите документ меньшего размера.");return}
    selected=file;
    document.getElementById("filename").textContent=file.name;
    document.getElementById("file-meta").textContent=`${extension.toUpperCase()} · ${formatBytes(file.size)}`;
    document.getElementById("file-type").textContent=extension.toUpperCase();
    fileCard.classList.remove("hidden");setState("");updateControls();
  }
  async function loadType(){
    const r=await fetch(`/api/document-types/${typeId}`);
    if(!r.ok){fail("Тип документа не найден.");start.disabled=true;return}
    const type=await r.json();
    document.title=`Проверка: ${type.title} — ViWork`;
    document.getElementById("title").textContent=type.title;
    document.getElementById("description").textContent=type.description;
    document.getElementById("scope").textContent=`Область проверки: ${type.scope}`;
    profileEnabled=type.enabled;
    if(!profileEnabled)fail("Этот тип документа пока недоступен.");
    updateControls();
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
    isAnalyzing=true;updateControls();results.classList.add("hidden");clearError();setState("Загружаем файл…",true);
    const data=new FormData();data.append("document_type_id",typeId);data.append("file",selected);
    try{const r=await fetch("/api/analyses",{method:"POST",body:data}),job=await r.json();if(!r.ok)throw new Error(job.detail||"Не удалось начать анализ.");await poll(job.analysis_id)}
    catch(reason){fail(reason.message||"Произошла ошибка.")}
    finally{isAnalyzing=false;updateControls()}
  }
  fileInput.addEventListener("change",()=>selectFile(fileInput.files[0]));
  document.getElementById("remove").addEventListener("click",clearFile);
  start.addEventListener("click",analyze);
  drop.addEventListener("click",()=>fileInput.click());
  ["dragenter","dragover"].forEach(name=>drop.addEventListener(name,event=>{event.preventDefault();if(!fileInput.disabled)drop.classList.add("dragging")}));
  ["dragleave","drop"].forEach(name=>drop.addEventListener(name,event=>{event.preventDefault();drop.classList.remove("dragging")}));
  drop.addEventListener("drop",event=>{if(!fileInput.disabled)selectFile(event.dataTransfer.files[0])});
  filters.addEventListener("click",event=>{const button=event.target.closest(".filter");if(button)applyFilter(button.dataset.filter)});
  document.getElementById("download").addEventListener("click",()=>{const blob=new Blob([markdown],{type:"text/markdown;charset=utf-8"}),link=document.createElement("a");link.href=URL.createObjectURL(blob);link.download=`report-${selected?selected.name.replace(/\.[^.]+$/g,""):"contract"}.md`;link.click();URL.revokeObjectURL(link.href)});
  loadType().catch(error=>fail(error.message||"Не удалось загрузить профиль проверки."));""",
    active="catalog",
)
