/**
 * Lira hologram — 12500pt point cloud with per-point speech deformation.
 * Points: [x, y, brightness, region, mouthWeight, jawDir] normalized 0..1.
 * Build v35 — Gaussian lips, MOUTH_SCALE 0.2; single-voice TTS (no overlap).
 */
window.LiraNodeFace = function (opts) {
  const HOLOGRAM_BUILD = 'v35';
  const getActive = (opts && opts.isActive) || function () { return true; };
  const assetUrl = (opts && opts.assetUrl) || function (n) { return n; };

  const canvas = document.getElementById('hologramC');
  const ctx = canvas.getContext('2d');
  const statusEl = document.getElementById('status');
  const voiceBar = document.getElementById('voiceBar');
  const sayInput = document.getElementById('say');
  const micBtn = document.getElementById('micBtn');

  const IW = 475;
  const IH = 587;
  const IMG_AR = IW / IH;
  const MOUTH = { x0: 0.40, x1: 0.64, y0: 0.515, y1: 0.605, cx: 0.52, cy: 0.558 };
  const MOUTH_RX = 0.14;
  const MOUTH_RY = 0.065;
  const MOUTH_SCALE = 0.2;
  const MOUTH_AMP = 18;
  const MOUTH_WIDE = 7;

  let particles = [];
  let pt = 0;
  let mouthOpen = 0;
  let mouthWide = 0;
  let jawTarget = 0;
  let wideTarget = 0;
  let speakEnergy = 0;
  let saying = '';
  let sayPhase = 0;
  let sayTimer = 0;
  let micOn = false;
  let audioCtx = null;
  let analyser = null;
  let micStream = null;
  let recognition = null;
  let running = false;
  let pointsReady = false;
  let nLast = performance.now();
  let nRaf = 0;
  let speakPollCursor = 0;
  let speakPollTimer = 0;
  let speakBootstrapped = false;
  let speakEventSource = null;
  let speakSseOk = false;
  const seenSpeakKeys = new Set();
  let typingUntil = 0;
  let mouthTest = 0;
  let ttsActive = false;
  let voiceOn = true;
  let voiceDriveUntil = 0;
  let ttsAudio = null;
  let ttsTimestamps = null;
  let ttsRaf = 0;
  const VOICE_ID = 'ara';
  const VOICE_MAX_CHARS = 320;
  let ttsBusy = false;
  /** Only the latest speak is allowed to play — kills overlap from concurrent /api/tts. */
  let ttsToken = 0;
  let ttsAbort = null;
  let W = 0;
  let H = 0;
  let scale = 0;
  let ox = 0;
  let oy = 0;
  const dpr = Math.min(2, devicePixelRatio || 1);
  const off = document.createElement('canvas');
  off.width = IW;
  off.height = IH;
  const octx = off.getContext('2d');
  const imgData = octx.createImageData(IW, IH);
  const buf = imgData.data;

  function vowelShape(ch) {
    const c = ch.toLowerCase();
    if ('aáàâ'.includes(c)) return { open: 1.0, wide: 0.72 };
    if ('eéèê'.includes(c)) return { open: 0.62, wide: 0.55 };
    if ('iíìî'.includes(c)) return { open: 0.38, wide: 0.52 };
    if ('oóòô'.includes(c)) return { open: 0.95, wide: 0.58 };
    if ('uúùû'.includes(c)) return { open: 0.65, wide: 0.42 };
    if ('bmp'.includes(c)) return { open: 0.18, wide: 0.48 };
    if ('fv'.includes(c)) return { open: 0.32, wide: 0.78 };
    return { open: 0.48, wide: 0.62 };
  }

  if (sayInput) {
    sayInput.addEventListener('focus', function () { typingUntil = Date.now() + 120000; });
    sayInput.addEventListener('keydown', function () { typingUntil = Date.now() + 8000; });
  }

  function isLiraSource(s) { return s === 'lira' || s === 'lira-chat'; }

  function voiceText(text) {
    const t = (text || '').trim();
    if (t.length <= VOICE_MAX_CHARS) return t;
    const cut = t.slice(0, VOICE_MAX_CHARS);
    return (cut.lastIndexOf(' ') > 40 ? cut.slice(0, cut.lastIndexOf(' ')) : cut) + '…';
  }

  function pumpMouth(open, wide, energy) {
    voiceDriveUntil = performance.now() + 180;
    open *= MOUTH_SCALE;
    wide *= MOUTH_SCALE;
    jawTarget = Math.max(jawTarget, open);
    wideTarget = Math.max(wideTarget, wide);
    mouthOpen = Math.max(mouthOpen, open * 0.92);
    mouthWide = Math.max(mouthWide, wide * 0.88);
    speakEnergy = Math.max(speakEnergy, energy);
  }

  function killBrowserTts() {
    try {
      if (window.speechSynthesis) window.speechSynthesis.cancel();
    } catch (e) { /* ignore */ }
  }

  function blockBrowserTts() {
    if (!window.speechSynthesis || window.speechSynthesis.__liraBlocked) return;
    var syn = window.speechSynthesis;
    var origSpeak = syn.speak.bind(syn);
    syn.speak = function () {
      if (running && voiceOn) return;
      return origSpeak.apply(syn, arguments);
    };
    syn.__liraBlocked = true;
  }

  function stopTtsPlayback() {
    killBrowserTts();
    if (ttsAbort) {
      try { ttsAbort.abort(); } catch (e) { /* ignore */ }
      ttsAbort = null;
    }
    if (ttsAudio) {
      try {
        ttsAudio.onplay = null;
        ttsAudio.onended = null;
        ttsAudio.onerror = null;
        ttsAudio.pause();
      } catch (e) { /* ignore */ }
      try { ttsAudio.src = ''; } catch (e2) { /* ignore */ }
      ttsAudio = null;
    }
    ttsTimestamps = null;
    cancelAnimationFrame(ttsRaf);
    ttsRaf = 0;
    ttsActive = false;
    ttsBusy = false;
  }

  function driveTimestampMouth(t) {
    const ts = ttsTimestamps;
    if (!ts || !ts.graph_chars || !ts.graph_times) {
      pumpMouth(0.5 + Math.sin(t * 9) * 0.38, 0.32 + Math.sin(t * 7) * 0.22, 0.88);
      return;
    }
    const chars = ts.graph_chars;
    const times = ts.graph_times;
    for (let i = 0; i < chars.length; i++) {
      const start = times[i][0];
      const end = times[i][1];
      if (t >= start && t < end) {
        const shape = vowelShape(chars[i]);
        pumpMouth(shape.open, shape.wide, 0.92);
        return;
      }
    }
    pumpMouth(0.28, 0.22, 0.55);
  }

  function tickTtsMouth() {
    if (!ttsActive || !ttsAudio) return;
    driveTimestampMouth(ttsAudio.currentTime || 0);
    ttsRaf = requestAnimationFrame(tickTtsMouth);
  }

  function mouthOnlyFallback(text, reason) {
    saying = text;
    sayTimer = Math.max(sayTimer, Math.min(12, text.length * 0.06));
    pumpMouth(0.7, 0.45, 0.8);
    if (statusEl) statusEl.textContent = 'ara · mouth only' + (reason ? ' (' + reason + ')' : '');
  }

  function speakRowKey(row) {
    return (row.t || '') + '|' + (row.from || 'lira') + '|' + (row.text || '').replace(/\s+/g, ' ').trim();
  }

  async function speakWithAraVoice(text) {
    if (!voiceOn) return;
    const line = voiceText(text);
    if (!line) return;
    // Invalidate every in-flight TTS fetch + currently playing clip (latest-wins).
    const myToken = ++ttsToken;
    killBrowserTts();
    if (ttsAbort) {
      try { ttsAbort.abort(); } catch (e) { /* ignore */ }
    }
    ttsAbort = typeof AbortController !== 'undefined' ? new AbortController() : null;
    if (ttsAudio) {
      try {
        ttsAudio.onplay = null;
        ttsAudio.onended = null;
        ttsAudio.onerror = null;
        ttsAudio.pause();
      } catch (e) { /* ignore */ }
      try { ttsAudio.src = ''; } catch (e2) { /* ignore */ }
      ttsAudio = null;
    }
    ttsTimestamps = null;
    cancelAnimationFrame(ttsRaf);
    ttsRaf = 0;
    ttsActive = false;
    ttsBusy = true;
    try {
      const fetchOpts = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: line, voice_id: VOICE_ID, with_timestamps: true }),
      };
      if (ttsAbort) fetchOpts.signal = ttsAbort.signal;
      const res = await fetch('/api/tts', fetchOpts);
      if (myToken !== ttsToken) return; // superseded while waiting
      if (!res.ok) throw new Error('tts ' + res.status);
      const data = await res.json();
      if (myToken !== ttsToken) return;
      if (!data.ok || !data.audio) throw new Error('no audio');
      ttsTimestamps = data.audio_timestamps || null;
      const dur = data.duration || Math.max(2, line.length * 0.07);
      // Hard-stop anything that slipped through before attaching the new clip
      if (ttsAudio) {
        try { ttsAudio.pause(); } catch (e) { /* ignore */ }
        ttsAudio = null;
      }
      const audio = new Audio('data:audio/mpeg;base64,' + data.audio);
      ttsAudio = audio;
      audio.onplay = function () {
        if (myToken !== ttsToken) {
          try { audio.pause(); } catch (e) { /* ignore */ }
          return;
        }
        ttsActive = true;
        saying = line;
        sayPhase = 0;
        sayTimer = Math.max(sayTimer, dur + 0.35);
        pumpMouth(0.85, 0.55, 0.95);
        if (statusEl) statusEl.textContent = 'me · ara';
        cancelAnimationFrame(ttsRaf);
        ttsRaf = requestAnimationFrame(tickTtsMouth);
      };
      audio.onended = function () {
        if (myToken !== ttsToken) return;
        stopTtsPlayback();
      };
      audio.onerror = function () {
        if (myToken !== ttsToken) return;
        stopTtsPlayback();
        mouthOnlyFallback(line, 'audio error');
      };
      await audio.play();
      if (myToken !== ttsToken) {
        try { audio.pause(); audio.src = ''; } catch (e) { /* ignore */ }
        if (ttsAudio === audio) ttsAudio = null;
      }
    } catch (e) {
      if (e && (e.name === 'AbortError' || myToken !== ttsToken)) return;
      if (myToken !== ttsToken) return;
      ttsBusy = false;
      if (statusEl) statusEl.textContent = 'ara failed · ' + (e.message || 'xai');
      mouthOnlyFallback(line, 'xai');
    }
  }

  function speakLine(line, source) {
    const text = (line || '').trim();
    if (!text) return;
    if (!isLiraSource(source) && source !== 'you' && sayInput && document.activeElement === sayInput && Date.now() < typingUntil) return;
    if (isLiraSource(source)) {
      var el = document.getElementById('liraReply');
      var short = text.length > 140 ? text.slice(0, 137) + '…' : text;
      if (el) el.textContent = short;
      if (sayInput) { sayInput.blur(); typingUntil = 0; }
    }
    if (source === 'you') {
      var el2 = document.getElementById('liraReply');
      if (el2) el2.textContent = '';
    }
    if (sayInput) {
      sayInput.value = isLiraSource(source) ? '' : text;
      sayInput.classList.add('live');
      setTimeout(function () { sayInput.classList.remove('live'); }, 1200);
    }
    saying = text;
    sayPhase = 0;
    sayTimer = Math.max(2.4, text.length * 0.072);
    jawTarget = 0.88 * MOUTH_SCALE;
    wideTarget = 0.62 * MOUTH_SCALE;
    mouthOpen = 0.72 * MOUTH_SCALE;
    mouthWide = 0.5 * MOUTH_SCALE;
    speakEnergy = 0.92;
    if (source === 'lira' && voiceOn) {
      speakWithAraVoice(text);
      statusEl.textContent = 'me · ara';
    } else if (isLiraSource(source)) {
      statusEl.textContent = 'me · here';
    } else {
      statusEl.textContent = 'Tilen · ' + text.slice(0, 40) + (text.length > 40 ? '…' : '');
      pumpMouth(0.65, 0.4, 0.75);
    }
  }

  function buildParticles(points) {
    let mouthN = 0;
    particles = points.map(function (row) {
      const x = row[0];
      const y = row[1];
      const b = row[2];
      const region = row[3] || 0;
      let mouthWeight = row[4] || 0;
      const jawDir = row[5] != null ? row[5] : (y - MOUTH.cy) / MOUTH_RY;
      if (mouthWeight < 0.01) {
        const dx = (x - MOUTH.cx) / MOUTH_RX;
        const dy = (y - MOUTH.cy) / MOUTH_RY;
        mouthWeight = Math.max(0, Math.min(1, Math.exp(-(dx * dx + dy * dy) * 1.15)));
      }
      const v = 0.3 + 0.7 * b;
      if (mouthWeight > 0.12) mouthN++;
      return {
        x: x * IW, y: y * IH, b: b, region: region,
        mouthWeight: mouthWeight,
        jawDir: Math.max(-1, Math.min(1, jawDir)),
        relX: (x - MOUTH.cx) / MOUTH_RX,
        relY: (y - MOUTH.cy) / MOUTH_RY,
        r: (region ? v * 0.55 : v * 0.28) * 0.6 * 255,
        g: (region ? v * 0.90 : v * 0.80) * 0.6 * 255,
        bl: v * 0.6 * 255,
        phase: Math.random() * Math.PI * 2,
        drift: 0.3 + Math.random() * 0.7,
        speed: 0.5 + Math.random(),
      };
    });
    pointsReady = true;
    statusEl.textContent = HOLOGRAM_BUILD + ' · lips ' + mouthN + 'pt · gaussian · space=test';
  }

  async function loadPoints() {
    try {
      const res = await fetch(assetUrl('lira-points-12500.json') + '?t=' + Date.now());
      if (!res.ok) throw new Error('points missing');
      buildParticles(await res.json());
    } catch (e) {
      statusEl.textContent = 'points load failed';
    }
  }

  function layout() {
    W = canvas.width = innerWidth * dpr;
    H = canvas.height = innerHeight * dpr;
    scale = Math.min(W / IW, H / IH);
    ox = (W - IW * scale) * 0.5;
    oy = (H - IH * scale) * 0.5;
    ctx.imageSmoothingEnabled = false;
  }

  function draw() {
    if (!pointsReady) {
      ctx.fillStyle = '#02040c';
      ctx.fillRect(0, 0, W, H);
      return;
    }

    const flicker = 0.94 + 0.06 * Math.sin(pt * 13.7) * Math.sin(pt * 7.3);
    const talking = sayTimer > 0 || micOn || mouthTest > 0 || ttsActive || performance.now() < voiceDriveUntil;
    const talk = talking ? Math.max(0.55, speakEnergy) : 0;
    const flap = talking ? (0.42 + 0.58 * Math.abs(Math.sin(sayPhase * 6.2))) * MOUTH_SCALE : 0;

    for (let i = 0; i < buf.length; i += 4) {
      buf[i] = 2; buf[i + 1] = 5; buf[i + 2] = 13; buf[i + 3] = 255;
    }

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      let px = p.x + Math.sin(pt * p.speed + p.phase) * p.drift;
      let py = p.y + Math.cos(pt * p.speed * 0.8 + p.phase) * p.drift;

      const mw = p.mouthWeight;
      if (mw > 0.04 && talking && (mouthOpen > 0.01 || flap > 0.1)) {
        const open = Math.max(mouthOpen, flap) * (1 + talk * 0.35 * MOUTH_SCALE) * mw;
        const jd = p.jawDir;
        const lipSplit = jd > 0.05 ? jd : jd * 0.35;
        py += open * MOUTH_AMP * lipSplit;
        px += mouthWide * p.relX * MOUTH_WIDE * open * 0.85;
        const corner = Math.max(0, 1 - Math.abs(p.relX)) * mw;
        px += Math.sin(sayPhase * 4.2 + p.phase) * talk * 3 * corner;
        py += Math.sin(sayPhase * 3.4 + p.phase) * talk * 1.2 * mw;
      }

      const tw = flicker * (0.8 + 0.2 * Math.sin(pt * 2 + p.phase));
      const xi = px | 0;
      const yi = py | 0;
      for (let dy = 0; dy < 2; dy++) {
        const yy = yi + dy;
        if (yy < 0 || yy >= IH) continue;
        for (let dx = 0; dx < 2; dx++) {
          const xx = xi + dx;
          if (xx < 0 || xx >= IW) continue;
          const bi = (yy * IW + xx) * 4;
          buf[bi] = Math.min(255, buf[bi] + p.r * tw);
          buf[bi + 1] = Math.min(255, buf[bi + 1] + p.g * tw);
          buf[bi + 2] = Math.min(255, buf[bi + 2] + p.bl * tw);
        }
      }
    }

    octx.putImageData(imgData, 0, 0);
    ctx.fillStyle = '#02040c';
    ctx.fillRect(0, 0, W, H);
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(off, ox, oy, IW * scale, IH * scale);

    ctx.fillStyle = 'rgba(0,0,0,0.12)';
    const step = 4 * dpr;
    for (let y = (pt * 30 * dpr) % step; y < H; y += step) {
      ctx.fillRect(0, y, W, dpr);
    }
  }

  function driveSpeech(dt) {
    let targetOpen = 0;
    let targetWide = 0;
    if (sayTimer > 0 || ttsActive) {
      if (sayTimer > 0) sayTimer -= dt;
      sayPhase += dt * 18;
      const shape = vowelShape(saying[Math.floor(sayPhase) % Math.max(1, saying.length)] || ' ');
      const flap = (0.4 + 0.6 * Math.abs(Math.sin(sayPhase * 6.2))) * MOUTH_SCALE;
      targetOpen = Math.max(shape.open * MOUTH_SCALE, flap);
      targetWide = Math.max(shape.wide * MOUTH_SCALE, flap * 0.72);
      speakEnergy = 0.62 + Math.sin(sayPhase * 3.2) * 0.38;
    } else {
      speakEnergy *= 0.9;
      targetOpen = 0;
      targetWide = 0;
    }
    const snap = Math.min(1, dt * 28);
    jawTarget += (targetOpen - jawTarget) * snap;
    wideTarget += (targetWide - wideTarget) * snap;
    mouthOpen += (jawTarget - mouthOpen) * Math.min(1, snap * 1.2);
    mouthWide += (wideTarget - mouthWide) * Math.min(1, snap);
    if (mouthTest > 0) {
      mouthTest = Math.max(0, mouthTest - dt);
      jawTarget = Math.max(jawTarget, MOUTH_SCALE);
      wideTarget = Math.max(wideTarget, 0.55 * MOUTH_SCALE);
    }
    if (voiceBar) voiceBar.style.width = (speakEnergy * 100) + '%';
  }

  function rememberSpeakRow(row) {
    const key = speakRowKey(row);
    if (!key || seenSpeakKeys.has(key)) return false;
    seenSpeakKeys.add(key);
    if (seenSpeakKeys.size > 240) {
      const drop = seenSpeakKeys.size - 180;
      let n = 0;
      for (const k of seenSpeakKeys) {
        seenSpeakKeys.delete(k);
        if (++n >= drop) break;
      }
    }
    return true;
  }

  function handleSpeakRow(row) {
    if (!row || !row.text) return;
    if (!rememberSpeakRow(row)) return;
    speakLine(row.text, row.from || 'lira');
  }

  function connectSpeakStream() {
    if (speakEventSource || location.protocol === 'file:') return;
    try {
      speakEventSource = new EventSource('/api/events');
      speakEventSource.addEventListener('open', function () {
        speakSseOk = true;
      });
      speakEventSource.addEventListener('speak', function (ev) {
        try {
          handleSpeakRow(JSON.parse(ev.data));
          speakPollCursor += 1;
        } catch (e) { /* skip */ }
      });
      speakEventSource.onerror = function () {
        speakSseOk = false;
        if (speakEventSource) { speakEventSource.close(); speakEventSource = null; }
        setTimeout(connectSpeakStream, 2000);
      };
    } catch (e) { /* poll */ }
  }

  async function pollChatSpeak() {
    if (speakEventSource && speakEventSource.readyState !== EventSource.CLOSED) return;
    if (speakSseOk && speakEventSource) return;
    speakPollTimer += 0.12;
    if (speakPollTimer < 0.35) return;
    speakPollTimer = 0;
    try {
      const res = await fetch(assetUrl('lira-speak.jsonl') + '?t=' + Date.now());
      if (!res.ok) return;
      const lines = (await res.text()).trim().split('\n').filter(Boolean);
      if (!speakBootstrapped) {
        speakPollCursor = lines.length;
        speakBootstrapped = true;
        return;
      }
      for (let i = speakPollCursor; i < lines.length; i++) {
        try { handleSpeakRow(JSON.parse(lines[i])); } catch (e) { /* skip */ }
      }
      speakPollCursor = lines.length;
    } catch (e) { /* offline */ }
  }

  async function startMic() {
    try {
      audioCtx = audioCtx || new AudioContext();
      micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const src = audioCtx.createMediaStreamSource(micStream);
      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 512;
      src.connect(analyser);
      micOn = true;
      micBtn.textContent = 'mic on';
      micBtn.classList.add('on');
    } catch (e) { micOn = false; }
  }

  function stopMic() {
    micOn = false;
    micBtn.textContent = 'mic off';
    micBtn.classList.remove('on');
    if (micStream) micStream.getTracks().forEach(function (tr) { tr.stop(); });
    micStream = null;
  }

  function pollMic() {
    if (!analyser) return;
    const buf = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(buf);
    let sum = 0;
    for (let i = 2; i < 48; i++) sum += buf[i];
    const amp = Math.min(1, (sum / 46) / 130);
    speakEnergy = Math.max(speakEnergy, amp);
    jawTarget = Math.max(jawTarget, amp * 0.5 * MOUTH_SCALE);
    wideTarget = Math.max(wideTarget, amp * 0.2 * MOUTH_SCALE);
  }

  function setupSpeechRec() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return;
    recognition = new SR();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.onresult = function (ev) {
      let line = '';
      for (let i = ev.resultIndex; i < ev.results.length; i++) line += ev.results[i][0].transcript;
      if (line.trim()) speakLine(line.trim(), 'mic');
    };
  }

  addEventListener('keydown', function (e) {
    if (e.code === 'Space' && !e.repeat && document.activeElement !== sayInput) {
      e.preventDefault();
      mouthTest = 3;
      jawTarget = MOUTH_SCALE;
      wideTarget = 0.6 * MOUTH_SCALE;
      speakEnergy = 0.9;
      statusEl.textContent = 'mouth test · space';
    }
  });

  micBtn.addEventListener('click', function () {
    if (micOn) { stopMic(); recognition && recognition.stop(); }
    else startMic().then(function () { recognition && recognition.start(); }).catch(function () {});
  });

  function setMouth(open, wide) {
    const o = Math.max(0, Math.min(1, open || 0));
    const w = Math.max(0, Math.min(1, wide != null ? wide : o * 0.55));
    pumpMouth(o, w, Math.max(0.5, o * 0.85));
    sayTimer = Math.max(sayTimer, 0.25);
  }

  function driveAudioLevel(amp) {
    const a = Math.max(0, Math.min(1, amp || 0));
    if (a < 0.02) return;
    setMouth(0.25 + a * 0.75, 0.15 + a * 0.45);
  }

  window.__liraHologramSpeak = speakLine;
  window.__liraHologramMouth = setMouth;
  window.liraHologram = {
    setMouth: setMouth,
    driveAudioLevel: driveAudioLevel,
    speak: speakLine,
    MOUTH: MOUTH,
    get mouthOpen() { return mouthOpen; },
    get mouthWide() { return mouthWide; },
    setVoice: function (on) { voiceOn = !!on; if (!on) stopTtsPlayback(); },
    voiceId: VOICE_ID,
  };

  if (sayInput) {
    sayInput.addEventListener('input', function () {
      typingUntil = Date.now() + 8000;
    });
  }

  function nodeFrame(now) {
    if (!running) return;
    const dt = Math.min(0.05, (now - nLast) / 1000);
    nLast = now;
    pt += dt;
    if (micOn) pollMic();
    pollChatSpeak();
    driveSpeech(dt);
    draw();
    nRaf = requestAnimationFrame(nodeFrame);
  }

  function teardown() {
    running = false;
    cancelAnimationFrame(nRaf);
    stopTtsPlayback();
    killBrowserTts();
    if (speakEventSource) {
      speakEventSource.close();
      speakEventSource = null;
    }
    speakSseOk = false;
    if (recognition) {
      try { recognition.stop(); } catch (e) { /* ignore */ }
    }
    stopMic();
  }

  window.__liraHologramTeardown = teardown;

  function boot() {
    killBrowserTts();
    blockBrowserTts();
    if (location.protocol === 'file:' || location.hostname.endsWith('github.io')) {
      voiceOn = false;
      statusEl.textContent = HOLOGRAM_BUILD + ' · voice needs face server host';
    } else {
      statusEl.textContent = HOLOGRAM_BUILD + ' · loading points…';
      fetch('/api/health').catch(function () {
        voiceOn = false;
        if (statusEl) statusEl.textContent = HOLOGRAM_BUILD + ' · server offline';
      });
    }
    setupSpeechRec();
    connectSpeakStream();
    layout();
    loadPoints();
    if (getActive()) {
      running = true;
      nLast = performance.now();
      nRaf = requestAnimationFrame(nodeFrame);
    }
  }

  boot();
  addEventListener('resize', function () { layout(); });

  return {
    resume: function () {
      layout();
      running = true;
      nLast = performance.now();
      cancelAnimationFrame(nRaf);
      nRaf = requestAnimationFrame(nodeFrame);
    },
    pause: function () {
      running = false;
      cancelAnimationFrame(nRaf);
      stopTtsPlayback();
    },
    setMouth: setMouth,
    driveAudioLevel: driveAudioLevel,
    particles: function () { return particles; },
  };
};