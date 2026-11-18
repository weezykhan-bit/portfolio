/* Routing, theme and startup. */
(() => {
  "use strict";
  const { $, $$, store } = SW;
  const VIEWS = ["speech", "studio", "changer", "transcribe", "voices", "history", "pronunciations"];
  const TITLES = { speech: "Text to Speech", studio: "Studio", changer: "Voice Changer", transcribe: "Speech to Text", voices: "Voices", history: "History", pronunciations: "Pronunciations" };

  function route() {
    const [view0, sub] = (location.hash || "#speech").slice(1).split("/");
    const view = VIEWS.includes(view0) ? view0 : "speech";
    VIEWS.forEach((v) => ($("#view-" + v).hidden = v !== view));
    $$(".nav a").forEach((a) => a.classList.toggle("active", a.dataset.view === view));
    document.title = `${TITLES[view]} · Swara`;
    if (view === "studio") SW.studio.route(sub);
    if (view === "transcribe") SW.transcribe.route(sub);
    if (view === "pronunciations") SW.lexicon.route();
    $("#main").scrollTop = 0;
  }
  window.addEventListener("hashchange", route);

  const applyTheme = (t) => { document.documentElement.dataset.theme = t; store.set("theme", t); window.dispatchEvent(new Event("resize")); };
  $("#themeToggle").addEventListener("click", () => applyTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark"));

  async function status() {
    try {
      SW.state.status = await SW.api("/api/status");
      $("#device").textContent = SW.state.status.device_label;
      $("#ttsMax").textContent = SW.state.status.max_text_chars.toLocaleString();
      SW.speech.onStatus();
    } catch { $("#device").textContent = "Engine offline"; }
  }

  (async () => {
    route();
    await Promise.all([status(), SW.loadVoices().catch((e) => SW.toast(e.message, "error")), SW.loadHistory()]);
    route();
    SW.queue.kick();
    setInterval(status, 20000);
  })();
})();
