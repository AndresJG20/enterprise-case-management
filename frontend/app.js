const $ = id => document.getElementById(id);
let token = null, user = null, offset = 0, total = 0;
const limit = 20;
const owners = new Map();
const transitions = {OPEN:["IN_PROGRESS"], IN_PROGRESS:["OPEN","RESOLVED"], RESOLVED:["IN_PROGRESS"]};

async function api(path, method = "GET", body) {
    const headers = {"Content-Type":"application/json"};
    if (token) headers.Authorization = "Bearer " + token;
    const response = await fetch("/api" + path, {method, headers, body:body === undefined ? undefined : JSON.stringify(body)});
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        if (response.status === 401 && token) clearSession();
        throw new Error(typeof error.detail === "string" ? error.detail : "Solicitud inválida ("+response.status+")");
    }
    return response.status === 204 ? null : response.json();
}
function clearSession() {
    token = null; user = null; offset = 0;
    $("workspace").hidden = true; $("loginPanel").hidden = false; $("logout").hidden = true;
}
function report(error) { $("notice").textContent = error.message; }
function cell(row,value) { const td = row.insertCell(); td.textContent = value; return td; }
async function refreshUsers() {
    owners.clear(); $("owners").replaceChildren();
    for (const item of await api("/users")) {
        owners.set(item.id,item.username);
        $("owners").add(new Option(item.username,item.id));
    }
}
async function refresh() {
    const filters = new FormData($("filter"));
    const q = new URLSearchParams({offset,limit});
    for (const [key,value] of filters) if (value) q.set(key,value);
    const [data, metrics] = await Promise.all([api("/cases?"+q),api("/metrics")]);
    total = data.total;
    $("metrics").replaceChildren();
    for (const [label,key] of [["Total","total"],["Abiertos","OPEN"],["En proceso","IN_PROGRESS"],["Resueltos","RESOLVED"]]) {
        const box = document.createElement("div"); box.className = "metric"; box.textContent = label;
        const count = document.createElement("strong"); count.textContent = metrics[key]; box.append(count); $("metrics").append(box);
    }
    $("rows").replaceChildren();
    for (const item of data.items) {
        const row = $("rows").insertRow();
        cell(row,item.id); cell(row,item.title); cell(row,owners.get(item.owner_id) ?? item.owner_id); cell(row,item.priority);
        const select = document.createElement("select");
        select.setAttribute("aria-label","Estado del caso "+item.id);
        for (const state of [item.status,...transitions[item.status]]) select.add(new Option(state,state));
        select.onchange = async () => {
            try { await api("/cases/"+item.id,"PATCH",{status:select.value,version:item.version}); await refresh(); }
            catch(e) { report(e); select.value = item.status; }
        };
        row.insertCell().append(select);
        const button = document.createElement("button"); button.textContent = "Ver";
        button.onclick = async () => {
            try {
                const events = await api("/cases/"+item.id+"/audit");
                $("history").replaceChildren();
                for (const event of events) { const li = document.createElement("li"); li.textContent = event.created_at+" — "+event.action+" — "+event.detail; $("history").append(li); }
                $("historyPanel").hidden = false;
            } catch(e) { report(e); }
        };
        row.insertCell().append(button);
    }
    $("page").textContent = (total ? offset+1 : 0)+"–"+Math.min(offset+limit,total)+" de "+total;
    $("prev").disabled = offset === 0; $("next").disabled = offset+limit >= total;
}
$("login").onsubmit = async e => {
    e.preventDefault();
    try {
        const result = await api("/login","POST",Object.fromEntries(new FormData(e.target)));
        token = result.access_token; user = result.user; e.target.reset();
        $("identity").textContent = user.username+" · "+user.role; $("loginPanel").hidden = true;
        $("workspace").hidden = false; $("logout").hidden = false;
        $("notice").textContent = ""; await refreshUsers(); await refresh();
    } catch(error) { report(error); }
};
$("logout").onclick = async () => { try { await api("/logout","POST"); } catch(e) { report(e); } finally { clearSession(); } };
$("newCase").onsubmit = async e => {
    e.preventDefault();
    const body = Object.fromEntries(new FormData(e.target)); body.owner_id = Number(body.owner_id);
    try { await api("/cases","POST",body); e.target.reset(); offset=0; await refresh(); }
    catch(error) { report(error); }
};
$("filter").onsubmit = e => { e.preventDefault(); offset=0; refresh().catch(report); };
$("prev").onclick = () => { offset=Math.max(0,offset-limit); refresh().catch(report); };
$("next").onclick = () => { offset+=limit; refresh().catch(report); };
