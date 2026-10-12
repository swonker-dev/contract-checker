from __future__ import annotations

from .ui_layout import render_page


REGULATIONS_HTML = render_page(
    "Нормативная база",
    r"""<a class="back" href="/">← К проверке договора</a>
    <header class="hero">
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
        <button class="drop" id="drop" type="button" aria-describedby="drop-hint">
          <span><span class="upload-icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 16V4m-4 4 4-4 4 4M4 16v4h16v-4"/></svg></span><strong><span class="drop-link">Выберите файл</span> или перетащите его сюда</strong><span class="drop-hint" id="drop-hint">JSON в кодировке UTF-8 · до 2 МБ</span></span>
        </button>
        <input class="file-input" id="file" type="file" accept=".json,application/json" aria-label="Выберите нормативный источник">
        <div class="file-card hidden" id="file-card">
          <span class="file-type" aria-hidden="true">JSON</span>
          <div class="file-info"><div class="file-name" id="file-name"></div><div class="file-meta" id="file-meta"></div></div>
          <button class="quiet" id="remove" type="button" aria-label="Убрать выбранный файл">Убрать</button>
        </div>
        <div class="upload-actions"><button class="primary" id="upload" type="button" aria-describedby="upload-hint" disabled>Загрузить редакцию</button><span class="button-hint" id="upload-hint">Выберите JSON-файл</span></div>
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

    <p class="note">После изменения источников поисковый индекс автоматически обновится при следующей проверке. Страница не имеет авторизации и предназначена только для локального запуска.</p>""",
    r"""const MAX_FILE_SIZE=2*1024*1024;
    const fileInput=document.getElementById("file"),drop=document.getElementById("drop"),fileCard=document.getElementById("file-card"),uploadButton=document.getElementById("upload"),statusNode=document.getElementById("status"),activeNode=document.getElementById("active"),archivedNode=document.getElementById("archived");
    let selectedFile=null,isUploading=false;

    async function request(url,options){const response=await fetch(url,options),payload=await response.json();if(!response.ok)throw new Error(payload.detail||"Ошибка запроса");return payload}
    function add(parent,tag,className,text){const element=document.createElement(tag);if(className)element.className=className;element.textContent=text;parent.appendChild(element);return element}
    function formatBytes(bytes){return bytes<1024*1024?`${new Intl.NumberFormat("ru-RU").format(Math.max(1,Math.ceil(bytes/1024)))} КБ`:`${new Intl.NumberFormat("ru-RU",{maximumFractionDigits:1}).format(bytes/1024/1024)} МБ`}
    function formatDate(value){if(!value)return "Не указана";const date=new Date(`${value}T00:00:00`);return Number.isNaN(date.getTime())?value:new Intl.DateTimeFormat("ru-RU").format(date)}
    function showStatus(message,type="success"){statusNode.textContent=message;statusNode.className=`status ${type}`}
    function hideStatus(){statusNode.className="status hidden";statusNode.textContent=""}
    function updateControls(){
      fileInput.disabled=isUploading;drop.disabled=isUploading;uploadButton.disabled=isUploading||!selectedFile;document.getElementById("remove").disabled=isUploading;
      const hint=document.getElementById("upload-hint");hint.classList.toggle("hidden",Boolean(selectedFile)&&!isUploading);hint.textContent=isUploading?"Редакция загружается":"Выберите JSON-файл";
    }
    function resetFile(){selectedFile=null;fileInput.value="";fileCard.classList.add("hidden");updateControls()}
    function selectFile(file){
      if(isUploading)return;
      hideStatus();resetFile();
      if(!file||!file.name.toLowerCase().endsWith(".json")){showStatus("Выберите файл в формате JSON.","error");return}
      if(file.size>MAX_FILE_SIZE){showStatus("Файл больше 2 МБ. Выберите файл меньшего размера.","error");return}
      selectedFile=file;document.getElementById("file-name").textContent=file.name;document.getElementById("file-meta").textContent=`JSON · ${formatBytes(file.size)}`;fileCard.classList.remove("hidden");updateControls()
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
      if(isUploading)return;
      if(!selectedFile){showStatus("Сначала выберите JSON-файл.","error");return}
      isUploading=true;updateControls();showStatus("Проверяем структуру и загружаем редакцию…","loading");
      const form=new FormData();form.append("file",selectedFile);
      try{const source=await request("/api/regulations",{method:"POST",body:form});await loadSources();resetFile();showStatus(`Редакция «${source.source_title}» загружена и активна.`)}
      catch(error){showStatus(error.message,"error")}
      finally{isUploading=false;updateControls()}
    }
    fileInput.addEventListener("change",()=>selectFile(fileInput.files[0]));
    uploadButton.addEventListener("click",upload);
    document.getElementById("remove").addEventListener("click",()=>{resetFile();hideStatus()});
    drop.addEventListener("click",()=>fileInput.click());
    ["dragenter","dragover"].forEach(name=>drop.addEventListener(name,event=>{event.preventDefault();if(!isUploading)drop.classList.add("dragging")}));
    ["dragleave","drop"].forEach(name=>drop.addEventListener(name,event=>{event.preventDefault();drop.classList.remove("dragging")}));
    drop.addEventListener("drop",event=>selectFile(event.dataTransfer.files[0]));
    loadSources().catch(error=>showStatus(error.message,"error"));""",
    active="regulations",
)
