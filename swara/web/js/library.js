/* Voices library, cloning, and History. */
(() => {
  "use strict";
  const { $, $$, esc, store } = SW;
  let filter = store.get("presetFilter", "all");

  // =================== Voices ===================
  function card(v) {
    const inUse = v.id === store.get("ttsVoice", "");
    return `<div class="paper vcard ${inUse ? "selected" : ""}" data-vid="${esc(v.id)}">
      <div class="vcard-top">${SW.disc(v, "lg")}<div style="min-width:0"><div class="vcard-name">${esc(v.name)}</div><div class="vcard-desc">${esc(v.description || SW.voiceMeta(v))}</div></div></div>
      <div class="tags" ${v.kind === "clone" ? "" : "hidden"}>${v.kind === "clone"
        ? `<span class="badge">${esc(SW.state.voices.clone_languages[v.language] || "English")}</span><span class="badge num">${Math.round(v.sample_seconds || 0)} s sample</span>`
        : ""}</div>
      <div class="vcard-actions">
        <button class="play sm light" data-preview="${esc(v.id)}" aria-label="Hear ${esc(v.name)}">${SW.ICON.play}</button>
        <span class="spacer"></span>
        ${v.kind === "clone" ? `<button class="icon-btn" data-rename aria-label="Rename" title="Rename">${SW.ICON.edit}</button><button class="icon-btn" data-vdel aria-label="Delete" title="Delete">${SW.ICON.trash}</button>` : ""}
        <button class="btn sm ${inUse ? "dark" : ""}" data-use>${inUse ? "In use" : "Use"}</button>
      </div></div>`;
  }
  function renderVoices() {
    const clones = SW.state.voices.clones;
    $("#myCount").textContent = clones.length ? `${clones.length} saved` : "";
    $("#myVoices").innerHTML = `<button class="add-tile" data-add-voice><span class="plus">${SW.ICON.plus}</span><strong>Clone a voice</strong><span>Upload or record 10–30 seconds</span></button>` + clones.map(card).join("");
    const langs = { all: "All", ...SW.state.voices.preset_languages };
    $("#presetFilter").innerHTML = Object.entries(langs).map(([k, n]) => `<button data-f="${k}" class="${filter === k ? "active" : ""}">${esc(n)}</button>`).join("");
    $("#presetVoices").innerHTML = SW.state.voices.presets.filter((v) => filter === "all" || v.lang_code === filter).map(card).join("");
  }
  document.addEventListener("sw:voices", renderVoices);
  $("#presetFilter").addEventListener("click", (e) => { const b = e.target.closest("[data-f]"); if (b) { filter = b.dataset.f; store.set("presetFilter", filter); renderVoices(); } });
  $("#view-voices").addEventListener("click", async (e) => {
    const c = e.target.closest("[data-vid]"); if (!c) return;
    const v = SW.voice(c.dataset.vid);
    if (e.target.closest("[data-use]")) { store.set("ttsVoice", v.id); document.dispatchEvent(new CustomEvent("sw:voices")); location.hash = "#speech"; SW.toast(`${v.name} will read your next script`); }
    if (e.target.closest("[data-rename]")) {
      const name = (await SW.dialog({ title: "Rename voice", input: v.name, confirm: "Save" }))?.trim();
      if (name) { try { await SW.json(`/api/voices/${encodeURIComponent(v.id)}`, { name }, "PATCH"); await SW.loadVoices(); } catch (err) { SW.toast(err.message, "error"); } }
    }
    if (e.target.closest("[data-vdel]")) {
      if (!(await SW.dialog({ title: `Delete “${v.name}”?`, body: "The voice sample is removed from this computer. Audio you already made stays in History. Studio characters cast with this voice will need a new one.", confirm: "Delete voice", danger: true }))) return;
      try { await SW.api(`/api/voices/${encodeURIComponent(v.id)}`, { method: "DELETE" }); await SW.loadVoices(); SW.toast("Voice deleted"); } catch (err) { SW.toast(err.message, "error"); }
    }
  });

  // =================== Clone modal ===================
  const cv = SW.source($('[data-source="clone"]'), "clone", () => { if (!$("#cvName").value && cv.name && cv.name !== "Recording") $("#cvName").value = cv.name.replace(/\.[^.]+$/, "").replace(/[_-]+/g, " ").slice(0, 60); ready(); });
  const ready = () => { $("#cvSave").disabled = !(cv.file && cv.secs >= 5 && $("#cvName").value.trim() && $("#cvConsent").checked); };
  ["#cvName", "#cvConsent"].forEach((s) => { $(s).addEventListener("input", ready); $(s).addEventListener("change", ready); });
  SW.openClone = () => {
    cv.reset();
    $("#cvName").value = ""; $("#cvDesc").value = ""; $("#cvLang").value = "en"; $("#cvConsent").checked = false;
    ready();
    SW.openModal("#cloneModal");
  };
  document.addEventListener("click", (e) => { if (e.target.closest("[data-add-voice]")) { SW.closeModals(); SW.openClone(); } });
  $("#cloneModal").addEventListener("close", () => cv.stopRecording());
  document.addEventListener("sw:voices", () => { const cur = $("#cvLang").value; $("#cvLang").innerHTML = SW.languageOptions(); $("#cvLang").value = cur || "en"; });
  $("#cvSave").addEventListener("click", async () => {
    const btn = $("#cvSave");
    btn.disabled = true; btn.textContent = "Saving…";
    const fd = new FormData();
    fd.append("name", $("#cvName").value.trim());
    fd.append("description", $("#cvDesc").value.trim());
    fd.append("language", $("#cvLang").value);
    fd.append("consent", $("#cvConsent").checked ? "true" : "false");
    fd.append("file", cv.file, "sample.wav");
    try {
      const v = await SW.api("/api/voices", { method: "POST", body: fd });
      SW.closeModals();
      store.set("ttsVoice", v.id);
      await SW.loadVoices();
      SW.toast(`“${v.name}” saved and selected`);
    } catch (err) { SW.toast(err.message, "error"); }
    btn.textContent = "Save voice";
    ready();
  });

  // =================== History ===================
  let kind = "all";
  function renderHistory() {
    const q = $("#historySearch").value.trim().toLowerCase();
    const items = SW.state.history.filter((h) => (kind === "all" || (h.kind || "tts") === kind) && (!q || `${h.text} ${h.voice_name}`.toLowerCase().includes(q)));
    $("#historyList").innerHTML = SW.historyList(items, q || kind !== "all" ? "<strong>Nothing matches</strong>Try another search or filter." : "<strong>No history yet</strong>Everything you generate is kept here, on this computer.");
  }
  document.addEventListener("sw:history", renderHistory);
  $("#historySearch").addEventListener("input", renderHistory);
  $("#historyKind").addEventListener("click", (e) => {
    const b = e.target.closest("[data-k]"); if (!b) return;
    kind = b.dataset.k;
    $$("#historyKind button").forEach((x) => x.classList.toggle("active", x === b));
    renderHistory();
  });
})();
