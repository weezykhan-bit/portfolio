/* Studio: long-form scripts with a cast. Each line is cued to a character; each
   character is cast to a voice. Lines render individually and export as one file. */
(() => {
  "use strict";
  const { $, $$, esc, fmtTime, fmtTC, fmtDate } = SW;
  let project = null;      // the open project (server shape)
  let saveTimer = 0, saving = null, renderJob = null, playQueue = null;

  // ---------- home ----------
  async function loadList() {
    let items = [];
    try { items = (await SW.api("/api/projects")).items; } catch (e) { SW.toast(e.message, "error"); }
    $("#projectList").innerHTML = items.length
      ? `<div class="proj-grid">${items.map((p) => `
          <div class="paper proj" data-pid="${esc(p.id)}" tabindex="0" role="button">
            <h2>${esc(p.title)}</h2>
            <div class="cues">${p.speakers.slice(0, 5).map((s, i) => `<span class="cue" style="--cue:${SW.CAST[i % 6]}">${esc(s)}</span>`).join("")}${p.speakers.length > 5 ? `<span class="muted">+${p.speakers.length - 5}</span>` : ""}</div>
            <div class="row-meta"><span><b class="num">${p.lines}</b> lines</span><span><b class="num">${p.words.toLocaleString()}</b> words</span><span>${p.rendered === p.lines ? "All rendered" : `${p.rendered}/${p.lines} rendered`}</span><span>${fmtDate(p.updated)}</span></div>
          </div>`).join("")}</div>`
      : `<div class="empty"><strong>No projects yet</strong>Use Studio for anything longer than a paragraph, or anything with more than one voice.<br><button class="btn primary" data-new-project>${SW.ICON.plus}New project</button></div>`;
  }
  const showNew = (on) => { $("#newProject").hidden = !on; $("#newProjectBtn").hidden = on; if (on) $("#npTitle").focus(); };
  document.addEventListener("click", (e) => { if (e.target.closest("[data-new-project]")) showNew(true); });
  $("#newProjectBtn").addEventListener("click", () => showNew(true));
  $("#npCancel").addEventListener("click", () => showNew(false));
  $("#npCreate").addEventListener("click", async () => {
    const btn = $("#npCreate");
    btn.disabled = true;
    try {
      const p = await SW.json("/api/projects", { title: $("#npTitle").value, text: $("#npText").value, voice_id: SW.store.get("ttsVoice", "preset:af_heart") });
      $("#npTitle").value = ""; $("#npText").value = "";
      showNew(false);
      location.hash = `#studio/${p.id}`;
    } catch (e) { SW.toast(e.message, "error"); }
    btn.disabled = false;
  });
  $("#projectList").addEventListener("click", (e) => { const c = e.target.closest("[data-pid]"); if (c) location.hash = `#studio/${c.dataset.pid}`; });
  $("#projectList").addEventListener("keydown", (e) => { const c = e.target.closest("[data-pid]"); if (c && e.key === "Enter") location.hash = `#studio/${c.dataset.pid}`; });

  // ---------- open / route ----------
  SW.studio = {
    async route(pid) {
      if (!pid) {
        await flush();
        project = null;
        $("#studioHome").hidden = false; $("#studioEditor").hidden = true;
        loadList();
        return;
      }
      if (project?.id === pid) return;
      try { project = await SW.api(`/api/projects/${pid}`); } catch (e) { SW.toast(e.message, "error"); location.hash = "#studio"; return; }
      $("#studioHome").hidden = true; $("#studioEditor").hidden = false;
      renderAll();
    },
    async createFromText(title, text) {
      const p = await SW.json("/api/projects", { title, text, voice_id: SW.store.get("ttsVoice", "preset:af_heart") });
      location.hash = `#studio/${p.id}`;
    },
  };

  // ---------- rendering ----------
  const castIndex = (speaker) => Math.max(0, project.cast.findIndex((c) => c.speaker === speaker));
  const cueColor = (speaker) => SW.CAST[castIndex(speaker) % 6];

  function renderAll() {
    $("#projTitle").value = project.title;
    renderCast();
    renderLines();
    renderSummary();
    renderSettings();
  }

  function renderCast() {
    $("#castList").innerHTML = project.cast.map((c, i) => {
      const v = SW.voice(c.voice_id);
      const used = project.lines.filter((l) => l.speaker === c.speaker).length;
      return `<div class="cast-item" data-ci="${i}" style="--cue:${SW.CAST[i % 6]}">
        <div style="min-width:0"><input class="cast-name" size="${Math.max(4, c.speaker.length + 1)}" value="${esc(c.speaker)}" aria-label="Character name" title="Rename character" maxlength="40"></div>
        <div style="display:flex;align-items:center;gap:2px">
          <span class="muted num" style="font-size:12px">${used} line${used === 1 ? "" : "s"}</span>
          ${project.cast.length > 1 && !used ? `<button class="icon-btn" data-castdel aria-label="Remove character" title="Remove character">${SW.ICON.trash}</button>` : ""}
        </div>
        <button class="cast-voice" data-castvoice style="grid-column:1 / -1">${SW.disc(v)}<span>${esc(v ? v.name : "Choose a voice")}</span><span class="muted" style="margin-left:auto;font-weight:400">${esc(v ? SW.voiceMeta(v) : "")}</span></button>
      </div>`;
    }).join("");
  }

  function lineHTML(l, start) {
    const opts = project.cast.map((c) => `<option ${c.speaker === l.speaker ? "selected" : ""}>${esc(c.speaker)}</option>`).join("");
    const busyHere = renderJob && renderJob.lines.includes(l.id);
    const st = busyHere ? "busy" : l.status;
    const label = { ready: "Ready", stale: "Edited", new: "New", empty: "Empty", novoice: "No voice", busy: "Rendering" }[st] || st;
    const playable = l.status === "ready";
    return `<div class="line" data-lid="${esc(l.id)}" style="--cue:${cueColor(l.speaker)}">
      <span class="tc">${start != null ? fmtTC(start) : "--:--.-"}</span>
      <div class="who"><span class="cue">${esc(l.speaker)}</span><select aria-label="Speaker">${opts}</select></div>
      <textarea rows="1" aria-label="Line text" placeholder="Type the line…">${esc(l.text)}</textarea>
      <div class="ctl">
        <span class="state ${st}">${label}</span>
        <button class="icon-btn" data-lplay ${playable ? "" : "disabled"} aria-label="Play line" title="Play line"><svg viewBox="0 0 24 24" style="fill:currentColor;stroke:none;width:14px;height:14px"><path d="M8 5v14l11-7z"/></svg></button>
        <button class="icon-btn" data-lrender ${l.status === "empty" || l.status === "novoice" || renderJob ? "disabled" : ""} aria-label="${l.status === "ready" ? "New take" : "Render line"}" title="${l.status === "ready" ? "New take" : "Render line"}">${SW.ICON.redo}</button>
        <div class="line-menu"><button class="icon-btn" data-lmenu aria-label="More" title="More">${SW.ICON.more}</button>
          <div class="menu" hidden>
            <button data-lact="above">${SW.ICON.up}Insert line above</button>
            <button data-lact="below">${SW.ICON.down}Insert line below</button>
            <button data-lact="pause">Pause after: ${l.pause.toFixed(1)} s</button>
            <button class="danger" data-lact="delete">${SW.ICON.trash}Delete line</button>
          </div></div>
      </div></div>`;
  }

  function renderLines() {
    let t = 0, known = true;
    $("#lines").innerHTML = project.lines.map((l) => {
      const start = known ? t : null;
      if (l.status === "ready" && l.duration != null) t += l.duration + l.pause;
      else if (l.status !== "empty") known = false;
      return lineHTML(l, start);
    }).join("");
    $$("#lines textarea").forEach(autosize);
    updateRenderAll();
  }

  function updateRenderAll() {
    const todo = project.lines.filter((l) => l.status === "new" || l.status === "stale").length;
    $("#projRenderAll").disabled = !todo || !!renderJob;
    $("#projRenderAll span").textContent = renderJob ? "Rendering…" : todo ? `Render ${todo} line${todo === 1 ? "" : "s"}` : "All rendered";
  }

  function renderSummary() {
    const lines = project.lines.filter((l) => l.status !== "empty");
    const ready = lines.filter((l) => l.status === "ready");
    const dur = ready.reduce((a, l) => a + (l.duration || 0) + l.pause, 0);
    const words = project.lines.reduce((a, l) => a + (l.text.trim() ? l.text.trim().split(/\s+/).length : 0), 0);
    $("#projSummary").innerHTML = `
      <div><b>${ready.length}/${lines.length}</b><span>lines rendered</span></div>
      <div><b>${fmtTime(dur)}</b><span>rendered length</span></div>
      <div><b>${words.toLocaleString()}</b><span>words</span></div>
      <div><b>${project.cast.length}</b><span>in the cast</span></div>`;
  }

  function renderSettings() {
    const s = project.settings;
    const sl = (k, label, min, max, step, lo, hi) => `<div class="slider"><div class="slider-head"><label>${label}</label><output>${(+s[k]).toFixed(2)}</output></div>
      <input type="range" data-ps="${k}" min="${min}" max="${max}" step="${step}" value="${s[k]}"><div class="slider-ends"><span>${lo}</span><span>${hi}</span></div></div>`;
    $("#projSettings").innerHTML = `
      <p class="hint" style="margin:10px 0 0">Built-in voices use Speed. Cloned voices use the other settings and the language.</p>
      ${sl("speed", "Speed", 0.6, 1.6, 0.05, "Slower", "Faster")}
      <label class="label">Cloned voices speak in</label><select class="select" data-ps="language">${SW.languageOptions()}</select>
      ${sl("exaggeration", "Expressiveness", 0.25, 1.5, 0.05, "Calm", "Dramatic")}
      ${sl("cfg_weight", "Pacing", 0.1, 1, 0.05, "Slower", "Brisker")}
      ${sl("temperature", "Variation", 0.3, 1.2, 0.05, "Steady", "Lively")}`;
    $("#projSettings [data-ps=language]").value = s.language;
  }

  function autosize(ta) { ta.style.height = "auto"; ta.style.height = ta.scrollHeight + "px"; }

  // ---------- saving ----------
  function schedule() { clearTimeout(saveTimer); $("#projSaved").textContent = "Saving…"; saveTimer = setTimeout(save, 600); }
  async function save() {
    clearTimeout(saveTimer);
    if (!project) return;
    const body = { title: project.title, cast: project.cast, settings: project.settings, lines: project.lines.map(({ id, speaker, text, pause }) => ({ id, speaker, text, pause })) };
    const pid = project.id;
    saving = SW.json(`/api/projects/${pid}`, body, "PUT").then((fresh) => {
      if (project?.id !== pid) return;
      // keep what the user typed since; take statuses from the server
      const byId = Object.fromEntries(fresh.lines.map((l) => [l.id, l]));
      project.lines.forEach((l) => { const f = byId[l.id]; if (f) { l.status = f.status; l.duration = f.duration; } });
      $("#projSaved").textContent = "Saved";
      refreshStatuses();
    }).catch((e) => { $("#projSaved").textContent = ""; SW.toast("Couldn't save: " + e.message, "error"); });
    await saving;
  }
  async function flush() { if (saveTimer) { await save(); } else if (saving) await saving; }

  // Update status chips and timecodes without re-rendering the text the user is typing in.
  function refreshStatuses() {
    const focused = document.activeElement?.closest?.(".line")?.dataset.lid;
    if (!focused) { renderLines(); renderSummary(); renderCast(); return; }
    let t = 0, known = true;
    project.lines.forEach((l) => {
      const row = $(`.line[data-lid="${CSS.escape(l.id)}"]`);
      if (!row) return;
      const tmp = document.createElement("div");
      tmp.innerHTML = lineHTML(l, known ? t : null);
      row.querySelector(".tc").replaceWith(tmp.querySelector(".tc"));
      row.querySelector(".ctl .state").replaceWith(tmp.querySelector(".state"));
      row.querySelector("[data-lplay]").disabled = l.status !== "ready";
      if (l.status === "ready" && l.duration != null) t += l.duration + l.pause; else if (l.status !== "empty") known = false;
    });
    renderSummary();
    updateRenderAll();
  }

  // ---------- editing events ----------
  $("#projTitle").addEventListener("input", (e) => { project.title = e.target.value; schedule(); });
  $("#lines").addEventListener("input", (e) => {
    const row = e.target.closest(".line"); if (!row) return;
    const l = project.lines.find((x) => x.id === row.dataset.lid);
    if (e.target.tagName === "TEXTAREA") { l.text = e.target.value; autosize(e.target); if (l.status === "ready") l.status = "stale"; if (!l.text.trim()) l.status = "empty"; else if (l.status === "empty") l.status = "new"; updateRenderAll(); schedule(); }
  });
  $("#lines").addEventListener("change", (e) => {
    if (e.target.tagName !== "SELECT") return;
    const row = e.target.closest(".line");
    const l = project.lines.find((x) => x.id === row.dataset.lid);
    l.speaker = e.target.value;
    renderLines(); renderCast(); schedule();
  });
  $("#lines").addEventListener("keydown", (e) => {
    // Enter at the end of a line starts a new line for the same speaker; Shift+Enter is a line break.
    if (e.target.tagName !== "TEXTAREA" || e.key !== "Enter" || e.shiftKey) return;
    if (e.target.selectionStart !== e.target.value.length) return;
    e.preventDefault();
    const row = e.target.closest(".line");
    insertLine(row.dataset.lid, 1);
  });
  function insertLine(refId, offset) {
    const i = project.lines.findIndex((x) => x.id === refId);
    const ref = project.lines[i] || project.lines[project.lines.length - 1];
    const l = { id: Math.random().toString(36).slice(2, 12), speaker: ref ? ref.speaker : project.cast[0].speaker, text: "", pause: 0.5, status: "empty", duration: null };
    project.lines.splice(i < 0 ? project.lines.length : i + offset, 0, l);
    renderLines(); schedule();
    $(`.line[data-lid="${l.id}"] textarea`)?.focus();
  }
  $("#addLine").addEventListener("click", () => insertLine(project.lines[project.lines.length - 1]?.id, 1));

  $("#lines").addEventListener("click", async (e) => {
    const row = e.target.closest(".line"); if (!row) return;
    const lid = row.dataset.lid, l = project.lines.find((x) => x.id === lid);
    if (e.target.closest("[data-lmenu]")) {
      const m = $(".menu", row); const open = m.hidden;
      $$(".menu").forEach((x) => (x.hidden = true)); m.hidden = !open; e.stopPropagation(); return;
    }
    const act = e.target.closest("[data-lact]")?.dataset.lact;
    if (act) {
      $$(".menu").forEach((x) => (x.hidden = true));
      if (act === "above") insertLine(lid, 0);
      if (act === "below") insertLine(lid, 1);
      if (act === "delete") {
        if (l.text.trim() && !(await SW.dialog({ title: "Delete this line?", body: l.text.slice(0, 120), confirm: "Delete", danger: true }))) return;
        project.lines = project.lines.filter((x) => x.id !== lid);
        if (!project.lines.length) project.lines.push({ id: Math.random().toString(36).slice(2, 12), speaker: project.cast[0].speaker, text: "", pause: 0.5, status: "empty" });
        renderLines(); renderCast(); schedule();
      }
      if (act === "pause") {
        const v = await SW.dialog({ title: "Pause after this line", body: "Seconds of silence before the next line (0 to 5).", input: String(l.pause), confirm: "Set pause" });
        if (v != null && !isNaN(parseFloat(v))) { l.pause = Math.max(0, Math.min(5, parseFloat(v))); renderLines(); schedule(); }
      }
      return;
    }
    if (e.target.closest("[data-lplay]")) playLine(l);
    if (e.target.closest("[data-lrender]")) render([lid]);
  });
  document.addEventListener("click", (e) => { if (!e.target.closest(".line-menu")) $$(".menu").forEach((m) => (m.hidden = true)); });

  // cast
  $("#castList").addEventListener("change", (e) => {
    if (!e.target.classList.contains("cast-name")) return;
    const i = +e.target.closest("[data-ci]").dataset.ci, old = project.cast[i].speaker;
    const name = e.target.value.trim() || old;
    if (name !== old && project.cast.some((c) => c.speaker === name)) { SW.toast(`There's already a character called ${name}.`, "error"); e.target.value = old; return; }
    project.cast[i].speaker = name;
    project.lines.forEach((l) => { if (l.speaker === old) l.speaker = name; });
    renderLines(); renderCast(); schedule();
  });
  $("#castList").addEventListener("click", (e) => {
    const item = e.target.closest("[data-ci]"); if (!item) return;
    const i = +item.dataset.ci;
    if (e.target.closest("[data-castvoice]")) {
      SW.pickVoice(project.cast[i].voice_id, (id) => {
        project.cast[i].voice_id = id;
        project.lines.forEach((l) => { if (l.speaker === project.cast[i].speaker && l.status === "ready") l.status = "stale"; });
        renderCast(); renderLines(); schedule();
      }, { title: `Cast a voice for ${project.cast[i].speaker}` });
    }
    if (e.target.closest("[data-castdel]")) { project.cast.splice(i, 1); renderCast(); renderLines(); schedule(); }
  });
  $("#addSpeaker").addEventListener("click", async () => {
    const name = (await SW.dialog({ title: "Add a character", input: "", confirm: "Add" }))?.trim();
    if (!name) return;
    if (project.cast.some((c) => c.speaker.toLowerCase() === name.toLowerCase())) { SW.toast(`${name} is already in the cast.`, "error"); return; }
    project.cast.push({ speaker: name, voice_id: project.cast[0]?.voice_id || "preset:af_heart" });
    renderCast(); renderLines(); schedule();
  });
  $("#projSettings").addEventListener("input", (e) => {
    const k = e.target.dataset.ps; if (!k) return;
    project.settings[k] = k === "language" ? e.target.value : +e.target.value;
    const out = e.target.closest(".slider")?.querySelector("output"); if (out) out.textContent = (+e.target.value).toFixed(2);
    schedule();
  });
  $("#projBack").addEventListener("click", () => { location.hash = "#studio"; });
  $("#projDelete").addEventListener("click", async () => {
    if (!(await SW.dialog({ title: `Delete “${project.title}”?`, body: "The script and every rendered line are removed from this computer.", confirm: "Delete project", danger: true }))) return;
    clearTimeout(saveTimer); saveTimer = 0;
    await SW.api(`/api/projects/${project.id}`, { method: "DELETE" });
    project = null;
    location.hash = "#studio";
  });

  // ---------- render / play / export ----------
  async function render(lineIds) {
    if (renderJob) return;
    await flush();
    const pid = project.id;
    let job;
    try { job = await SW.json(`/api/projects/${pid}/render`, { line_ids: lineIds || null }); } catch (e) { SW.toast(e.message, "error"); return; }
    renderJob = { id: job.id, lines: lineIds || project.lines.filter((l) => l.status === "new" || l.status === "stale").map((l) => l.id) };
    renderLines();
    const poll = setInterval(async () => { if (project?.id === pid) await reloadStatuses(); }, 2500);
    await SW.trackJob(job, {
      onDone: () => { if (lineIds?.length === 1 && project?.id === pid) { const l = project.lines.find((x) => x.id === lineIds[0]); if (l) setTimeout(() => playLine(l), 50); } },
    });
    clearInterval(poll);
    renderJob = null;
    if (project?.id === pid) { await reloadStatuses(); renderLines(); }
  }
  async function reloadStatuses() {
    try {
      const fresh = await SW.api(`/api/projects/${project.id}`);
      const byId = Object.fromEntries(fresh.lines.map((l) => [l.id, l]));
      project.lines.forEach((l) => { const f = byId[l.id]; if (f && f.text === l.text) { l.status = f.status; l.duration = f.duration; } });
      refreshStatuses();
    } catch { /* ignore */ }
  }
  $("#projRenderAll").addEventListener("click", () => render(null));

  function playLine(l) {
    playQueue = null;
    SW.player.play({ key: `l:${l.id}`, title: `${l.speaker} · line ${project.lines.indexOf(l) + 1}`, sub: l.text, url: `/api/projects/${project.id}/lines/${l.id}/audio?v=${Date.now()}` });
  }
  $("#projExportBtn").addEventListener("click", (e) => { e.stopPropagation(); const m = $("#projExportMenu"); m.hidden = !m.hidden; });
  $("#projExportMenu").addEventListener("click", async (e) => {
    const kind = e.target.closest("[data-export]")?.dataset.export; if (!kind) return;
    $("#projExportMenu").hidden = true;
    await flush();
    const name = (project.title || "project").replace(/[^\w\- ]+/g, "").trim() || "project";
    const base = `/api/projects/${project.id}/export`;
    if (kind === "play") {
      try {
        const res = await fetch(`${base}?format=wav&download=0`);
        if (!res.ok) throw new Error((await res.json()).error);
        SW.player.play({ key: `p:${project.id}`, title: project.title, sub: `${project.lines.length} lines · ${project.cast.length} voices`, url: `${base}?format=wav&download=0&v=${Date.now()}`, mp3: `${base}?format=mp3`, wav: `${base}?format=wav`, name });
      } catch (err) { SW.toast(err.message, "error"); }
      return;
    }
    SW.download(`${base}?format=${kind}`, `${name}.${kind}`);
  });

  document.addEventListener("sw:voices", () => { if (project && !$("#studioEditor").hidden) { renderCast(); } });
  document.addEventListener("sw:player", () => {
    $$(".line").forEach((r) => r.classList.toggle("playing", SW.player.item?.key === `l:${r.dataset.lid}`));
  });
  window.addEventListener("beforeunload", () => { if (saveTimer) save(); });
})();
