/* Swara core: helpers, API, jobs, player, voice picker. Everything hangs off window.SW. */
(() => {
  "use strict";
  const SW = (window.SW = {});

  // ---------- helpers ----------
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const store = {
    get(k, d) { try { const v = localStorage.getItem("sw." + k); return v == null ? d : JSON.parse(v); } catch { return d; } },
    set(k, v) { try { localStorage.setItem("sw." + k, JSON.stringify(v)); } catch { /* private window */ } },
  };
  const fmtTime = (s) => { s = Math.max(0, Math.round(s || 0)); const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), r = s % 60; return (h ? `${h}:${String(m).padStart(2, "0")}` : `${m}`) + `:${String(r).padStart(2, "0")}`; };
  const fmtTC = (s) => { s = Math.max(0, s || 0); const m = Math.floor(s / 60), r = s - m * 60; return `${String(m).padStart(2, "0")}:${r.toFixed(1).padStart(4, "0")}`; };
  const fmtDate = (t) => {
    const d = new Date(t * 1000), now = new Date();
    const time = d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
    if (d.toDateString() === now.toDateString()) return `Today ${time}`;
    const y = new Date(now); y.setDate(now.getDate() - 1);
    if (d.toDateString() === y.toDateString()) return `Yesterday ${time}`;
    return d.toLocaleDateString([], { day: "numeric", month: "short" }) + ` ${time}`;
  };
  const isMac = /Mac|iPhone|iPad/.test(navigator.platform);
  Object.assign(SW, { $, $$, esc, store, fmtTime, fmtTC, fmtDate, isMac });

  async function api(path, opts = {}) {
    let res;
    try { res = await fetch(path, opts); } catch { throw new Error("Swara's engine isn't responding. Is the Swara window still open?"); }
    if (!res.ok) {
      let msg = `Something went wrong (${res.status}).`;
      try { const j = await res.json(); msg = j.error || (Array.isArray(j.detail) ? j.detail.map((d) => d.msg).join(", ") : j.detail) || msg; } catch { /* not json */ }
      throw new Error(msg);
    }
    const type = res.headers.get("content-type") || "";
    return type.includes("json") ? res.json() : res;
  }
  SW.api = api;
  SW.json = (path, body, method = "POST") => api(path, { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });

  SW.toast = (msg, type = "") => {
    const el = document.createElement("div");
    el.className = "toast " + type;
    el.textContent = msg;
    $("#toasts").append(el);
    setTimeout(() => el.remove(), type === "error" ? 7000 : 3200);
  };

  SW.ICON = {
    play: '<svg class="i-play" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg><svg class="i-pause" viewBox="0 0 24 24"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg>',
    check: '<svg viewBox="0 0 24 24"><path d="m5 12 5 5L20 7"/></svg>',
    mic: '<svg viewBox="0 0 24 24"><path d="M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3z"/><path d="M5 11a7 7 0 0 0 14 0"/></svg>',
    trash: '<svg viewBox="0 0 24 24"><path d="M4 7h16M10 11v6M14 11v6M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12M9 7V4h6v3"/></svg>',
    edit: '<svg viewBox="0 0 24 24"><path d="M4 20h4L19 9l-4-4L4 16z"/></svg>',
    redo: '<svg viewBox="0 0 24 24"><path d="M20 11a8 8 0 1 0-2.3 5.7"/><path d="M20 4v7h-7"/></svg>',
    reuse: '<svg viewBox="0 0 24 24"><path d="M9 14 4 9l5-5"/><path d="M4 9h11a5 5 0 0 1 0 10h-3"/></svg>',
    more: '<svg viewBox="0 0 24 24"><circle cx="5" cy="12" r="1.3"/><circle cx="12" cy="12" r="1.3"/><circle cx="19" cy="12" r="1.3"/></svg>',
    plus: '<svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>',
    up: '<svg viewBox="0 0 24 24"><path d="M12 19V5m-6 6 6-6 6 6"/></svg>',
    down: '<svg viewBox="0 0 24 24"><path d="M12 5v14m6-6-6 6-6-6"/></svg>',
    chev: '<svg viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"/></svg>',
  };

  // ---------- voices ----------
  SW.state = { status: null, voices: { presets: [], clones: [], clone_languages: {}, preset_languages: {} }, history: [] };
  SW.allVoices = () => [...SW.state.voices.clones, ...SW.state.voices.presets];
  SW.voice = (id) => SW.allVoices().find((v) => v.id === id);
  SW.voiceMeta = (v) => {
    if (!v) return "Voice not found";
    if (v.kind === "clone") return `Your clone · ${SW.state.voices.clone_languages[v.language] || "English"}`;
    return `${v.language} · ${v.gender === "female" ? "Female" : "Male"}`;
  };
  const DISC = ["#ffd83d", "#ff9cc2", "#7fe0a6", "#84c8ff", "#ffb661", "#c9adff", "#9be3e0", "#f4a39a"];
  SW.discColor = (id) => { let h = 0; for (const c of id || "") h = (h * 31 + c.charCodeAt(0)) >>> 0; return DISC[h % DISC.length]; };
  SW.disc = (v, cls = "") => `<span class="disc ${cls}" style="--dc:${SW.discColor(v?.id)}" aria-hidden="true">${v?.kind === "clone" ? `<span class="tag-clone">${SW.ICON.mic}</span>` : ""}</span>`;
  SW.voicePickHTML = (v) => `${SW.disc(v)}<span class="vp-text"><span class="vp-name">${esc(v ? v.name : "Choose a voice")}</span><span class="vp-meta">${esc(SW.voiceMeta(v))}</span></span>${SW.ICON.chev}`;
  SW.CAST = ["var(--c0)", "var(--c1)", "var(--c2)", "var(--c3)", "var(--c4)", "var(--c5)"];

  SW.loadVoices = async () => {
    SW.state.voices = await api("/api/voices");
    const n = SW.state.voices.clones.length;
    $("#voiceCount").textContent = n ? n : "";
    document.dispatchEvent(new CustomEvent("sw:voices"));
  };
  SW.languageOptions = (withAuto = false) => {
    const langs = Object.entries(SW.state.voices.clone_languages)
      .sort((a, b) => (a[0] === "en" ? -1 : b[0] === "en" ? 1 : a[0] === "hi" ? -1 : b[0] === "hi" ? 1 : a[1].localeCompare(b[1])));
    return (withAuto ? `<option value="">Detect automatically</option>` : "") + langs.map(([k, n]) => `<option value="${k}">${esc(n)}</option>`).join("");
  };

  // ---------- modals ----------
  SW.openModal = (sel) => { $(sel).hidden = false; };
  SW.closeModals = () => {
    $$(".modal").forEach((m) => { if (!m.hidden && m.id) { m.hidden = true; m.dispatchEvent(new Event("close")); } });
    SW.stopPreview();
  };
  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("modal") && e.target.id) SW.closeModals();
    if (e.target.closest("[data-close]")) SW.closeModals();
  });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") { SW.closeModals(); $$(".menu").forEach((m) => (m.hidden = true)); } });

  SW.dialog = ({ title, body = "", input = null, confirm = "OK", danger = false }) => new Promise((resolve) => {
    const wrap = document.createElement("div");
    wrap.className = "modal";
    wrap.innerHTML = `<div class="sheet-modal" role="dialog" aria-modal="true" style="width:min(420px,100%)">
      <div class="modal-head"><h2>${esc(title)}</h2></div>
      ${body ? `<p class="muted" style="margin:0 0 6px">${esc(body)}</p>` : ""}
      ${input != null ? `<input class="input" value="${esc(input)}" maxlength="80">` : ""}
      <div class="modal-foot"><button class="btn" data-x>Cancel</button><button class="btn ${danger ? "" : "primary"}" data-ok ${danger ? 'style="background:var(--danger);border-color:var(--danger);color:#fff"' : ""}>${esc(confirm)}</button></div></div>`;
    document.body.append(wrap);
    const inp = $("input", wrap);
    const done = (v) => { wrap.remove(); resolve(v); };
    $("[data-ok]", wrap).onclick = () => done(inp ? inp.value : true);
    $("[data-x]", wrap).onclick = () => done(null);
    wrap.onclick = (e) => { if (e.target === wrap) done(null); };
    wrap.onkeydown = (e) => { if (e.key === "Enter") done(inp ? inp.value : true); if (e.key === "Escape") { e.stopPropagation(); done(null); } };
    setTimeout(() => { (inp || $("[data-ok]", wrap)).focus(); inp?.select(); }, 30);
  });

  // ---------- downloads (browser or desktop window) ----------
  SW.download = async (url, filename) => {
    if (window.pywebview?.api?.save_file) {
      try {
        const saved = await window.pywebview.api.save_file(url, filename);
        if (saved) SW.toast(`Saved to ${saved}`);
      } catch (e) { SW.toast("Couldn't save the file: " + e, "error"); }
      return;
    }
    // Check first, so an export error shows as a message instead of a broken download.
    try {
      const res = await fetch(url, { method: "GET" });
      if (!res.ok) { let m = "Download failed."; try { m = (await res.json()).error || m; } catch { /* */ } throw new Error(m); }
      const blob = await res.blob();
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = filename;
      document.body.append(a);
      a.click();
      setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 2000);
    } catch (e) { SW.toast(e.message, "error"); }
  };
  document.addEventListener("click", (e) => {
    const a = e.target.closest("a[data-dl]");
    if (!a || !a.dataset.url) return;
    e.preventDefault();
    SW.download(a.dataset.url, a.dataset.name || "swara-audio");
  });

  // ---------- jobs ----------
  // trackJob polls a job and drives a progress block (.progress with .bar i, .ptext, [data-cancel]).
  SW.trackJob = (job, { progress, button, label, onDone, onEnd } = {}) => new Promise((resolve) => {
    const bar = progress && $(".bar", progress), fill = progress && $(".bar i", progress), text = progress && $(".ptext", progress);
    const btnLabel = button && $(".lbl", button), orig = btnLabel?.textContent;
    if (progress) { progress.hidden = false; fill.style.width = "0"; text.textContent = "Starting…"; }
    if (button) { button.disabled = true; if (btnLabel) btnLabel.textContent = label || "Working…"; }
    const cancelBtn = progress && $("[data-cancel]", progress);
    if (cancelBtn) cancelBtn.onclick = async () => { text.textContent = "Stopping after the current part…"; try { await api(`/api/jobs/${job.id}/cancel`, { method: "POST" }); } catch { /* */ } };
    SW.queue.kick();
    const finish = (j) => {
      if (progress) { progress.hidden = true; bar.classList.remove("indet"); }
      if (button) { button.disabled = false; if (btnLabel) btnLabel.textContent = orig; }
      SW.queue.kick();
      onEnd?.(j);
      resolve(j);
    };
    const tick = async () => {
      let j;
      try { j = await api(`/api/jobs/${job.id}`); } catch (e) { SW.toast(e.message, "error"); finish(null); return; }
      if (progress) {
        if (j.status === "queued") { bar.classList.add("indet"); text.textContent = j.position > 1 ? `Waiting in queue · #${j.position}` : "Waiting for the engine…"; }
        else if (j.status === "running" && j.total) {
          bar.classList.remove("indet");
          fill.style.width = `${Math.round((j.done / j.total) * 100)}%`;
          text.textContent = SW.progressText(j);
        } else if (j.status === "running") {
          bar.classList.add("indet");
          text.textContent = j.elapsed > 5 ? "Loading the voice model. The first run of the day takes up to a minute…" : "Preparing…";
        }
      }
      if (j.status === "done") { finish(j); onDone?.(j); return; }
      if (j.status === "error") { SW.toast(j.error || "That didn't work.", "error"); finish(j); return; }
      if (j.status === "cancelled") { SW.toast("Stopped."); finish(j); return; }
      setTimeout(tick, 700);
    };
    tick();
  });
  SW.progressText = (j) => {
    if (j.kind === "transcribe") return `Transcribed ${fmtTime(j.done)} of ${fmtTime(j.total)} · ${fmtTime(j.elapsed)}`;
    if (j.kind === "studio") return `Line ${Math.min(j.done + 1, j.total)} of ${j.total} · ${fmtTime(j.elapsed)}`;
    return `Part ${Math.min(j.done + 1, j.total)} of ${j.total} · ${fmtTime(j.elapsed)}`;
  };

  // Rail queue indicator: shows whatever the engine is working on.
  SW.queue = (() => {
    let timer = 0;
    const el = $("#queue");
    async function poll() {
      clearTimeout(timer);
      let items = [];
      try { items = (await api("/api/jobs")).items; } catch { /* engine down */ }
      el.classList.toggle("on", items.length > 0);
      el.innerHTML = items.slice(0, 3).map((j) => {
        const pct = j.total ? Math.round((j.done / j.total) * 100) : 0;
        const kind = { tts: "Speech", studio: "Studio", changer: "Voice Changer", transcribe: "Transcribing" }[j.kind] || "Working";
        return `<div><div class="queue-row"><span>${esc(kind)} · ${esc(j.label)}</span><span class="num">${j.status === "queued" ? "queued" : pct + "%"}</span></div><div class="bar"><i style="width:${pct}%"></i></div></div>`;
      }).join("") + (items.length > 3 ? `<div class="muted">+${items.length - 3} more</div>` : "");
      if (items.length) timer = setTimeout(poll, 1000);
    }
    return { kick: () => setTimeout(poll, 50) };
  })();

  // ---------- audio utilities ----------
  let _ctx;
  SW.audioCtx = () => (_ctx ||= new (window.AudioContext || window.webkitAudioContext)());
  SW.decode = (buf) => new Promise((res, rej) => SW.audioCtx().decodeAudioData(buf.slice(0), res, rej));
  SW.toMono = async (audioBuffer, rate = 24000) => {
    const off = new OfflineAudioContext(1, Math.ceil(audioBuffer.duration * rate), rate);
    const src = off.createBufferSource();
    src.buffer = audioBuffer; src.connect(off.destination); src.start();
    return (await off.startRendering()).getChannelData(0);
  };
  SW.encodeWav = (samples, rate = 24000) => {
    const buf = new ArrayBuffer(44 + samples.length * 2), v = new DataView(buf);
    const w = (o, s) => [...s].forEach((c, i) => v.setUint8(o + i, c.charCodeAt(0)));
    w(0, "RIFF"); v.setUint32(4, 36 + samples.length * 2, true); w(8, "WAVE"); w(12, "fmt ");
    v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true); v.setUint32(24, rate, true);
    v.setUint32(28, rate * 2, true); v.setUint16(32, 2, true); v.setUint16(34, 16, true); w(36, "data"); v.setUint32(40, samples.length * 2, true);
    for (let i = 0; i < samples.length; i++) v.setInt16(44 + i * 2, Math.max(-1, Math.min(1, samples[i])) * 0x7fff, true);
    return new Blob([buf], { type: "audio/wav" });
  };
  SW.peaks = (data, n) => {
    const out = new Float32Array(n), step = Math.max(1, Math.floor(data.length / n));
    let max = 0;
    for (let i = 0; i < n; i++) {
      let m = 0;
      for (let j = i * step, e = Math.min(data.length, j + step); j < e; j++) { const a = Math.abs(data[j]); if (a > m) m = a; }
      out[i] = m; if (m > max) max = m;
    }
    if (max > 0) for (let i = 0; i < n; i++) out[i] = Math.pow(out[i] / max, 0.75);
    return out;
  };
  const cssVar = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  SW.paintWave = (cv, peaks, progress, { played = cssVar("--hl"), rest = cssVar("--booth-line") } = {}) => {
    const dpr = window.devicePixelRatio || 1, w = cv.clientWidth, h = cv.clientHeight;
    if (!w) return;
    if (cv.width !== Math.round(w * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); }
    const ctx = cv.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    const bar = 2, gap = 2, n = Math.floor(w / (bar + gap));
    for (let i = 0; i < n; i++) {
      const p = peaks ? peaks[Math.floor((i / n) * peaks.length)] : 0.06;
      const bh = Math.max(2, p * (h - 4));
      ctx.fillStyle = i / n < progress ? played : rest;
      ctx.fillRect(i * (bar + gap), (h - bh) / 2, bar, bh);
    }
  };

  // ---------- player ----------
  const audioEl = $("#audio"), canvas = $("#waveCanvas");
  const player = (SW.player = { item: null, peaks: null, raf: 0 });
  // item: { key, title, sub, url, mp3, wav, name }
  player.play = async (item, autoplay = true) => {
    SW.stopPreview();
    player.item = item;
    $("#player").hidden = false;
    $("#pTitle").textContent = item.title;
    $("#pSub").textContent = item.sub || "";
    const set = (el, url, ext) => { el.hidden = !url; el.dataset.url = url || ""; el.dataset.name = `${item.name || "swara"}.${ext}`; el.href = url || "#"; };
    set($("#pMp3"), item.mp3, "mp3");
    set($("#pWav"), item.wav, "wav");
    audioEl.src = item.url;
    player.peaks = null;
    draw();
    if (autoplay) audioEl.play().catch(() => {});
    document.dispatchEvent(new CustomEvent("sw:player"));
    try {
      const decoded = await SW.decode(await (await fetch(item.url)).arrayBuffer());
      if (player.item === item) { player.peaks = SW.peaks(decoded.getChannelData(0), 700); draw(); }
    } catch { /* waveform is decorative */ }
  };
  player.toggle = () => { if (audioEl.paused) audioEl.play(); else audioEl.pause(); };
  player.isPlaying = (key) => player.item?.key === key && !audioEl.paused;
  player.close = () => { audioEl.pause(); $("#player").hidden = true; player.item = null; document.dispatchEvent(new CustomEvent("sw:player")); };
  const draw = () => SW.paintWave(canvas, player.peaks, audioEl.duration ? audioEl.currentTime / audioEl.duration : 0);
  const tick = () => { draw(); $("#tCur").textContent = fmtTime(audioEl.currentTime); if (!audioEl.paused) player.raf = requestAnimationFrame(tick); };
  const sync = () => { $("#playBtn").classList.toggle("playing", !audioEl.paused); document.dispatchEvent(new CustomEvent("sw:player")); };
  audioEl.addEventListener("play", () => { SW.stopPreview(); sync(); tick(); });
  audioEl.addEventListener("pause", () => { sync(); cancelAnimationFrame(player.raf); draw(); });
  audioEl.addEventListener("ended", () => { sync(); draw(); player.onEnded?.(); });
  audioEl.addEventListener("loadedmetadata", () => { $("#tDur").textContent = fmtTime(audioEl.duration); });
  $("#playBtn").addEventListener("click", player.toggle);
  $("#pClose").addEventListener("click", player.close);
  canvas.addEventListener("click", (e) => {
    if (!audioEl.duration) return;
    const r = canvas.getBoundingClientRect();
    audioEl.currentTime = ((e.clientX - r.left) / r.width) * audioEl.duration;
    $("#tCur").textContent = fmtTime(audioEl.currentTime);
    draw();
  });
  window.addEventListener("resize", draw);
  document.addEventListener("keydown", (e) => {
    if (e.code === "Space" && player.item && !e.target.closest("input, textarea, select, button, a, [contenteditable]")) { e.preventDefault(); player.toggle(); }
  });
  SW.historyItem = (h) => ({
    key: "h:" + h.id, title: h.voice_name, sub: h.text, url: `/api/history/${h.id}/audio`,
    mp3: `/api/history/${h.id}/audio?format=mp3&download=1`, wav: `/api/history/${h.id}/audio?format=wav&download=1`, name: `swara-${h.id}`,
  });

  // ---------- voice previews ----------
  const pv = $("#previewAudio");
  let pvBtn = null;
  SW.stopPreview = () => { pv.pause(); pvBtn?.classList.remove("playing", "loading"); pvBtn = null; };
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-preview]");
    if (!btn) return;
    e.stopPropagation();
    if (pvBtn === btn) { SW.stopPreview(); return; }
    SW.stopPreview();
    audioEl.pause();
    pvBtn = btn;
    btn.classList.add("loading");
    pv.src = `/api/voices/${encodeURIComponent(btn.dataset.preview)}/preview`;
    pv.play().then(() => btn.classList.replace("loading", "playing")).catch(() => { btn.classList.remove("loading"); SW.toast("Couldn't play that preview.", "error"); });
  }, true);
  pv.addEventListener("ended", SW.stopPreview);

  // ---------- voice picker ----------
  let onPick = null, pickedId = null;
  SW.pickVoice = (currentId, cb, { title = "Choose a voice" } = {}) => {
    onPick = cb; pickedId = currentId;
    $("#pickerModal h2").textContent = title;
    $("#pickerSearch").value = "";
    renderPicker();
    SW.openModal("#pickerModal");
    setTimeout(() => $("#pickerSearch").focus(), 40);
  };
  function renderPicker() {
    const q = $("#pickerSearch").value.trim().toLowerCase();
    const match = (v) => !q || `${v.name} ${SW.voiceMeta(v)} ${v.description || ""}`.toLowerCase().includes(q);
    const row = (v) => `<div class="prow ${v.id === pickedId ? "sel" : ""}" data-id="${esc(v.id)}" role="option" aria-selected="${v.id === pickedId}" tabindex="0">
        ${SW.disc(v)}<div class="p-text"><div class="p-name">${esc(v.name)}</div><div class="p-meta">${esc(SW.voiceMeta(v))}</div></div>
        <button class="play sm light" data-preview="${esc(v.id)}" aria-label="Hear ${esc(v.name)}">${SW.ICON.play}</button>
        <span class="tick">${v.id === pickedId ? SW.ICON.check : ""}</span></div>`;
    let html = "";
    const clones = SW.state.voices.clones.filter(match);
    if (clones.length) html += `<div class="pgroup">Your voices</div>` + clones.map(row).join("");
    else if (!q) html += `<div class="prow" data-add-voice tabindex="0"><span class="disc" style="--dc:var(--paper-2)"></span><div class="p-text"><div class="p-name">Clone your own voice</div><div class="p-meta">Upload or record 10–30 seconds of speech</div></div></div>`;
    for (const [code, label] of Object.entries(SW.state.voices.preset_languages)) {
      const list = SW.state.voices.presets.filter((v) => v.lang_code === code && match(v));
      if (list.length) html += `<div class="pgroup">${esc(label)}</div>` + list.map(row).join("");
    }
    $("#pickerList").innerHTML = html || `<div class="empty" style="margin:6px">No voices match “${esc(q)}”.</div>`;
  }
  $("#pickerSearch").addEventListener("input", renderPicker);
  const choose = (row) => { if (!row?.dataset.id) return; const id = row.dataset.id; SW.closeModals(); onPick?.(id); };
  $("#pickerList").addEventListener("click", (e) => { if (!e.target.closest("[data-preview]")) choose(e.target.closest(".prow")); });
  $("#pickerList").addEventListener("keydown", (e) => { if (e.key === "Enter") choose(e.target.closest(".prow")); });

  // ---------- history rows (shared by several views) ----------
  SW.historyRow = (h) => {
    const playing = SW.player.isPlaying("h:" + h.id);
    const kind = h.kind === "changer" ? `<span class="badge">Voice Changer</span>` : "";
    return `<div class="row ${SW.player.item?.key === "h:" + h.id ? "playing" : ""}" data-hid="${esc(h.id)}">
      <button class="play sm ${playing ? "playing" : ""}" data-hplay aria-label="Play">${SW.ICON.play}</button>
      <div style="min-width:0"><div class="row-title">${esc(h.text)}</div>
        <div class="row-meta"><b>${esc(h.voice_name)}</b>${kind}<span class="num">${fmtTime(h.duration)}</span><span>${fmtDate(h.created)}</span><span>made in ${h.render_seconds}s</span></div></div>
      <div class="row-actions">
        ${h.kind !== "changer" ? `<button class="icon-btn" data-hreuse title="Open in Text to Speech" aria-label="Open in Text to Speech">${SW.ICON.reuse}</button>` : ""}
        <a class="icon-btn fmt" data-dl data-url="/api/history/${h.id}/audio?format=mp3&download=1" data-name="swara-${h.id}.mp3" href="#" title="Download MP3">MP3</a>
        <a class="icon-btn fmt" data-dl data-url="/api/history/${h.id}/audio?format=wav&download=1" data-name="swara-${h.id}.wav" href="#" title="Download WAV">WAV</a>
        <button class="icon-btn" data-hdel title="Delete" aria-label="Delete">${SW.ICON.trash}</button>
      </div></div>`;
  };
  SW.historyList = (items, empty) => items.length ? `<div class="rows">${items.map(SW.historyRow).join("")}</div>` : `<div class="empty">${empty}</div>`;
  SW.loadHistory = async () => {
    try { SW.state.history = (await api("/api/history")).items; } catch { SW.state.history = []; }
    document.dispatchEvent(new CustomEvent("sw:history"));
  };
  document.addEventListener("click", async (e) => {
    const row = e.target.closest(".row[data-hid]");
    if (!row) return;
    const h = SW.state.history.find((x) => x.id === row.dataset.hid);
    if (!h) return;
    if (e.target.closest("[data-hplay]")) {
      if (SW.player.item?.key === "h:" + h.id) SW.player.toggle(); else SW.player.play(SW.historyItem(h));
    } else if (e.target.closest("[data-hreuse]")) {
      document.dispatchEvent(new CustomEvent("sw:reuse", { detail: h }));
    } else if (e.target.closest("[data-hdel]")) {
      if (!(await SW.dialog({ title: "Delete this audio?", body: "It's removed from this computer.", confirm: "Delete", danger: true }))) return;
      try {
        await api(`/api/history/${h.id}`, { method: "DELETE" });
        if (SW.player.item?.key === "h:" + h.id) SW.player.close();
        await SW.loadHistory();
      } catch (err) { SW.toast(err.message, "error"); }
    }
  });
  document.addEventListener("sw:player", () => {
    $$(".row[data-hid]").forEach((r) => {
      const me = SW.player.item?.key === "h:" + r.dataset.hid;
      r.classList.toggle("playing", me);
      $("[data-hplay]", r)?.classList.toggle("playing", me && !audioEl.paused);
    });
  });
})();
