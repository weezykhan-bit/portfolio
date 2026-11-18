/* Voice Changer, Speech to Text and Pronunciations. */
(() => {
  "use strict";
  const { $, $$, esc, fmtTime, fmtTC, fmtDate, store } = SW;

  // =================== Voice Changer ===================
  let vcVoice = store.get("vcVoice", "preset:bf_emma");
  const vcSrc = SW.source($('[data-source="changer"]'), "changer", () => vcReady());
  const vcReady = () => { $("#vcGo").disabled = !vcSrc.file || !SW.voice(vcVoice); };
  const vcRender = () => { $("#vcVoice").innerHTML = SW.voicePickHTML(SW.voice(vcVoice)); vcReady(); };
  $("#vcVoice").addEventListener("click", () => SW.pickVoice(vcVoice, (id) => { vcVoice = id; store.set("vcVoice", id); vcRender(); }, { title: "Change it to which voice?" }));
  document.addEventListener("sw:voices", () => { if (!SW.voice(vcVoice)) vcVoice = "preset:bf_emma"; vcRender(); });
  $("#vcGo").addEventListener("click", async () => {
    if (!vcSrc.file) return;
    const fd = new FormData();
    fd.append("voice_id", vcVoice);
    fd.append("file", vcSrc.file, vcSrc.file.name || "recording.wav");
    try {
      const job = await SW.api("/api/changer", { method: "POST", body: fd });
      await SW.trackJob(job, {
        progress: $("#vcProgress"), button: $("#vcGo"), label: "Changing voice…",
        onDone: async (j) => { await SW.loadHistory(); SW.player.play(SW.historyItem(j.result)); SW.toast(`Ready in ${j.result.render_seconds} s`); },
      });
    } catch (e) { SW.toast(e.message, "error"); }
  });
  document.addEventListener("sw:history", () => {
    const items = SW.state.history.filter((h) => h.kind === "changer").slice(0, 5);
    $("#vcRecent").innerHTML = SW.historyList(items, "<strong>Nothing converted yet</strong>Record yourself reading a line, then hear it in another voice.");
  });

  // =================== Speech to Text ===================
  let sttSize = store.get("sttSize", "small");
  let doc = null;
  const sttSrc = SW.source($('[data-source="transcribe"]'), "transcribe", () => { $("#sttGo").disabled = !sttSrc.file; });
  const sizeHint = { small: "Good for clear speech. Much faster on a computer without a graphics card.", accurate: "Best for accents, noise, Hindi and mixed languages. Slower: plan on several minutes per hour of audio, more on CPU." };
  function setSize(v) { sttSize = v; store.set("sttSize", v); $$("#sttSize button").forEach((b) => b.classList.toggle("active", b.dataset.v === v)); $("#sttSizeHint").textContent = sizeHint[v]; }
  $("#sttSize").addEventListener("click", (e) => { const b = e.target.closest("[data-v]"); if (b) setSize(b.dataset.v); });
  setSize(sttSize);
  document.addEventListener("sw:voices", () => { const cur = $("#sttLang").value; $("#sttLang").innerHTML = SW.languageOptions(true); $("#sttLang").value = cur || ""; });
  $("#sttGo").addEventListener("click", async () => {
    if (!sttSrc.file) return;
    const fd = new FormData();
    fd.append("size", sttSize);
    fd.append("language", $("#sttLang").value);
    fd.append("file", sttSrc.file, sttSrc.file.name || "recording.wav");
    try {
      const job = await SW.api("/api/transcribe", { method: "POST", body: fd });
      await SW.trackJob(job, {
        progress: $("#sttProgress"), button: $("#sttGo"), label: "Transcribing…",
        onDone: (j) => { sttSrc.reset(); loadTranscripts(); location.hash = `#transcribe/${j.result.id}`; },
      });
    } catch (e) { SW.toast(e.message, "error"); }
  });
  async function loadTranscripts() {
    let items = [];
    try { items = (await SW.api("/api/transcripts")).items; } catch { /* */ }
    const langs = SW.state.voices.clone_languages;
    $("#sttList").innerHTML = items.length ? `<div class="rows">${items.map((t) => `
      <div class="row clickable" data-tid="${esc(t.id)}" tabindex="0" role="button">
        <span class="disc" style="--dc:var(--paper-2);width:30px;height:30px"></span>
        <div style="min-width:0"><div class="row-title">${esc(t.name)}</div>
          <div class="row-meta"><span class="num">${fmtTime(t.duration)}</span><span>${esc(langs[t.language] || t.language)}</span><span>${fmtDate(t.created)}</span><span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:420px">${esc(t.preview)}</span></div></div>
        <div class="row-actions"><button class="icon-btn" data-tdel aria-label="Delete transcript" title="Delete">${SW.ICON.trash}</button></div>
      </div>`).join("")}</div>`
      : `<div class="empty"><strong>No transcripts yet</strong>Drop an interview, voice note or video above to get text and subtitles.</div>`;
  }
  $("#sttList").addEventListener("click", async (e) => {
    const row = e.target.closest("[data-tid]"); if (!row) return;
    if (e.target.closest("[data-tdel]")) {
      if (!(await SW.dialog({ title: "Delete this transcript?", confirm: "Delete", danger: true }))) return;
      await SW.api(`/api/transcripts/${row.dataset.tid}`, { method: "DELETE" });
      loadTranscripts(); return;
    }
    location.hash = `#transcribe/${row.dataset.tid}`;
  });
  $("#sttList").addEventListener("keydown", (e) => { const r = e.target.closest("[data-tid]"); if (r && e.key === "Enter") location.hash = `#transcribe/${r.dataset.tid}`; });

  SW.transcribe = {
    async route(tid) {
      $("#sttHome").hidden = !!tid; $("#sttDoc").hidden = !tid;
      if (!tid) { loadTranscripts(); return; }
      try { doc = await SW.api(`/api/transcripts/${tid}`); } catch (e) { SW.toast(e.message, "error"); location.hash = "#transcribe"; return; }
      $("#sttTitle").textContent = doc.name;
      $("#sttMeta").textContent = `${fmtTime(doc.duration)} · ${SW.state.voices.clone_languages[doc.language] || doc.language} · ${doc.segments.length} segments · transcribed in ${doc.render_seconds} s`;
      $("#sttSegments").innerHTML = doc.segments.length
        ? doc.segments.map((s) => `<div class="segment"><span class="tc">${fmtTC(s.start)}</span><p>${esc(s.text)}</p></div>`).join("")
        : `<div class="empty" style="margin:16px">No speech was found in this file.</div>`;
    },
  };
  const plain = () => doc.segments.map((s) => s.text).join("\n");
  $("#sttBack").addEventListener("click", () => { location.hash = "#transcribe"; });
  $("#sttCopy").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(plain()); SW.toast("Copied"); }
    catch { const ta = Object.assign(document.createElement("textarea"), { value: plain() }); document.body.append(ta); ta.select(); document.execCommand("copy"); ta.remove(); SW.toast("Copied"); }
  });
  $$("[data-stt-export]").forEach((b) => b.addEventListener("click", () => {
    const f = b.dataset.sttExport;
    SW.download(`/api/transcripts/${doc.id}/export?format=${f}`, `${doc.name.replace(/\.[^.]+$/, "")}.${f}`);
  }));
  $("#sttToSpeech").addEventListener("click", () => { SW.speech.setText(plain()); location.hash = "#speech"; });
  $("#sttToStudio").addEventListener("click", async () => {
    try { await SW.studio.createFromText(doc.name.replace(/\.[^.]+$/, ""), doc.segments.map((s) => s.text).join("\n")); }
    catch (e) { SW.toast(e.message, "error"); }
  });

  // =================== Pronunciations ===================
  let rules = [], dirty = false;
  async function loadLex() {
    try { rules = (await SW.api("/api/pronunciations")).items; } catch { rules = []; }
    dirty = false;
    renderLex();
  }
  function renderLex() {
    $("#lexRows").innerHTML = rules.length ? rules.map((r, i) => `
      <div class="lex" data-i="${i}">
        <input class="input" data-f="find" value="${esc(r.find)}" placeholder="Written as, e.g. OTT" aria-label="Written as">
        <svg class="arrow" viewBox="0 0 24 24"><path d="M5 12h14m-5-5 5 5-5 5"/></svg>
        <input class="input" data-f="say" value="${esc(r.say)}" placeholder="Say it as, e.g. O T T" aria-label="Say it as">
        <label class="check" title="Only replace when the capitals match"><input type="checkbox" data-f="match_case" ${r.match_case ? "checked" : ""}>Match case</label>
        <button class="icon-btn" data-del aria-label="Remove word" title="Remove">${SW.ICON.trash}</button>
      </div>`).join("")
      : `<div class="empty" style="border:0"><strong>No words yet</strong>Add brand names, people's names and abbreviations the voices get wrong.<br>For example: <span class="num">Swara → Swuh-raa</span>, <span class="num">OTT → O T T</span>, <span class="num">Ltd → Limited</span>.</div>`;
    $("#lexSave").disabled = !dirty;
    preview();
  }
  const markDirty = () => { dirty = true; $("#lexSave").disabled = false; preview(); };
  $("#lexRows").addEventListener("input", (e) => {
    const row = e.target.closest("[data-i]"); if (!row) return;
    const r = rules[+row.dataset.i], f = e.target.dataset.f;
    r[f] = f === "match_case" ? e.target.checked : e.target.value;
    markDirty();
  });
  $("#lexRows").addEventListener("click", (e) => {
    const row = e.target.closest("[data-i]"); if (!row || !e.target.closest("[data-del]")) return;
    rules.splice(+row.dataset.i, 1); dirty = true; renderLex();
  });
  $("#lexAdd").addEventListener("click", () => { rules.push({ find: "", say: "", match_case: false }); dirty = true; renderLex(); $$("#lexRows [data-f=find]").pop()?.focus(); });
  $("#lexSave").addEventListener("click", async () => {
    try { rules = (await SW.json("/api/pronunciations", { items: rules }, "PUT")).items; dirty = false; renderLex(); SW.toast("Pronunciations saved. They apply to every voice."); }
    catch (e) { SW.toast(e.message, "error"); }
  });
  let pvTimer = 0;
  function preview() {
    clearTimeout(pvTimer);
    const t = $("#lexTest").value;
    if (!t.trim()) { $("#lexOut").textContent = ""; return; }
    // Local preview of unsaved rules, matching the server's rules.
    let out = t;
    for (const r of [...rules].filter((r) => r.find.trim()).sort((a, b) => b.find.length - a.find.length)) {
      const re = new RegExp(`(?<![\\p{L}\\p{N}_])${r.find.trim().replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}(?![\\p{L}\\p{N}_])`, r.match_case ? "gu" : "giu");
      out = out.replace(re, () => r.say);
    }
    $("#lexOut").innerHTML = `Voices will read: <b>${esc(out)}</b>`;
  }
  $("#lexTest").addEventListener("input", preview);
  SW.lexicon = { route: loadLex, dirty: () => dirty };
})();
