/* Text to Speech view. */
(() => {
  "use strict";
  const { $, $$, store, fmtTime } = SW;
  const text = $("#ttsText");
  const DEFAULTS = { speed: 1, exaggeration: 0.5, cfg: 0.5, temperature: 0.8 };
  const fmt = { speed: (v) => `${(+v).toFixed(2)}×`, exaggeration: (v) => (+v).toFixed(2), cfg: (v) => (+v).toFixed(2), temperature: (v) => (+v).toFixed(2) };
  let voiceId = store.get("ttsVoice", "preset:af_heart");
  let busy = false;

  const SAMPLES = {
    promo: "This Friday. One family. One secret that could change everything.\n\nThe new season of Ghar Wapsi premieres at 9 PM, only on your favourite channel. Don't miss it.",
    narration: "Every great journey begins with a single decision. Ours began on a rainy Tuesday morning, in a small studio above a bakery, with nothing but a microphone and an idea.\n\nWhat happened next surprised everyone, including us.",
    ad: "Tired of paying every month just to hear your own words out loud? Swara turns any script into lifelike speech, in your own voice, without a subscription. It all runs on your computer.",
    hindi: "नमस्ते! स्वरा पूरी तरह आपके अपने कंप्यूटर पर चलता है। बस अपनी स्क्रिप्ट लिखिए, आवाज़ चुनिए, और सुनिए।",
  };

  // ----- voice -----
  function render() {
    const v = SW.voice(voiceId);
    $("#ttsVoice").innerHTML = SW.voicePickHTML(v);
    const clone = v?.kind === "clone";
    $("#ttsClone").hidden = !clone;
    $("#ttsPreset").hidden = clone;
    $("#ttsCue").textContent = v ? v.name : "No voice";
    $("#ttsCue").style.setProperty("--cue", SW.discColor(v?.id));
    $("#ttsCueMeta").textContent = SW.voiceMeta(v);
    if (clone && !$("#ttsLang").dataset.touched) $("#ttsLang").value = v.language || "en";
    estimate();
  }
  function setVoice(id) {
    voiceId = id;
    store.set("ttsVoice", id);
    $("#ttsLang").dataset.touched = "";
    render();
  }
  $("#ttsVoice").addEventListener("click", () => SW.pickVoice(voiceId, setVoice, { title: "Who should read this?" }));
  document.addEventListener("sw:voices", () => {
    $("#ttsLang").innerHTML = SW.languageOptions();
    if (!SW.voice(voiceId)) voiceId = "preset:af_heart";
    render();
  });
  $("#ttsLang").addEventListener("change", (e) => { e.target.dataset.touched = "1"; });

  // ----- sliders -----
  const saved = store.get("ttsSettings", {});
  for (const id of Object.keys(fmt)) {
    const el = $("#" + id), out = el.closest(".slider").querySelector("output");
    if (saved[id] != null) el.value = saved[id];
    const upd = () => { out.textContent = fmt[id](el.value); };
    el.addEventListener("input", () => { upd(); store.set("ttsSettings", Object.fromEntries(Object.keys(fmt).map((k) => [k, +$("#" + k).value]))); estimate(); });
    upd();
  }
  $("#resetSettings").addEventListener("click", () => {
    for (const [k, v] of Object.entries(DEFAULTS)) { $("#" + k).value = v; $("#" + k).dispatchEvent(new Event("input")); }
    $("#seed").value = "";
    SW.toast("Settings reset");
  });

  // ----- text -----
  text.value = store.get("ttsDraft", "");
  function onText() {
    const n = text.value.length, max = SW.state.status?.max_text_chars || 20000;
    $("#ttsCount").textContent = n.toLocaleString();
    $(".counter").classList.toggle("over", n > max);
    store.set("ttsDraft", text.value);
    estimate();
  }
  text.addEventListener("input", onText);
  $$(".chip[data-sample]").forEach((c) => c.addEventListener("click", () => {
    text.value = SAMPLES[c.dataset.sample];
    if (c.dataset.sample === "hindi") {
      const v = SW.voice(voiceId);
      if (v?.kind === "clone") { $("#ttsLang").value = "hi"; $("#ttsLang").dataset.touched = "1"; }
      else if (v?.lang_code !== "h") setVoice("preset:hf_alpha");
    }
    onText();
    text.focus();
  }));

  function estimate() {
    const n = text.value.trim().length, v = SW.voice(voiceId);
    if (!n || !v) { $("#ttsEst").textContent = ""; return; }
    const secs = n / 15 / (v.kind === "preset" ? +$("#speed").value : 1);
    const dev = SW.state.status?.device || "cpu";
    const f = v.kind === "preset" ? (dev === "cuda" ? 0.05 : 0.45) : (dev === "cuda" ? 0.6 : dev === "mps" ? 1.5 : 8);
    const r = secs * f;
    $("#ttsEst").textContent = `About ${fmtTime(secs)} of audio · ready in ${r < 5 ? "a few seconds" : r < 90 ? `about ${Math.round(r)} s` : `about ${Math.round(r / 60)} min`} on this computer`;
  }

  // ----- generate -----
  $(".kbd-go").textContent = SW.isMac ? "⌘ ↵" : "Ctrl ↵";
  $("#ttsGo").addEventListener("click", go);
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter" && !$("#view-speech").hidden) { e.preventDefault(); go(); }
  });
  async function go() {
    if (busy) return;
    const t = text.value.trim();
    if (!t) { SW.toast("Write or paste something first.", "error"); text.focus(); return; }
    const v = SW.voice(voiceId);
    if (!v) { $("#ttsVoice").click(); return; }
    busy = true;
    try {
      const job = await SW.json("/api/generate", {
        text: t, voice_id: v.id, seed: $("#seed").value === "" ? null : Math.max(0, parseInt($("#seed").value, 10) || 0),
        speed: +$("#speed").value, exaggeration: +$("#exaggeration").value, cfg_weight: +$("#cfg").value,
        temperature: +$("#temperature").value, language: v.kind === "clone" ? $("#ttsLang").value : "en",
      });
      await SW.trackJob(job, {
        progress: $("#ttsProgress"), button: $("#ttsGo"), label: "Generating…",
        onDone: async (j) => {
          await SW.loadHistory();
          SW.player.play(SW.historyItem(j.result));
          SW.toast(`Ready in ${j.result.render_seconds} s`);
        },
      });
    } catch (e) { SW.toast(e.message, "error"); }
    busy = false;
  }

  // ----- recent + reuse -----
  document.addEventListener("sw:history", () => {
    const items = SW.state.history.filter((h) => h.kind !== "changer").slice(0, 4);
    $("#ttsRecent").innerHTML = SW.historyList(items, "<strong>Nothing generated yet</strong>Your audio appears here and is saved on this computer.");
  });
  document.addEventListener("sw:reuse", (e) => {
    const h = e.detail, s = h.settings || {};
    text.value = h.text; onText();
    if (SW.voice(h.voice_id)) setVoice(h.voice_id);
    const map = { speed: s.speed, exaggeration: s.exaggeration, cfg: s.cfg_weight, temperature: s.temperature };
    for (const [k, v] of Object.entries(map)) if (v != null) { $("#" + k).value = v; $("#" + k).dispatchEvent(new Event("input")); }
    $("#seed").value = s.seed ?? "";
    if (s.language) { $("#ttsLang").value = s.language; $("#ttsLang").dataset.touched = "1"; }
    location.hash = "#speech";
  });
  SW.speech = { setText: (t) => { text.value = t; onText(); }, onStatus: () => { onText(); } };
})();
