const $=(s)=>document.querySelector(s);
const $$=(s)=>document.querySelectorAll(s);
let latestTelemetry={};

function toast(text){const el=$("#toast");el.textContent=text;el.classList.add("show");setTimeout(()=>el.classList.remove("show"),2400)}
function escapeHtml(text){const d=document.createElement("div");d.textContent=text||"";return d.innerHTML}
function switchView(name){
 $$(".view").forEach(v=>v.classList.toggle("active",v.id===name));
 $$(".nav-item").forEach(v=>v.classList.toggle("active",v.dataset.view===name));
 $("#page-title").textContent=name[0].toUpperCase()+name.slice(1).replace("chat","chat").replace("documents","Documents");
 $("#eyebrow").textContent=name==="dashboard"?"Overview":"NeuroRAG workspace";
 if(name==="dashboard")refreshDashboard();
 if(name==="documents")loadDocuments();
 if(name==="memories")loadMemories();
 if(name==="performance")refreshDashboard();
 if(name==="settings")loadSettings();
}
$$(".nav-item").forEach(b=>b.addEventListener("click",()=>switchView(b.dataset.view)));
$$("[data-action]").forEach(b=>b.addEventListener("click",()=>switchView(b.dataset.action)));

async function api(path,options={}){const r=await fetch(path,options);let body;try{body=await r.json()}catch{body={}}if(!r.ok)throw new Error(body.detail||`Request failed (${r.status})`);return body}

async function refreshDashboard(){
 try{
  const [status,memories,documents]=await Promise.all([
   api("/api/status"),
   api("/api/users/"+encodeURIComponent($("#chat-user").value||"usr_99")+"/memories"),
   api("/api/documents")
  ]);
  $("#status-dot").parentElement.classList.add("online");$("#status-text").textContent="Backend online";
  $("#metric-documents").textContent=documents.length;
  $("#metric-conversations").textContent=status.telemetry.conversation_count;
  $("#metric-memories").textContent=memories.length;
  $("#metric-latency").textContent=Math.round(status.telemetry.total_latency_ms)+" ms";
  const rows=[
   ["Retrieval",status.telemetry.retrieval_latency_ms],
   ["Reranking",status.telemetry.rerank_latency_ms],
   ["Generation",status.telemetry.generation_latency_ms],
   ["Total",status.telemetry.total_latency_ms]
  ];
  $("#dashboard-bars").innerHTML=rows.map(([n,v])=>`<div class="bar-row"><span>${n}</span><div class="bar-track"><div class="bar-fill" style="width:${Math.min(100,v/10||2)}%"></div></div><b>${Math.round(v)} ms</b></div>`).join("");
  latestTelemetry=status.telemetry;
  renderPerformance(status.telemetry);
 }catch(e){$("#status-dot").parentElement.classList.remove("online");$("#status-text").textContent="Backend offline";toast(e.message)}
}

