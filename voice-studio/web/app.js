/* Voice Studio front end. Plain JS, no build step, no network calls beyond the local server. */
(() => {
  "use strict";

  // ---------------- helpers ----------------
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const store = {
    get(k, d) { try { const v = localStorage.getItem("vs." + k); return v == null ? d : JSON.parse(v); } catch { return d; } },
    set(k, v) { try { localStorage.setItem("vs." + k, JSON.stringify(v)); } catch { /* private mode */ } },
  };
  const isMac = /Mac|iPhone|iPad/.test(navigator.platform);
  const fmtTime = (s) => { s = Math.max(0, Math.round(s || 0)); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`; };
  const fmtDate = (t) => {
    const d = new Date(t * 1000), now = new Date();
    const time = d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
    if (d.toDateString() === now.toDateString()) return `Today, ${time}`;
    return d.toLocaleDateString([], { month: "short", day: "numeric" }) + `, ${time}`;
  };

  async function api(path, opts = {}) {
    const res = await fetch(path, opts);
    if (!res.ok) {
      let msg = `Request failed (${res.status})`;
      try { const j = await res.json(); msg = j.error || (Array.isArray(j.detail) ? j.detail.map((d) => d.msg).join(", ") : j.detail) || msg; } catch { /* not json */ }
      throw new Error(msg);
    }
    return res.json();
  }
  const postJSON = (path, body, method = "POST") => api(path, { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });

  function toast(msg, type = "") {
    const el = document.createElement("div");
    el.className = "toast " + type;
    el.textContent = msg;
    $("#toasts").append(el);
    setTimeout(() => el.remove(), type === "error" ? 6000 : 3200);
  }

  const ICON = {
    check: '<svg viewBox="0 0 24 24"><path d="m5 12 5 5L20 7"/></svg>',
    mic: '<svg viewBox="0 0 24 24"><path d="M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3z"/><path d="M5 11a7 7 0 0 0 14 0"/></svg>',
    trash: '<svg viewBox="0 0 24 24"><path d="M4 7h16M10 11v6M14 11v6M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12M9 7V4h6v3"/></svg>',
    edit: '<svg viewBox="0 0 24 24"><path d="M4 20h4L19 9l-4-4L4 16z"/></svg>',
    reuse: '<svg viewBox="0 0 24 24"><path d="M4 12a8 8 0 0 1 14-5.3L20 9"/><path d="M20 4v5h-5M20 12a8 8 0 0 1-14 5.3L4 15"/><path d="M4 20v-5h5"/></svg>',
    play: '<svg class="i-play" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg><svg class="i-pause" viewBox="0 0 24 24"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg>',
    plus: '<svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>',
  };

  // Deterministic gradient avatar per voice
  function avatarHTML(v, size = "") {
    const name = v?.name || "?";
    let h = 0;
    for (const c of (v?.id || name)) h = (h * 31 + c.charCodeAt(0)) >>> 0;
    const a = h % 360, b = (a + 40 + (h >> 9) % 80) % 360;
    const style = `background:linear-gradient(135deg,hsl(${a} 70% 58%),hsl(${b} 75% 45%))`;
    const initials = name.trim().split(/\s+/).map((w) => w[0]).join("").slice(0, 2).toUpperCase();
    const badge = v?.kind === "clone" ? `<span class="badge" title="Cloned voice">${ICON.mic}</span>` : "";
    return `<span class="avatar ${size}" style="${style}">${esc(initials)}${badge}</span>`;
  }

  // ---------------- state ----------------
  const state = {
    status: null,
    voices: { presets: [], clones: [], clone_languages: {}, preset_languages: {} },
    voiceId: store.get("voiceId", "preset:af_heart"),
    history: [],
    job: null,
    presetFilter: store.get("presetFilter", "all"),
  };
  const DEFAULTS = { speed: 1, exaggeration: 0.5, cfg: 0.5, temperature: 0.8 };
  const allVoices = () => [...state.voices.clones, ...state.voices.presets];
  const currentVoice = () => allVoices().find((v) => v.id === state.voiceId);

  // ---------------- routing ----------------
  function route() {
    const view = (location.hash || "#tts").slice(1);
    const known = ["tts", "voices", "history"];
    const v = known.includes(view) ? view : "tts";
    known.forEach((k) => ($("#view-" + k).hidden = k !== v));
    $$(".nav-item").forEach((a) => a.classList.toggle("active", a.dataset.view === v));
    if (v === "history") renderHistory();
    if (v === "voices") renderVoices();
    window.scrollTo(0, 0);
  }
  window.addEventListener("hashchange", route);

  // ---------------- status ----------------
  async function loadStatus() {
    try {
      state.status = await api("/api/status");
      $("#device").textContent = state.status.device_label;
      $("#charMax").textContent = state.status.max_text_chars.toLocaleString();
      updateEstimate();
    } catch {
      $("#device").textContent = "Server not reachable";
    }
  }

  // ---------------- voices ----------------
  async function loadVoices() {
    state.voices = await api("/api/voices");
    if (!currentVoice()) state.voiceId = "preset:af_heart";
    renderVoiceSelect();
    fillLanguageSelects();
    renderVoices();
  }

  function voiceMeta(v) {
    if (!v) return "";
    if (v.kind === "clone") return `Cloned · ${state.voices.clone_languages[v.language] || "English"}`;
    return `${v.language} · ${v.gender === "female" ? "Female" : "Male"}`;
  }

  function fillLanguageSelects() {
    const opts = Object.entries(state.voices.clone_languages)
      .sort((a, b) => (a[0] === "en" ? -1 : b[0] === "en" ? 1 : a[1].localeCompare(b[1])))
      .map(([k, n]) => `<option value="${k}">${esc(n)}</option>`).join("");
    $("#language").innerHTML = opts;
    $("#voiceLang").innerHTML = opts;
  }

  function selectVoice(id) {
    state.voiceId = id;
    store.set("voiceId", id);
    const v = currentVoice();
    if (v?.kind === "clone") $("#language").value = v.language || "en";
    renderVoiceSelect();
    renderVoices();
  }

  function renderVoiceSelect() {
    const v = currentVoice();
    $("#vsAvatar").outerHTML = avatarHTML(v).replace('class="avatar', 'id="vsAvatar" class="avatar');
    $("#vsName").textContent = v ? v.name : "Choose a voice";
    $("#vsMeta").textContent = voiceMeta(v);
    const clone = v?.kind === "clone";
    $("#cloneSettings").hidden = !clone;
    $("#presetSettings").hidden = clone;
    if (clone && !$("#language").dataset.touched) $("#language").value = v.language || "en";
    updateEstimate();
  }

  // Voice picker modal
  function openPicker() {
    $("#pickerSearch").value = "";
    renderPicker();
    openModal("#pickerModal");
    setTimeout(() => $("#pickerSearch").focus(), 50);
  }
  function renderPicker() {
    const q = $("#pickerSearch").value.trim().toLowerCase();
    const match = (v) => !q || `${v.name} ${voiceMeta(v)} ${v.description || ""}`.toLowerCase().includes(q);
    const row = (v) => `
      <div class="p-row ${v.id === state.voiceId ? "selected" : ""}" data-id="${esc(v.id)}">
        ${avatarHTML(v)}
        <div class="p-text"><div class="p-name">${esc(v.name)}</div><div class="p-meta">${esc(voiceMeta(v))}</div></div>
        <button class="play-btn sm ghost" data-preview="${esc(v.id)}" aria-label="Preview ${esc(v.name)}">${ICON.play}</button>
        <span class="check">${v.id === state.voiceId ? ICON.check : ""}</span>
      </div>`;
    let html = "";
    const clones = state.voices.clones.filter(match);
    if (clones.length) html += `<div class="picker-group">My voices</div>` + clones.map(row).join("");
    for (const [code, label] of Object.entries(state.voices.preset_languages)) {
      const list = state.voices.presets.filter((v) => v.lang_code === code && match(v));
      if (list.length) html += `<div class="picker-group">${esc(label)}</div>` + list.map(row).join("");
    }
    if (!state.voices.clones.length && !q) {
      html = `<div class="p-row" data-goto-add>${`<span class="avatar" style="background:var(--ink);color:var(--ink-text)">${ICON.plus}</span>`}
        <div class="p-text"><div class="p-name">Clone your own voice</div><div class="p-meta">Upload or record 10–30 seconds of speech</div></div></div>` + html;
    }
    $("#pickerList").innerHTML = html || `<div class="empty">No voices match “${esc(q)}”.</div>`;
  }
  $("#pickerSearch").addEventListener("input", renderPicker);
  $("#pickerList").addEventListener("click", (e) => {
    if (e.target.closest("[data-preview]")) return;
    if (e.target.closest("[data-goto-add]")) { closeModals(); openAddVoice(); return; }
    const row = e.target.closest(".p-row[data-id]");
    if (row) { selectVoice(row.dataset.id); closeModals(); }
  });
  $("#voiceSelect").addEventListener("click", openPicker);

  // Previews (shared by picker and voice cards)
  const previewAudio = $("#previewAudio");
  let previewBtn = null;
  function stopPreview() {
    previewAudio.pause();
    if (previewBtn) previewBtn.classList.remove("playing", "loading");
    previewBtn = null;
  }
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-preview]");
    if (!btn) return;
    e.stopPropagation();
    if (previewBtn === btn) { stopPreview(); return; }
    stopPreview();
    player.pause();
    previewBtn = btn;
    btn.classList.add("loading");
    previewAudio.src = `/api/voices/${encodeURIComponent(btn.dataset.preview)}/preview`;
    previewAudio.play().then(() => btn.classList.replace("loading", "playing")).catch(() => {
      btn.classList.remove("loading");
      toast("Couldn't play the preview. The first preview of a voice needs a few seconds to generate.", "error");
    });
  });
  previewAudio.addEventListener("ended", stopPreview);
  previewAudio.addEventListener("error", () => { if (previewBtn) toast("Preview failed to load.", "error"); stopPreview(); });

  // Voices page
  function renderVoices() {
    const clones = state.voices.clones;
    $("#myCount").textContent = clones.length ? `${clones.length} voice${clones.length > 1 ? "s" : ""}` : "";
    const card = (v) => `
      <div class="v-card ${v.id === state.voiceId ? "selected" : ""}" data-id="${esc(v.id)}">
        <div class="v-top">
          ${avatarHTML(v, "lg")}
          <div style="min-width:0">
            <div class="v-name">${esc(v.name)}</div>
            <div class="v-desc">${esc(v.description || voiceMeta(v))}</div>
          </div>
        </div>
        <div class="v-tags">
          ${v.kind === "clone"
            ? `<span class="tag accent">Cloned</span><span class="tag">${esc(state.voices.clone_languages[v.language] || "English")}</span><span class="tag">${Math.round(v.sample_seconds || 0)}s sample</span>`
            : `<span class="tag">${esc(v.language)}</span><span class="tag">${v.gender === "female" ? "Female" : "Male"}</span>`}
        </div>
        <div class="v-actions">
          <button class="play-btn sm ghost" data-preview="${esc(v.id)}" aria-label="Play">${ICON.play}</button>
          <span class="spacer"></span>
          ${v.kind === "clone" ? `<button class="icon-btn" data-rename title="Rename">${ICON.edit}</button><button class="icon-btn" data-delete title="Delete">${ICON.trash}</button>` : ""}
          <button class="btn ${v.id === state.voiceId ? "btn-primary" : ""}" data-use>${v.id === state.voiceId ? "Selected" : "Use"}</button>
        </div>
      </div>`;
    $("#myVoices").innerHTML =
      `<button class="add-card" id="addCard"><span class="plus">${ICON.plus}</span><strong>Clone a voice</strong><span>Upload or record 10–30 seconds</span></button>` +
      clones.map(card).join("");

    const langs = { all: "All", ...state.voices.preset_languages };
    $("#presetFilter").innerHTML = Object.entries(langs).map(([k, n]) => `<button data-f="${k}" class="${state.presetFilter === k ? "active" : ""}">${esc(n)}</button>`).join("");
    const presets = state.voices.presets.filter((v) => state.presetFilter === "all" || v.lang_code === state.presetFilter);
    $("#presetVoices").innerHTML = presets.map(card).join("");
  }
  $("#presetFilter").addEventListener("click", (e) => {
    const b = e.target.closest("[data-f]");
    if (!b) return;
    state.presetFilter = b.dataset.f;
    store.set("presetFilter", state.presetFilter);
    renderVoices();
  });
  $("#view-voices").addEventListener("click", async (e) => {
    if (e.target.closest("#addCard")) return openAddVoice();
    const cardEl = e.target.closest(".v-card");
    if (!cardEl) return;
    const id = cardEl.dataset.id;
    const v = allVoices().find((x) => x.id === id);
    if (e.target.closest("[data-use]")) { selectVoice(id); location.hash = "#tts"; toast(`${v.name} selected`); }
    if (e.target.closest("[data-rename]")) {
      const name = await dialog({ title: "Rename voice", input: v.name, confirm: "Save" });
      if (name && name.trim()) {
        try { await postJSON(`/api/voices/${encodeURIComponent(id)}`, { name }, "PATCH"); await loadVoices(); } catch (err) { toast(err.message, "error"); }
      }
    }
    if (e.target.closest("[data-delete]")) {
      const ok = await dialog({ title: `Delete “${v.name}”?`, body: "The voice sample is removed from this computer. Audio you already generated stays in History.", confirm: "Delete", danger: true });
      if (ok) {
        try {
          await api(`/api/voices/${encodeURIComponent(id)}`, { method: "DELETE" });
          if (state.voiceId === id) state.voiceId = "preset:af_heart";
          await loadVoices();
          toast("Voice deleted");
        } catch (err) { toast(err.message, "error"); }
      }
    }
  });
  $("#addVoiceBtn").addEventListener("click", () => openAddVoice());

  // ---------------- modals & dialog ----------------
  function openModal(sel) { $(sel).hidden = false; }
  function closeModals() {
    $$(".modal").forEach((m) => { if (!m.hidden) { m.hidden = true; m.dispatchEvent(new Event("close")); } });
    stopPreview();
  }
  document.addEventListener("click", (e) => {
    if (e.target.matches(".modal") || e.target.closest("[data-close]")) closeModals();
  });

  function dialog({ title, body = "", input = null, confirm = "OK", danger = false }) {
    return new Promise((resolve) => {
      const wrap = document.createElement("div");
      wrap.className = "modal";
      wrap.innerHTML = `<div class="modal-card" style="width:min(420px,100%)">
        <div class="modal-head"><h3>${esc(title)}</h3></div>
        ${body ? `<p class="muted" style="margin:0 0 6px">${esc(body)}</p>` : ""}
        ${input != null ? `<input class="input" value="${esc(input)}" maxlength="60">` : ""}
        <div class="modal-foot"><button class="btn" data-x>Cancel</button><button class="btn btn-primary ${danger ? "btn-danger" : ""}" data-ok>${esc(confirm)}</button></div></div>`;
      if (danger) $("[data-ok]", wrap).style.cssText = "background:var(--danger);border-color:var(--danger);color:#fff";
      document.body.append(wrap);
      const inp = $("input", wrap);
      const done = (val) => { wrap.remove(); resolve(val); };
      $("[data-ok]", wrap).onclick = () => done(inp ? inp.value : true);
      $("[data-x]", wrap).onclick = () => done(null);
      wrap.onclick = (e) => { if (e.target === wrap) done(null); };
      wrap.onkeydown = (e) => { if (e.key === "Enter") done(inp ? inp.value : true); if (e.key === "Escape") done(null); };
      setTimeout(() => (inp || $("[data-ok]", wrap)).focus(), 30);
      if (inp) inp.select();
    });
  }
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeModals(); });

  // ---------------- settings ----------------
  const sliders = {
    speed: (v) => `${(+v).toFixed(2)}×`,
    exaggeration: (v) => (+v).toFixed(2),
    cfg: (v) => (+v).toFixed(2),
    temperature: (v) => (+v).toFixed(2),
  };
  const saved = store.get("settings", {});
  for (const [id, fmt] of Object.entries(sliders)) {
    const el = $("#" + id);
    if (saved[id] != null) el.value = saved[id];
    const out = $(`#${id}Out`);
    const upd = () => { out.textContent = fmt(el.value); };
    el.addEventListener("input", () => { upd(); saveSettings(); updateEstimate(); });
    upd();
  }
  function saveSettings() {
    store.set("settings", Object.fromEntries(Object.keys(sliders).map((k) => [k, +$("#" + k).value])));
  }
  $("#resetSettings").addEventListener("click", () => {
    for (const [k, v] of Object.entries(DEFAULTS)) { $("#" + k).value = v; $("#" + k).dispatchEvent(new Event("input")); }
    $("#seed").value = "";
    toast("Settings reset");
  });
  $("#language").addEventListener("change", (e) => { e.target.dataset.touched = "1"; });

  // ---------------- editor ----------------
  const textEl = $("#text");
  textEl.value = store.get("draft", "");
  const SAMPLES = {
    narration: "Every great journey begins with a single decision. Ours began on a rainy Tuesday morning, in a small studio above a bakery, with nothing but a microphone and an idea.\n\nWhat happened next surprised everyone, including us.",
    ad: "Tired of paying every month just to hear your own words out loud? Meet Voice Studio. Lifelike speech, your own cloned voice, and zero subscriptions. It all runs on your computer. Try it today.",
    story: "The lighthouse keeper had not seen a ship in eleven years. So when the lantern flickered twice, then three times, he put down his tea and climbed the stairs, slowly, one hand on the cold iron rail.",
    hindi: "नमस्ते! यह वॉइस स्टूडियो पूरी तरह आपके अपने कंप्यूटर पर चलता है। बस टेक्स्ट लिखिए, आवाज़ चुनिए, और सुनिए।",
  };
  $$(".chip[data-sample]").forEach((c) => c.addEventListener("click", () => {
    textEl.value = SAMPLES[c.dataset.sample];
    if (c.dataset.sample === "hindi") {
      const v = currentVoice();
      if (v?.kind === "clone") { $("#language").value = "hi"; $("#language").dataset.touched = "1"; }
      else if (v?.lang_code !== "h") selectVoice("preset:hf_alpha");
    }
    onText();
    textEl.focus();
  }));
  function onText() {
    const n = textEl.value.length;
    $("#charCount").textContent = n.toLocaleString();
    $(".counter").classList.toggle("over", state.status && n > state.status.max_text_chars);
    store.set("draft", textEl.value);
    updateEstimate();
  }
  textEl.addEventListener("input", onText);

  function updateEstimate() {
    const n = textEl.value.trim().length;
    const v = currentVoice();
    if (!n || !v) { $("#estimate").textContent = ""; return; }
    const audioSecs = n / 15 / (v.kind === "preset" ? +$("#speed").value : 1);
    const dev = state.status?.device || "cpu";
    const factor = v.kind === "preset" ? (dev === "cuda" ? 0.05 : 0.45) : (dev === "cuda" ? 0.6 : dev === "mps" ? 1.5 : 7);
    const render = audioSecs * factor;
    const r = render < 5 ? "a few seconds" : render < 90 ? `~${Math.round(render)}s` : `~${Math.round(render / 60)} min`;
    $("#estimate").textContent = `≈ ${fmtTime(audioSecs)} of audio · renders in ${r} on this machine`;
  }

  // ---------------- generate ----------------
  $("#kbdHint").textContent = isMac ? "⌘ ↵" : "Ctrl ↵";
  $("#generateBtn").addEventListener("click", generate);
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter" && !$("#view-tts").hidden) { e.preventDefault(); generate(); }
  });

  async function generate() {
    if (state.job) return;
    const text = textEl.value.trim();
    if (!text) { toast("Type or paste some text first.", "error"); textEl.focus(); return; }
    const v = currentVoice();
    if (!v) { openPicker(); return; }
    const seed = $("#seed").value === "" ? null : Math.max(0, parseInt($("#seed").value, 10) || 0);
    const body = {
      text, voice_id: v.id, seed,
      speed: +$("#speed").value,
      exaggeration: +$("#exaggeration").value,
      cfg_weight: +$("#cfg").value,
      temperature: +$("#temperature").value,
      language: v.kind === "clone" ? $("#language").value : "en",
    };
    setBusy(true);
    try {
      const job = await postJSON("/api/generate", body);
      state.job = job;
      pollJob(job.id, v);
    } catch (err) {
      setBusy(false);
      toast(err.message, "error");
    }
  }

  function setBusy(busy) {
    $("#generateBtn").disabled = busy;
    $("#generateBtn .btn-label").textContent = busy ? "Generating…" : "Generate speech";
    $("#progress").hidden = !busy;
    if (busy) { $("#progressFill").style.width = "0"; $("#progressText").textContent = "Starting…"; }
  }

  async function pollJob(id, voice) {
    let j;
    try { j = await api(`/api/jobs/${id}`); } catch (err) { finishJob(); toast(err.message, "error"); return; }
    const bar = $(".progress-bar");
    if (j.status === "queued") {
      bar.classList.add("indeterminate");
      $("#progressText").textContent = j.position > 1 ? `Queued (#${j.position})` : "Queued…";
    } else if (j.status === "running") {
      if (j.total) {
        bar.classList.remove("indeterminate");
        $("#progressFill").style.width = `${Math.round((j.done / j.total) * 100)}%`;
        $("#progressText").textContent = `Rendering part ${Math.min(j.done + 1, j.total)} of ${j.total} · ${fmtTime(j.elapsed)}`;
      } else {
        bar.classList.add("indeterminate");
        const loaded = voice.kind === "preset" ? state.status?.loaded?.kokoro : (state.status?.loaded?.clone_en || state.status?.loaded?.clone_multi);
        $("#progressText").textContent = j.elapsed > 4 && !loaded ? "Loading voice model (first run can take a minute)…" : "Preparing voice…";
      }
    }
    if (j.status === "done") {
      finishJob();
      $("#progressFill").style.width = "100%";
      await loadHistory();
      playItem(j.result, true);
      toast(`Done in ${j.result.render_seconds}s`);
      loadStatus();
      return;
    }
    if (j.status === "error") { finishJob(); toast(j.error || "Generation failed", "error"); return; }
    if (j.status === "cancelled") { finishJob(); toast("Cancelled"); return; }
    setTimeout(() => pollJob(id, voice), 600);
  }
  function finishJob() { state.job = null; setBusy(false); $(".progress-bar").classList.remove("indeterminate"); }
  $("#cancelBtn").addEventListener("click", async () => {
    if (!state.job) return;
    $("#progressText").textContent = "Cancelling after the current part…";
    try { await api(`/api/jobs/${state.job.id}/cancel`, { method: "POST" }); } catch { /* ignore */ }
  });

  // ---------------- history ----------------
  async function loadHistory() {
    try { state.history = (await api("/api/history")).items; } catch { state.history = []; }
    renderRecent();
    if (!$("#view-history").hidden) renderHistory();
  }
  function historyRow(h) {
    const playing = player.item?.id === h.id;
    return `<div class="h-row ${playing ? "playing" : ""}" data-id="${esc(h.id)}">
      <button class="play-btn sm ${playing && !audioEl.paused ? "playing" : ""}" data-play aria-label="Play">${ICON.play}</button>
      <div style="min-width:0">
        <div class="h-text">${esc(h.text)}</div>
        <div class="h-meta"><b>${esc(h.voice_name)}</b><span>${fmtTime(h.duration)}</span><span>${fmtDate(h.created)}</span><span>rendered in ${h.render_seconds}s</span></div>
      </div>
      <div class="h-actions">
        <button class="icon-btn" data-reuse title="Load text and voice into the editor">${ICON.reuse}</button>
        <a class="icon-btn" href="/api/history/${h.id}/audio?format=wav&download=1" title="Download WAV">WAV</a>
        <a class="icon-btn" href="/api/history/${h.id}/audio?format=mp3&download=1" title="Download MP3">MP3</a>
        <button class="icon-btn" data-del title="Delete">${ICON.trash}</button>
      </div>
    </div>`;
  }
  function renderRecent() {
    const items = state.history.slice(0, 4);
    $("#recentList").innerHTML = items.length ? items.map(historyRow).join("")
      : `<div class="empty"><strong>Nothing generated yet</strong>Your audio will appear here, saved on this computer.</div>`;
  }
  function renderHistory() {
    const q = $("#historySearch").value.trim().toLowerCase();
    const items = state.history.filter((h) => !q || `${h.text} ${h.voice_name}`.toLowerCase().includes(q));
    $("#historyList").innerHTML = items.length ? items.map(historyRow).join("")
      : `<div class="empty"><strong>${q ? "No matches" : "No history yet"}</strong>${q ? "Try a different search." : "Generate something on the Text to Speech page."}</div>`;
  }
  $("#historySearch").addEventListener("input", renderHistory);
  document.addEventListener("click", async (e) => {
    const row = e.target.closest(".h-row");
    if (!row) return;
    const h = state.history.find((x) => x.id === row.dataset.id);
    if (!h) return;
    if (e.target.closest("[data-play]")) {
      if (player.item?.id === h.id) togglePlay(); else playItem(h, true);
    } else if (e.target.closest("[data-reuse]")) {
      textEl.value = h.text; onText();
      if (allVoices().some((v) => v.id === h.voice_id)) selectVoice(h.voice_id);
      const s = h.settings || {};
      const map = { speed: s.speed, exaggeration: s.exaggeration, cfg: s.cfg_weight, temperature: s.temperature };
      for (const [k, v] of Object.entries(map)) if (v != null) { $("#" + k).value = v; $("#" + k).dispatchEvent(new Event("input")); }
      $("#seed").value = s.seed ?? "";
      if (s.language) { $("#language").value = s.language; $("#language").dataset.touched = "1"; }
      location.hash = "#tts";
    } else if (e.target.closest("[data-del]")) {
      const ok = await dialog({ title: "Delete this generation?", body: "The audio file is removed from this computer.", confirm: "Delete", danger: true });
      if (!ok) return;
      try {
        await api(`/api/history/${h.id}`, { method: "DELETE" });
        if (player.item?.id === h.id) closePlayer();
        await loadHistory();
      } catch (err) { toast(err.message, "error"); }
    }
  });

  // ---------------- player ----------------
  const audioEl = $("#audio");
  const canvas = $("#wave");
  const player = { item: null, peaks: null, raf: 0, pause: () => audioEl.pause() };

  async function playItem(h, autoplay) {
    stopPreview();
    player.item = h;
    $("#player").hidden = false;
    $("#playerTitle").textContent = h.voice_name;
    $("#playerSub").textContent = h.text;
    $("#dlWav").href = `/api/history/${h.id}/audio?format=wav&download=1`;
    $("#dlMp3").href = `/api/history/${h.id}/audio?format=mp3&download=1`;
    $("#timeDur").textContent = fmtTime(h.duration);
    const url = `/api/history/${h.id}/audio`;
    audioEl.src = url;
    player.peaks = null;
    drawWave();
    if (autoplay) audioEl.play().catch(() => { /* autoplay blocked: user presses play */ });
    try {
      const buf = await (await fetch(url)).arrayBuffer();
      const decoded = await decodeAudio(buf);
      player.peaks = computePeaks(decoded.getChannelData(0), 600);
      drawWave();
    } catch { /* waveform is decorative */ }
    renderRecent();
    if (!$("#view-history").hidden) renderHistory();
  }
  function togglePlay() { if (audioEl.paused) audioEl.play(); else audioEl.pause(); }
  function closePlayer() { audioEl.pause(); $("#player").hidden = true; player.item = null; renderRecent(); }
  $("#playBtn").addEventListener("click", togglePlay);
  $("#playerClose").addEventListener("click", closePlayer);
  const syncPlayBtns = () => {
    const playing = !audioEl.paused;
    $("#playBtn").classList.toggle("playing", playing);
    $$(".h-row").forEach((r) => {
      const me = r.dataset.id === player.item?.id;
      r.classList.toggle("playing", me);
      $("[data-play]", r).classList.toggle("playing", me && playing);
    });
  };
  audioEl.addEventListener("play", () => { stopPreview(); syncPlayBtns(); tick(); });
  audioEl.addEventListener("pause", () => { syncPlayBtns(); cancelAnimationFrame(player.raf); drawWave(); });
  audioEl.addEventListener("ended", () => { syncPlayBtns(); drawWave(); });
  audioEl.addEventListener("loadedmetadata", () => { $("#timeDur").textContent = fmtTime(audioEl.duration); });
  function tick() { drawWave(); $("#timeCur").textContent = fmtTime(audioEl.currentTime); if (!audioEl.paused) player.raf = requestAnimationFrame(tick); }
  canvas.addEventListener("click", (e) => {
    if (!audioEl.duration) return;
    const r = canvas.getBoundingClientRect();
    audioEl.currentTime = ((e.clientX - r.left) / r.width) * audioEl.duration;
    $("#timeCur").textContent = fmtTime(audioEl.currentTime);
    drawWave();
  });
  document.addEventListener("keydown", (e) => {
    if (e.code === "Space" && player.item && !e.target.closest("input, textarea, select, button, [contenteditable]")) { e.preventDefault(); togglePlay(); }
  });

  function cssVar(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }
  function drawWave() { paintWave(canvas, player.peaks, audioEl.duration ? audioEl.currentTime / audioEl.duration : 0); }
  function paintWave(cv, peaks, progress) {
    const dpr = window.devicePixelRatio || 1;
    const w = cv.clientWidth, h = cv.clientHeight;
    if (!w) return;
    if (cv.width !== Math.round(w * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); }
    const ctx = cv.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    const bar = 2, gap = 1.5, n = Math.floor(w / (bar + gap));
    const played = cssVar("--accent"), rest = cssVar("--border-strong");
    for (let i = 0; i < n; i++) {
      const p = peaks ? peaks[Math.floor((i / n) * peaks.length)] : 0.08;
      const bh = Math.max(2, p * (h - 4));
      ctx.fillStyle = i / n < progress ? played : rest;
      ctx.beginPath();
      ctx.roundRect ? ctx.roundRect(i * (bar + gap), (h - bh) / 2, bar, bh, 1) : ctx.rect(i * (bar + gap), (h - bh) / 2, bar, bh);
      ctx.fill();
    }
  }
  function computePeaks(data, n) {
    const out = new Float32Array(n), step = Math.max(1, Math.floor(data.length / n));
    let max = 0;
    for (let i = 0; i < n; i++) {
      let m = 0;
      for (let j = i * step, e = Math.min(data.length, j + step); j < e; j++) { const a = Math.abs(data[j]); if (a > m) m = a; }
      out[i] = m; if (m > max) max = m;
    }
    if (max > 0) for (let i = 0; i < n; i++) out[i] = Math.pow(out[i] / max, 0.8);
    return out;
  }
  window.addEventListener("resize", () => { drawWave(); if (sample.peaks) paintWave($("#sampleWave"), sample.peaks, sample.progress()); });

  // ---------------- audio decode / WAV encode (browser side) ----------------
  let _ctx;
  const audioCtx = () => (_ctx ||= new (window.AudioContext || window.webkitAudioContext)());
  function decodeAudio(buf) {
    return new Promise((res, rej) => audioCtx().decodeAudioData(buf.slice(0), res, rej));
  }
  async function toMono24k(audioBuffer) {
    const rate = 24000;
    const len = Math.ceil(audioBuffer.duration * rate);
    const off = new OfflineAudioContext(1, len, rate);
    const src = off.createBufferSource();
    src.buffer = audioBuffer;
    src.connect(off.destination);
    src.start();
    const out = await off.startRendering();
    return out.getChannelData(0);
  }
  function encodeWav(samples, rate = 24000) {
    const buf = new ArrayBuffer(44 + samples.length * 2), v = new DataView(buf);
    const w = (o, s) => [...s].forEach((c, i) => v.setUint8(o + i, c.charCodeAt(0)));
    w(0, "RIFF"); v.setUint32(4, 36 + samples.length * 2, true); w(8, "WAVE"); w(12, "fmt ");
    v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
    v.setUint32(24, rate, true); v.setUint32(28, rate * 2, true); v.setUint16(32, 2, true); v.setUint16(34, 16, true);
    w(36, "data"); v.setUint32(40, samples.length * 2, true);
    for (let i = 0; i < samples.length; i++) v.setInt16(44 + i * 2, Math.max(-1, Math.min(1, samples[i])) * 0x7fff, true);
    return new Blob([buf], { type: "audio/wav" });
  }

  // ---------------- add voice ----------------
  const sample = { blob: null, peaks: null, url: null, audio: new Audio(), progress: () => (sample.audio.duration ? sample.audio.currentTime / sample.audio.duration : 0) };
  function openAddVoice() {
    resetSample();
    $("#voiceName").value = "";
    $("#voiceDesc").value = "";
    $("#voiceLang").value = "en";
    $("#consent").checked = false;
    switchTab("upload");
    openModal("#addModal");
    updateSaveState();
  }
  $("#addModal").addEventListener("close", () => { stopRecording(true); sample.audio.pause(); });
  function switchTab(t) {
    $$(".tab").forEach((b) => b.classList.toggle("active", b.dataset.tab === t));
    $("#tab-upload").hidden = t !== "upload";
    $("#tab-record").hidden = t !== "record";
  }
  $$(".tab").forEach((b) => b.addEventListener("click", () => { stopRecording(true); switchTab(b.dataset.tab); }));

  function resetSample() {
    sample.audio.pause();
    if (sample.url) URL.revokeObjectURL(sample.url);
    Object.assign(sample, { blob: null, peaks: null, url: null });
    $("#samplePreview").hidden = true;
    $("#quality").innerHTML = "";
    $("#fileInput").value = "";
    updateSaveState();
  }
  $("#sampleClear").addEventListener("click", resetSample);

  async function acceptAudio(arrayBuffer, sourceName) {
    let decoded;
    try { decoded = await decodeAudio(arrayBuffer); } catch {
      toast("Your browser couldn't read that file. Try WAV or MP3.", "error"); return;
    }
    const mono = await toMono24k(decoded);
    let peak = 0, sum = 0;
    for (let i = 0; i < mono.length; i++) { const a = Math.abs(mono[i]); if (a > peak) peak = a; sum += mono[i] * mono[i]; }
    const rmsDb = 20 * Math.log10(Math.sqrt(sum / Math.max(1, mono.length)) + 1e-9);
    const secs = mono.length / 24000;
    sample.blob = encodeWav(mono);
    sample.url = URL.createObjectURL(sample.blob);
    sample.audio.src = sample.url;
    sample.peaks = computePeaks(mono, 300);
    $("#samplePreview").hidden = false;
    $("#sampleDur").textContent = fmtTime(secs);
    paintWave($("#sampleWave"), sample.peaks, 0);

    const q = [];
    if (secs < 5) q.push(["bad", `Only ${secs.toFixed(1)}s. At least 5s is required; 10–30s gives the best clone.`]);
    else if (secs < 10) q.push(["warn", `${secs.toFixed(1)}s works, but 10–30s gives a more faithful clone.`]);
    else if (secs > 40) q.push(["warn", `${Math.round(secs)}s. Only the first 40s of speech is used.`]);
    else q.push(["", `${Math.round(secs)}s — a good length.`]);
    if (peak > 0.995) q.push(["warn", "Audio is clipping (too loud). Distortion will be copied into the clone."]);
    if (rmsDb < -38) q.push(["warn", "Recording is very quiet. Move closer to the microphone if you can."]);
    else if (peak <= 0.995) q.push(["", "Levels look healthy."]);
    q.push(["", "Best results: one speaker, no music, no echo, no background noise."]);
    $("#quality").innerHTML = q.map(([c, t]) => `<li class="${c}">${esc(t)}</li>`).join("");
    if (!$("#voiceName").value && sourceName) $("#voiceName").value = sourceName.replace(/\.[^.]+$/, "").replace(/[_-]+/g, " ").slice(0, 60);
    sample.secs = secs;
    updateSaveState();
  }

  const samplePlay = $("#samplePlay");
  samplePlay.addEventListener("click", () => { if (sample.audio.paused) sample.audio.play(); else sample.audio.pause(); });
  sample.audio.addEventListener("play", () => {
    samplePlay.classList.add("playing");
    const loop = () => { paintWave($("#sampleWave"), sample.peaks, sample.progress()); if (!sample.audio.paused) requestAnimationFrame(loop); };
    loop();
  });
  sample.audio.addEventListener("pause", () => samplePlay.classList.remove("playing"));
  sample.audio.addEventListener("ended", () => { samplePlay.classList.remove("playing"); paintWave($("#sampleWave"), sample.peaks, 0); });

  // upload
  const drop = $("#drop");
  $("#fileInput").addEventListener("change", async (e) => {
    const f = e.target.files[0];
    if (f) acceptAudio(await f.arrayBuffer(), f.name);
  });
  ["dragenter", "dragover"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("over"); }));
  ["dragleave", "drop"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove("over"); }));
  drop.addEventListener("drop", async (e) => {
    const f = e.dataTransfer.files[0];
    if (f) acceptAudio(await f.arrayBuffer(), f.name);
  });

  // record
  const rec = { media: null, stream: null, chunks: [], start: 0, timer: 0, analyser: null, raf: 0 };
  $("#recBtn").addEventListener("click", () => (rec.media ? stopRecording() : startRecording()));
  async function startRecording() {
    if (!navigator.mediaDevices?.getUserMedia) { toast("Recording isn't available in this browser. Upload a file instead.", "error"); return; }
    try {
      rec.stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: false, noiseSuppression: true, autoGainControl: true } });
    } catch {
      toast("Microphone access was blocked. Allow it in your browser settings, or upload a file.", "error"); return;
    }
    resetSample();
    rec.chunks = [];
    rec.media = new MediaRecorder(rec.stream);
    rec.media.ondataavailable = (e) => e.data.size && rec.chunks.push(e.data);
    rec.media.onstop = async () => {
      if (rec.discard) return;
      const blob = new Blob(rec.chunks, { type: rec.media?.mimeType || "audio/webm" });
      acceptAudio(await blob.arrayBuffer(), "");
      if (!$("#voiceName").value) $("#voiceName").value = "My voice";
    };
    rec.discard = false;
    rec.media.start();
    rec.start = Date.now();
    $("#recBtn").classList.add("recording");
    $("#recLabel").textContent = "Stop recording";
    rec.timer = setInterval(() => {
      const s = (Date.now() - rec.start) / 1000;
      $("#recTime").textContent = fmtTime(s);
      if (s >= 45) stopRecording();
    }, 250);
    const ctx = audioCtx();
    if (ctx.state === "suspended") ctx.resume();
    const src = ctx.createMediaStreamSource(rec.stream);
    rec.analyser = ctx.createAnalyser();
    rec.analyser.fftSize = 1024;
    src.connect(rec.analyser);
    const data = new Float32Array(rec.analyser.fftSize);
    const meter = () => {
      if (!rec.analyser) return;
      rec.analyser.getFloatTimeDomainData(data);
      let m = 0; for (const x of data) m = Math.max(m, Math.abs(x));
      const fill = $("#meterFill");
      fill.style.width = `${Math.min(100, m * 140)}%`;
      fill.style.background = m > 0.95 ? "var(--danger)" : m < 0.05 ? "var(--warn)" : "var(--ok)";
      rec.raf = requestAnimationFrame(meter);
    };
    meter();
  }
  function stopRecording(discard = false) {
    if (!rec.media) return;
    rec.discard = discard;
    clearInterval(rec.timer);
    cancelAnimationFrame(rec.raf);
    rec.analyser = null;
    try { rec.media.stop(); } catch { /* already stopped */ }
    rec.stream.getTracks().forEach((t) => t.stop());
    rec.media = null;
    $("#recBtn").classList.remove("recording");
    $("#recLabel").textContent = "Record again";
    $("#meterFill").style.width = "0";
  }

  function updateSaveState() {
    $("#saveVoice").disabled = !(sample.blob && sample.secs >= 5 && $("#voiceName").value.trim() && $("#consent").checked);
  }
  ["#voiceName", "#consent"].forEach((s) => $(s).addEventListener("input", updateSaveState));
  $("#consent").addEventListener("change", updateSaveState);

  $("#saveVoice").addEventListener("click", async () => {
    const btn = $("#saveVoice");
    btn.disabled = true;
    btn.textContent = "Saving…";
    const fd = new FormData();
    fd.append("name", $("#voiceName").value.trim());
    fd.append("description", $("#voiceDesc").value.trim());
    fd.append("language", $("#voiceLang").value);
    fd.append("consent", $("#consent").checked ? "true" : "false");
    fd.append("file", sample.blob, "sample.wav");
    try {
      const v = await api("/api/voices", { method: "POST", body: fd });
      closeModals();
      await loadVoices();
      selectVoice(v.id);
      $("#language").value = v.language; $("#language").dataset.touched = "";
      toast(`“${v.name}” saved. It's now selected.`);
    } catch (err) {
      toast(err.message, "error");
    } finally {
      btn.textContent = "Save voice";
      updateSaveState();
    }
  });

  // ---------------- theme ----------------
  const applyTheme = (t) => { document.documentElement.dataset.theme = t; store.set("theme", t); drawWave(); };
  applyTheme(store.get("theme", matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));
  $("#themeToggle").addEventListener("click", () => applyTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark"));

  // ---------------- boot ----------------
  (async () => {
    onText();
    route();
    await Promise.all([loadStatus(), loadVoices().catch((e) => toast(e.message, "error")), loadHistory()]);
    route();
    setInterval(loadStatus, 15000);
  })();
})();
