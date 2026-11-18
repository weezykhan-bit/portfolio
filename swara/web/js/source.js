/* Upload-or-record audio input, used by Clone, Voice Changer and Speech to Text. */
(() => {
  "use strict";
  const { $, esc, fmtTime } = SW;

  const KINDS = {
    clone: { accept: "audio/*,.wav,.mp3,.m4a,.ogg,.flac,.webm,.aac", hint: "WAV, MP3, M4A · 10–30 seconds of one person speaking", maxRec: 45, check: true },
    changer: { accept: "audio/*,.wav,.mp3,.m4a,.ogg,.flac,.webm,.aac", hint: "WAV, MP3, M4A · one speaker, up to 10 minutes", maxRec: 300 },
    transcribe: { accept: "audio/*,video/*,.wav,.mp3,.m4a,.ogg,.flac,.webm,.aac,.mp4,.mov,.mkv", hint: "Audio or video: MP3, WAV, M4A, MP4, MOV", maxRec: 600, keepOriginal: true },
  };

  // Returns a controller: { file, name, secs, reset(), el }
  SW.source = (el, kind, onChange) => {
    const cfg = KINDS[kind];
    const id = "src-" + kind;
    el.innerHTML = `
      <label class="drop" data-drop>
        <input type="file" accept="${cfg.accept}" hidden>
        <svg viewBox="0 0 24 24"><path d="M12 16V4m0 0-4 4m4-4 4 4"/><path d="M4 16v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/></svg>
        <strong>Drop a file or click to browse</strong><span>${esc(cfg.hint)}</span>
      </label>
      <div class="or">or record</div>
      ${kind === "clone" ? `<div class="read-box" style="margin-bottom:10px">Read this aloud, naturally:<p>The morning light spread slowly across the city. I made a cup of tea, opened my notebook and planned the day. Some days are loud and busy, others are calm, but every one of them begins with a single step.</p></div>` : ""}
      <div class="rec-row">
        <button class="rec" type="button" data-rec aria-controls="${id}-meter"><i></i><span>Record</span></button>
        <div class="meter" id="${id}-meter"><i></i></div>
        <span class="time num" data-rtime>0:00</span>
      </div>
      <div class="clip" data-clip hidden>
        <button class="play sm" type="button" data-cplay aria-label="Play">${SW.ICON.play}</button>
        <canvas height="36"></canvas>
        <span class="name" data-cname></span>
        <span class="time num" data-cdur style="color:var(--ink-3)"></span>
        <button class="icon-btn" type="button" data-cclear aria-label="Remove"><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></svg></button>
      </div>
      <ul class="quality" data-quality></ul>`;

    const ctl = { file: null, name: "", secs: 0, el };
    const drop = $("[data-drop]", el), input = $("input", drop), clip = $("[data-clip]", el), canvas = $("canvas", clip);
    const au = new Audio();
    let peaks = null, url = null;
    const cs = getComputedStyle(document.documentElement);
    const paintNow = () => SW.paintWave(canvas, peaks, au.duration ? au.currentTime / au.duration : 0, { played: cs.getPropertyValue("--ink").trim(), rest: cs.getPropertyValue("--rule-strong").trim() });

    ctl.reset = () => {
      au.pause();
      if (url) URL.revokeObjectURL(url);
      Object.assign(ctl, { file: null, name: "", secs: 0 });
      url = null; peaks = null;
      clip.hidden = true;
      $("[data-quality]", el).innerHTML = "";
      input.value = "";
      onChange?.(ctl);
    };

    async function accept(blob, name) {
      const buf = await blob.arrayBuffer();
      let decoded = null;
      try { decoded = await SW.decode(buf); } catch {
        if (!cfg.keepOriginal) { SW.toast("Couldn't read that file. Try WAV or MP3.", "error"); return; }
      }
      let file = blob, mono = null;
      if (decoded) {
        mono = await SW.toMono(decoded, cfg.keepOriginal ? 16000 : 24000);
        // Clone and Voice Changer get a clean WAV; transcription keeps the original (it may be video).
        if (!cfg.keepOriginal || !(blob instanceof File)) file = SW.encodeWav(mono, cfg.keepOriginal ? 16000 : 24000);
      }
      ctl.file = file instanceof File ? file : new File([file], (name || "recording").replace(/\.[^.]+$/, "") + (file.type === "audio/wav" ? ".wav" : ""), { type: file.type });
      ctl.name = name || "Recording";
      ctl.secs = decoded ? decoded.duration : 0;
      if (url) URL.revokeObjectURL(url);
      url = URL.createObjectURL(blob);
      au.src = url;
      peaks = mono ? SW.peaks(mono, 300) : null;
      clip.hidden = false;
      $("[data-cname]", el).textContent = ctl.name;
      $("[data-cdur]", el).textContent = decoded ? fmtTime(ctl.secs) : "";
      requestAnimationFrame(paintNow);
      if (cfg.check && mono) quality(mono, ctl.secs);
      onChange?.(ctl);
    }

    function quality(mono, secs) {
      let peak = 0, sum = 0;
      for (let i = 0; i < mono.length; i++) { const a = Math.abs(mono[i]); if (a > peak) peak = a; sum += mono[i] * mono[i]; }
      const rmsDb = 20 * Math.log10(Math.sqrt(sum / Math.max(1, mono.length)) + 1e-9);
      const q = [];
      if (secs < 5) q.push(["bad", `Only ${secs.toFixed(1)} s. You need at least 5 s; 10–30 s clones best.`]);
      else if (secs < 10) q.push(["warn", `${secs.toFixed(1)} s works, but 10–30 s gives a closer match.`]);
      else if (secs > 40) q.push(["warn", `${Math.round(secs)} s. Only the first 40 s of speech is used.`]);
      else q.push(["", `${Math.round(secs)} s, a good length.`]);
      if (peak > 0.995) q.push(["warn", "It's clipping (too loud). The distortion will be cloned too."]);
      else if (rmsDb < -38) q.push(["warn", "It's very quiet. Move closer to the microphone."]);
      else q.push(["", "Levels look healthy."]);
      q.push(["", "Clones copy everything: keep music, echo and background noise out."]);
      $("[data-quality]", el).innerHTML = q.map(([c, t]) => `<li class="${c}">${esc(t)}</li>`).join("");
    }

    // upload
    input.addEventListener("change", () => { const f = input.files[0]; if (f) accept(f, f.name); });
    ["dragenter", "dragover"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("over"); }));
    ["dragleave", "drop"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove("over"); }));
    drop.addEventListener("drop", (e) => { const f = e.dataTransfer.files[0]; if (f) accept(f, f.name); });

    // playback
    const pbtn = $("[data-cplay]", el);
    pbtn.addEventListener("click", () => { if (au.paused) { SW.stopPreview(); $("#audio").pause(); au.play(); } else au.pause(); });
    au.addEventListener("play", () => { pbtn.classList.add("playing"); const loop = () => { paintNow(); if (!au.paused) requestAnimationFrame(loop); }; loop(); });
    au.addEventListener("pause", () => pbtn.classList.remove("playing"));
    au.addEventListener("ended", () => { pbtn.classList.remove("playing"); au.currentTime = 0; paintNow(); });
    $("[data-cclear]", el).addEventListener("click", ctl.reset);
    canvas.addEventListener("click", (e) => { if (!au.duration) return; const r = canvas.getBoundingClientRect(); au.currentTime = ((e.clientX - r.left) / r.width) * au.duration; paintNow(); });

    // recording
    const rec = { media: null, stream: null, chunks: [], t0: 0, timer: 0, an: null, raf: 0 };
    const recBtn = $("[data-rec]", el), fill = $(".meter i", el);
    recBtn.addEventListener("click", () => (rec.media ? stop() : start()));
    async function start() {
      if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) { micHelp("Recording isn't available here."); return; }
      try {
        rec.stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: false, noiseSuppression: kind !== "clone", autoGainControl: true } });
      } catch { micHelp("Microphone access was blocked."); return; }
      ctl.reset();
      rec.chunks = [];
      rec.discard = false;
      rec.media = new MediaRecorder(rec.stream);
      rec.media.ondataavailable = (e) => e.data.size && rec.chunks.push(e.data);
      rec.media.onstop = () => { if (!rec.discard) accept(new Blob(rec.chunks, { type: rec.media?.mimeType || "audio/webm" }), "Recording"); };
      rec.media.start();
      rec.t0 = Date.now();
      recBtn.classList.add("on");
      $("span", recBtn).textContent = "Stop";
      rec.timer = setInterval(() => {
        const s = (Date.now() - rec.t0) / 1000;
        $("[data-rtime]", el).textContent = fmtTime(s);
        if (s >= cfg.maxRec) stop();
      }, 250);
      const ctx = SW.audioCtx();
      if (ctx.state === "suspended") ctx.resume();
      rec.an = ctx.createAnalyser();
      rec.an.fftSize = 1024;
      ctx.createMediaStreamSource(rec.stream).connect(rec.an);
      const data = new Float32Array(rec.an.fftSize);
      const meter = () => {
        if (!rec.an) return;
        rec.an.getFloatTimeDomainData(data);
        let m = 0; for (const x of data) m = Math.max(m, Math.abs(x));
        fill.style.width = `${Math.min(100, m * 140)}%`;
        fill.style.background = m > 0.95 ? "var(--danger)" : m < 0.05 ? "var(--warn)" : "var(--ok)";
        rec.raf = requestAnimationFrame(meter);
      };
      meter();
    }
    function stop(discard = false) {
      if (!rec.media) return;
      rec.discard = discard;
      clearInterval(rec.timer);
      cancelAnimationFrame(rec.raf);
      rec.an = null;
      try { rec.media.stop(); } catch { /* */ }
      rec.stream.getTracks().forEach((t) => t.stop());
      rec.media = null;
      recBtn.classList.remove("on");
      $("span", recBtn).textContent = "Record again";
      fill.style.width = "0";
    }
    function micHelp(reason) {
      if (window.pywebview?.api?.open_in_browser) {
        SW.dialog({ title: "Can't use the microphone in this window", body: `${reason} Upload a recording instead, or open Swara in your web browser, where recording works.`, confirm: "Open in browser" })
          .then((ok) => ok && window.pywebview.api.open_in_browser());
      } else SW.toast(`${reason} Allow microphone access for this page in your browser settings, or upload a file.`, "error");
    }
    ctl.stopRecording = () => stop(true);
    return ctl;
  };
})();