function appendMessage(role,text){
 const box=$("#messages");const empty=box.querySelector(".empty");if(empty)empty.remove();
 const div=document.createElement("div");div.className="message "+role;div.textContent=text;box.appendChild(div);box.scrollTop=box.scrollHeight;
}
$("#send-chat").addEventListener("click",sendChat);
$("#chat-query").addEventListener("keydown",e=>{if(e.key==="Enter")sendChat()});
async function sendChat(){
 const query=$("#chat-query").value.trim();if(!query)return;
 appendMessage("user",query);$("#chat-query").value="";
 const send=$("#send-chat");send.disabled=true;send.textContent="Thinking...";
 appendMessage("assistant","Thinking...");
 try{
  const body=await api("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query,user_id:$("#chat-user").value.trim(),session_id:$("#chat-session").value.trim()})});
  const items=$("#messages").querySelectorAll(".assistant");items[items.length-1].textContent=body.answer;
  $("#chat-memories").innerHTML=body.memories_used.length?body.memories_used.map(m=>`<div>${escapeHtml(m.fact)}</div>`).join(""):"None";
  $("#chat-sources").innerHTML=body.sources.length?body.sources.map(s=>`<div class="mini-source"><strong>${escapeHtml(s.title)}</strong><br>${escapeHtml(s.text).slice(0,180)}</div>`).join(""):"No retrieved sources";
  latestTelemetry=body.telemetry;renderPerformance(body.telemetry);refreshDashboard();
 }catch(e){const items=$("#messages").querySelectorAll(".assistant");items[items.length-1].textContent="Error: "+e.message}
 finally{send.disabled=false;send.textContent="Send"}
}
$("#clear-chat").addEventListener("click",()=>{$("#messages").innerHTML='<div class="empty">Ask a question about your indexed documents.</div>';$("#chat-memories").textContent="None";$("#chat-sources").textContent="None"});

async function uploadFile(file){
 if(!file)return;
 const fd=new FormData();fd.append("file",file);
 try{await api("/api/documents/upload",{method:"POST",body:fd});toast(file.name+" indexed");loadDocuments();refreshDashboard()}catch(e){toast(e.message)}
}
$("#document-file").addEventListener("change",e=>uploadFile(e.target.files[0]));
const drop=$("#drop-zone");["dragenter","dragover"].forEach(n=>drop.addEventListener(n,e=>{e.preventDefault();drop.classList.add("drag")}));
["dragleave","drop"].forEach(n=>drop.addEventListener(n,e=>{e.preventDefault();drop.classList.remove("drag")}));
drop.addEventListener("drop",e=>uploadFile(e.dataTransfer.files[0]));
$("#document-search").addEventListener("input",loadDocuments);
async function loadDocuments(){
 try{
  const docs=await api("/api/documents");const term=$("#document-search").value.toLowerCase();
  const filtered=docs.filter(d=>d.title.toLowerCase().includes(term));
  $("#document-list").innerHTML=filtered.length?filtered.map(d=>`<div class="document-card"><div><strong>${escapeHtml(d.title)}</strong><br><small>${d.chunk_count} chunks · ${escapeHtml(d.status)}</small></div><button class="delete-memory" data-delete-document="${escapeHtml(d.id)}">Delete</button></div>`).join(""):"<div class='panel'>No documents found. Upload a PDF or TXT file.</div>";
  $$("[data-delete-document]").forEach(b=>b.addEventListener("click",async()=>{if(confirm("Delete this document?")){try{await api("/api/documents/"+encodeURIComponent(b.dataset.deleteDocument),{method:"DELETE"});loadDocuments();refreshDashboard()}catch(e){toast(e.message)}}}));
 }catch(e){toast(e.message)}
}

$("#load-memories").addEventListener("click",loadMemories);
async function loadMemories(){
 const user=$("#memory-user").value.trim();if(!user)return;
 try{
  const memories=await api("/api/users/"+encodeURIComponent(user)+"/memories");
  $("#memory-list").innerHTML=memories.length?memories.map(m=>`<div class="memory-card"><div><strong>${escapeHtml(m.fact)}</strong><br><small>${escapeHtml(m.category)} · session ${escapeHtml(m.source_session||"unknown")}</small></div><button class="delete-memory" data-memory="${m.id}">Delete</button></div>`).join(""):"<div class='panel'>No memories saved for this user.</div>";
  $$("[data-memory]").forEach(b=>b.addEventListener("click",async()=>{if(confirm("Delete this memory?")){try{await api(`/api/users/${encodeURIComponent(user)}/memories/${b.dataset.memory}`,{method:"DELETE"});loadMemories();refreshDashboard()}catch(e){toast(e.message)}}}));
 }catch(e){toast(e.message)}
}

function renderPerformance(t){
 $("#performance-metrics").innerHTML=[
  ["Retrieval",t.retrieval_latency_ms+" ms"],["Reranking",t.rerank_latency_ms+" ms"],["Generation",t.generation_latency_ms+" ms"],["Total",t.total_latency_ms+" ms"]
 ].map(([n,v])=>`<article><p>${n}</p><strong>${v}</strong></article>`).join("");
 $("#telemetry-detail").innerHTML=[
  ["Retrieved candidates",t.retrieved_candidates||0],["Compressed documents",t.compressed_documents||0],["Final context documents",t.final_context_documents||0]
 ].map(([n,v])=>`<div><small>${n}</small><strong>${v}</strong></div>`).join("");
}
async function loadSettings(){
 try{
  const h=await api("/health");
  const cards=[
   ["Backend connection","Online"],["Environment mode",h.environment],["LLM provider",h.providers.llm],["Embedding provider",h.providers.embedding],["Reranking provider",h.providers.rerank],["Memory provider",h.providers.memory],["Vector database",h.providers.vector]
  ];
  $("#settings-grid").innerHTML=cards.map(([n,v])=>`<div class="setting-card"><small>${n}</small><strong>${escapeHtml(v)}</strong></div>`).join("");
 }catch(e){toast(e.message)}
}
refreshDashboard();
