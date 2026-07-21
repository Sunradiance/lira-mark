/**
 * Lira hologram — 12500pt point cloud with independent lip rig.
 * Points: [x, y, brightness, region, mouthWeight, jawDir] normalized 0..1.
 * Build v38 — full-face smile (cheeks, zygomatic, nasolabial, eye squint) + closed lips.
 * TTS still single-voice (v35 no-overlap).
 */
window.LiraNodeFace = function (opts) {
  const HOLOGRAM_BUILD = 'v38';
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
  /** Global gain — keep modest so lips don't slab the whole cheek. */
  const MOUTH_SCALE = 0.55;
  const LIP_OPEN_AMP = 15;
  /** Lateral + lift for corners — real smile is width/up, not gape. */
  const LIP_SMILE_AMP = 11;
  /** Whole midface smile amps (px at full smile). */
  const FACE_SMILE_LIFT = 12;
  const FACE_SMILE_OUT = 9;
  const FACE_SMILE_SQUINT = 5;
  const LIP_PUCKER_AMP = 8;
  const LIP_ROLL_AMP = 4.5;
  const LIP_WIDE_AMP = 6;
  // legacy aliases used by older status / tests
  const MOUTH_AMP = LIP_OPEN_AMP;
  const MOUTH_WIDE = LIP_WIDE_AMP;

  let particles = [];
  let pt = 0;
  /** Live lip drivers 0..1 (smoothed). */
  let lip = { open: 0, wide: 0, smile: 0, pucker: 0, roll: 0 };
  let lipT = { open: 0, wide: 0, smile: 0, pucker: 0, roll: 0 };
  // back-compat mirrors
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

  /** Phoneme → independent lip drivers (0..1). */
  function lipShape(ch) {
    const c = (ch || ' ').toLowerCase();
    // { open, wide, smile, pucker, roll }
    // smile is closed-curve, never paired with high open (that reads as creepy gape)
    if ('aáàâä'.includes(c)) return { open: 1.0, wide: 0.78, smile: 0.06, pucker: 0.05, roll: 0.05 };
    if ('eéèêë'.includes(c)) return { open: 0.38, wide: 0.55, smile: 0.55, pucker: 0.04, roll: 0.06 };
    if ('iíìîïy'.includes(c)) return { open: 0.12, wide: 0.42, smile: 0.82, pucker: 0.03, roll: 0.08 };
    if ('oóòôö'.includes(c)) return { open: 0.82, wide: 0.22, smile: 0.04, pucker: 0.78, roll: 0.12 };
    if ('uúùûüw'.includes(c)) return { open: 0.48, wide: 0.12, smile: 0.02, pucker: 0.92, roll: 0.15 };
    if ('bmp'.includes(c)) return { open: 0.04, wide: 0.28, smile: 0.08, pucker: 0.25, roll: 0.55 };
    if ('fv'.includes(c)) return { open: 0.22, wide: 0.45, smile: 0.08, pucker: 0.18, roll: 0.35 };
    if ('tdnlsz'.includes(c)) return { open: 0.28, wide: 0.4, smile: 0.12, pucker: 0.1, roll: 0.18 };
    if ('kgq'.includes(c)) return { open: 0.42, wide: 0.35, smile: 0.06, pucker: 0.18, roll: 0.1 };
    if (c === ' ' || c === '.' || c === ',' || c === '!' || c === '?') {
      return { open: 0.06, wide: 0.15, smile: 0.08, pucker: 0.04, roll: 0.04 };
    }
    return { open: 0.38, wide: 0.42, smile: 0.1, pucker: 0.1, roll: 0.1 };
  }
  function vowelShape(ch) {
    const s = lipShape(ch);
    return { open: s.open, wide: s.wide };
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

  function pumpLips(drivers, energy) {
    voiceDriveUntil = performance.now() + 180;
    const d = drivers || {};
    const gain = MOUTH_SCALE;
    const keys = ['open', 'wide', 'smile', 'pucker', 'roll'];
    for (let i = 0; i < keys.length; i++) {
      const k = keys[i];
      const v = Math.max(0, Math.min(1, d[k] != null ? d[k] : 0)) * gain;
      lipT[k] = Math.max(lipT[k], v);
      lip[k] = Math.max(lip[k], v * 0.9);
    }
    jawTarget = lipT.open;
    wideTarget = lipT.wide;
    mouthOpen = lip.open;
    mouthWide = lip.wide;
    speakEnergy = Math.max(speakEnergy, energy != null ? energy : 0.7);
  }
  function pumpMouth(open, wide, energy) {
    pumpLips({ open: open, wide: wide, smile: (wide || 0) * 0.35, pucker: 0, roll: 0 }, energy);
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
      const wob = 0.5 + Math.sin(t * 9) * 0.35;
      pumpLips({
        open: wob,
        wide: 0.3 + Math.sin(t * 7) * 0.18,
        smile: 0.12 + Math.sin(t * 5) * 0.08,
        pucker: 0.1 + Math.sin(t * 4.2) * 0.08,
        roll: 0.08,
      }, 0.88);
      return;
    }
    const chars = ts.graph_chars;
    const times = ts.graph_times;
    for (let i = 0; i < chars.length; i++) {
      const start = times[i][0];
      const end = times[i][1];
      if (t >= start && t < end) {
        pumpLips(lipShape(chars[i]), 0.92);
        return;
      }
    }
    pumpLips({ open: 0.2, wide: 0.18, smile: 0.06, pucker: 0.05, roll: 0.05 }, 0.55);
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
    pumpLips({ open: 0.7, wide: 0.45, smile: 0.2, pucker: 0.1, roll: 0.08 }, 0.92);
    if (source === 'lira' && voiceOn) {
      speakWithAraVoice(text);
      statusEl.textContent = 'me · ara · lips';
    } else if (isLiraSource(source)) {
      statusEl.textContent = 'me · here · lips';
    } else {
      statusEl.textContent = 'Tilen · ' + text.slice(0, 40) + (text.length > 40 ? '…' : '');
      pumpLips({ open: 0.55, wide: 0.35, smile: 0.15, pucker: 0.08, roll: 0.05 }, 0.75);
    }
  }

  function gauss2(nx, ny, cx, cy, sx, sy) {
    const dx = (nx - cx) / sx;
    const dy = (ny - cy) / sy;
    return Math.exp(-(dx * dx + dy * dy));
  }

  /**
   * Whole-face smile field — cheeks, zygomatic, nasolabial, lower lids.
   * Returns weights + preferred motion axes per point (normalized face space).
   */
  function classifyFaceSmile(nx, ny) {
    const side = nx < 0.5 ? -1 : 1;
    const ax = Math.abs(nx - 0.5); // 0 = midline
    // Skip deep interior mouth hole / pure center nose tip over-push
    let cheek = 0;
    let bone = 0;
    let naso = 0;
    let squint = 0;
    let temple = 0;
    let jaw = 0;

    // Apple of cheek (lifts + rounds outward)
    cheek = Math.max(
      gauss2(nx, ny, 0.32, 0.50, 0.11, 0.075),
      gauss2(nx, ny, 0.68, 0.50, 0.11, 0.075)
    );
    // Zygomatic arch / cheekbone (higher, more lateral)
    bone = Math.max(
      gauss2(nx, ny, 0.26, 0.43, 0.10, 0.06),
      gauss2(nx, ny, 0.74, 0.43, 0.10, 0.06),
      gauss2(nx, ny, 0.30, 0.46, 0.09, 0.05),
      gauss2(nx, ny, 0.70, 0.46, 0.09, 0.05)
    );
    // Nasolabial fold (nose wing → mouth corner) — pulls up and slightly out
    naso = Math.max(
      gauss2(nx, ny, 0.40, 0.52, 0.055, 0.07),
      gauss2(nx, ny, 0.60, 0.52, 0.055, 0.07),
      gauss2(nx, ny, 0.38, 0.55, 0.05, 0.055),
      gauss2(nx, ny, 0.62, 0.55, 0.05, 0.055)
    );
    // Lower eyelid / under-eye (Duchenne squint — lift + slight inward)
    squint = Math.max(
      gauss2(nx, ny, 0.36, 0.385, 0.09, 0.045),
      gauss2(nx, ny, 0.64, 0.385, 0.09, 0.045),
      gauss2(nx, ny, 0.34, 0.41, 0.07, 0.04),
      gauss2(nx, ny, 0.66, 0.41, 0.07, 0.04)
    );
    // Outer eye / temple crow's feet gather
    temple = Math.max(
      gauss2(nx, ny, 0.20, 0.38, 0.07, 0.05),
      gauss2(nx, ny, 0.80, 0.38, 0.07, 0.05)
    );
    // Upper jaw / near mouth corners (connects lips to cheek)
    jaw = Math.max(
      gauss2(nx, ny, 0.34, 0.58, 0.07, 0.05),
      gauss2(nx, ny, 0.66, 0.58, 0.07, 0.05)
    );

    // Kill midline (no cheek on nose bridge / philtrum)
    const midKill = Math.max(0, 1 - ax / 0.07);
    cheek *= (1 - 0.85 * midKill);
    bone *= (1 - 0.9 * midKill);
    naso *= (1 - 0.35 * midKill);

    // Forehead almost still; very soft brow settle on strong smile
    let brow = 0;
    if (ny > 0.28 && ny < 0.38 && ax > 0.08) {
      brow = gauss2(nx, ny, nx < 0.5 ? 0.35 : 0.65, 0.33, 0.1, 0.04) * 0.35;
    }

    const w = Math.min(1, cheek * 1.05 + bone * 1.1 + naso * 0.95 + squint * 0.85 + temple * 0.55 + jaw * 0.7 + brow);
    if (w < 0.04) {
      return { w: 0, lift: 0, out: 0, squint: 0, side: side };
    }

    // Preferred motion mix (relative, normalized later by w)
    const lift =
      cheek * 1.0 +
      bone * 1.15 +
      naso * 0.85 +
      squint * 0.7 +
      jaw * 0.45 +
      brow * 0.25 +
      temple * 0.2;
    const out =
      cheek * 0.95 +
      bone * 1.05 +
      naso * 0.55 +
      jaw * 0.5 +
      temple * 0.35 -
      squint * 0.25; // under-eye slightly gathers in
    const sq = squint * 1.0 + temple * 0.4;

    return {
      w: Math.min(1, w),
      lift: lift,
      out: out,
      squint: sq,
      side: side,
      cheek: cheek,
      bone: bone,
      naso: naso,
    };
  }

  /**
   * Classify each point into a lip role from geometry (no baked mesh):
   * upper | lower | cornerL | cornerR | soft (cheek/chin near mouth) | none
   */
  function classifyLip(nx, ny, bakedW, bakedJaw) {
    const dx = (nx - MOUTH.cx) / MOUTH_RX;
    const dy = (ny - MOUTH.cy) / MOUTH_RY;
    const r2 = dx * dx + dy * dy;
    let w = bakedW || 0;
    if (w < 0.01) {
      w = Math.max(0, Math.min(1, Math.exp(-r2 * 1.15)));
    }
    // Outside influence — skip
    if (w < 0.05 && r2 > 2.4) {
      return { role: 'none', w: 0, u: 0, side: 0, arch: 0, jawDir: 0 };
    }
    // Along-lip parameter: -1 left … +1 right
    const u = Math.max(-1, Math.min(1, dx));
    const side = u < 0 ? -1 : 1;
    // Lip arch: 0 at corners, 1 at center
    const arch = Math.max(0, 1 - Math.abs(u));
    // Corner band
    const cornerness = Math.max(0, Math.abs(u) - 0.55) / 0.45;
    let role = 'soft';
    let jawDir = bakedJaw != null ? bakedJaw : dy;
    jawDir = Math.max(-1, Math.min(1, jawDir));

    if (w > 0.12 || r2 < 1.35) {
      if (cornerness > 0.45 && r2 < 1.55) {
        role = u < 0 ? 'cornerL' : 'cornerR';
      } else if (dy < -0.06) {
        role = 'upper';
        jawDir = Math.min(jawDir, -0.25);
      } else if (dy > 0.06) {
        role = 'lower';
        jawDir = Math.max(jawDir, 0.25);
      } else {
        // vermillion seam — slight bias by baked jaw or y
        role = jawDir < 0 ? 'upper' : 'lower';
      }
    } else if (dy > 0.55 && r2 < 2.2) {
      role = 'soft'; // chin soft tissue
    } else if (r2 > 1.8) {
      role = 'none';
      w = 0;
    }

    // Pure lip weight: stronger on vermillion, weaker on soft
    let lipW = w;
    if (role === 'upper' || role === 'lower') {
      lipW = Math.min(1, w * (0.55 + 0.45 * Math.exp(-Math.abs(dy) * 1.8)));
    } else if (role === 'cornerL' || role === 'cornerR') {
      lipW = Math.min(1, w * (0.7 + 0.3 * cornerness));
    } else if (role === 'soft') {
      lipW = Math.min(0.35, w * 0.4);
    }

    return { role: role, w: lipW, u: u, side: side, arch: arch, jawDir: jawDir, corner: cornerness };
  }

  function buildParticles(points) {
    let upperN = 0;
    let lowerN = 0;
    let cornerN = 0;
    let lipN = 0;
    let faceN = 0;
    particles = points.map(function (row) {
      const x = row[0];
      const y = row[1];
      const b = row[2];
      const region = row[3] || 0;
      const bakedW = row[4] || 0;
      const bakedJaw = row[5] != null ? row[5] : null;
      const lipInfo = classifyLip(x, y, bakedW, bakedJaw);
      const face = classifyFaceSmile(x, y);
      const v = 0.3 + 0.7 * b;
      if (lipInfo.role === 'upper') upperN++;
      else if (lipInfo.role === 'lower') lowerN++;
      else if (lipInfo.role === 'cornerL' || lipInfo.role === 'cornerR') cornerN++;
      if (lipInfo.w > 0.12) lipN++;
      if (face.w > 0.12) faceN++;
      // Pre-normalize face motion axes so amps stay stable
      const inv = face.w > 0.001 ? 1 / Math.max(face.w, 0.25) : 0;
      return {
        x: x * IW, y: y * IH, nx: x, ny: y, b: b, region: region,
        mouthWeight: lipInfo.w,
        jawDir: lipInfo.jawDir,
        relX: (x - MOUTH.cx) / MOUTH_RX,
        relY: (y - MOUTH.cy) / MOUTH_RY,
        lipRole: lipInfo.role,
        lipU: lipInfo.u,
        lipSide: lipInfo.side,
        lipArch: lipInfo.arch,
        lipCorner: lipInfo.corner || 0,
        faceW: face.w,
        faceLift: face.lift * inv,
        faceOut: face.out * inv,
        faceSquint: face.squint * inv,
        faceSide: face.side,
        r: (region ? v * 0.55 : v * 0.28) * 0.6 * 255,
        g: (region ? v * 0.90 : v * 0.80) * 0.6 * 255,
        bl: v * 0.6 * 255,
        phase: Math.random() * Math.PI * 2,
        drift: 0.3 + Math.random() * 0.7,
        speed: 0.5 + Math.random(),
      };
    });
    pointsReady = true;
    statusEl.textContent =
      HOLOGRAM_BUILD + ' · lips↑' + upperN + ' ↓' + lowerN + ' ∠' + cornerN +
      ' · face☺' + faceN + ' · space=test';
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
    const talk = talking ? Math.max(0.45, speakEnergy) : 0;
    const smile = lip.smile;
    const pucker = lip.pucker;
    const roll = lip.roll;
    const wide = lip.wide;
    // Smile dominance 0..1 — real smile *closes* the gape, doesn't open it
    const smileAmt = Math.min(1, smile / Math.max(0.08, MOUTH_SCALE * 0.85));
    const smileClose = smileAmt * smileAmt; // ease-in so light smile still can talk
    // Micro idle only when not smiling hard (avoids smile+gape)
    const micro = talking && smileAmt < 0.45
      ? (0.06 + 0.08 * Math.abs(Math.sin(sayPhase * 5.5)))
      : 0;
    let open = Math.max(lip.open, micro * MOUTH_SCALE);
    // Zygomatic smile antagonizes jaw open — creepy gape dies here
    open *= (1 - 0.92 * smileClose);
    // Pure smile: tiny residual open only at very center if talking, else sealed
    if (smileAmt > 0.55) open = Math.min(open, 0.04 * MOUTH_SCALE * (1 - smileAmt));
    const activeLips = talking && (open > 0.006 || smile > 0.008 || pucker > 0.008 || roll > 0.008 || wide > 0.008);

    for (let i = 0; i < buf.length; i += 4) {
      buf[i] = 2; buf[i + 1] = 5; buf[i + 2] = 13; buf[i + 3] = 255;
    }

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      let px = p.x + Math.sin(pt * p.speed + p.phase) * p.drift;
      let py = p.y + Math.cos(pt * p.speed * 0.8 + p.phase) * p.drift;

      const mw = p.mouthWeight;
      if (activeLips && mw > 0.04 && p.lipRole !== 'none') {
        const role = p.lipRole;
        const arch = p.lipArch;       // 1 center, 0 corners
        const side = p.lipSide;       // -1 left, +1 right
        const u = p.lipU;
        const w = mw * (0.75 + 0.25 * talk);
        // outer thirds of the lip (where smile lives)
        const outer = Math.max(0, 1 - arch * 1.15);
        // corner falloff along lip (smooth)
        const cornerW = Math.pow(Math.min(1, Math.abs(u)), 1.35);

        // --- OPEN: speech gape only (suppressed while smiling) ---
        if (role === 'upper') {
          py -= open * LIP_OPEN_AMP * w * (0.45 + 0.55 * arch);
          py += roll * LIP_ROLL_AMP * w * (0.35 + 0.4 * arch) * (1 - 0.7 * smileClose);
        } else if (role === 'lower') {
          py += open * LIP_OPEN_AMP * w * (0.55 + 0.5 * arch);
          py -= roll * LIP_ROLL_AMP * w * (0.3 + 0.35 * arch) * (1 - 0.7 * smileClose);
        } else if (role === 'cornerL' || role === 'cornerR') {
          // open barely moves corners — smile owns them
          py += open * LIP_OPEN_AMP * w * 0.06;
        } else if (role === 'soft') {
          py += open * LIP_OPEN_AMP * w * 0.28 * (1 - smileClose);
        }

        // --- WIDE: mild lateral for speech; smile has its own stretch ---
        if (role === 'upper' || role === 'lower') {
          px += wide * LIP_WIDE_AMP * u * w * (0.35 + 0.25 * open) * (1 - 0.5 * smileClose);
        }

        // --- SMILE: closed human smile (zygomatic) ---
        // Corners go OUT + UP. Center stays sealed (lower rises to meet upper).
        // No center gape. Curve is a gentle U, not a scream.
        if (smile > 0.01) {
          const s = smile * w;
          if (role === 'cornerL' || role === 'cornerR') {
            // Main smile vector — lateral dominant, lift secondary
            px += s * LIP_SMILE_AMP * side * 1.15;
            py -= s * LIP_SMILE_AMP * 0.72;
            // slight tuck so corners don't balloon into open void
            py += s * LIP_SMILE_AMP * 0.08;
          } else if (role === 'upper') {
            // Outer upper follows corners up; CENTER stays put or tiny press down (seal)
            py -= s * LIP_SMILE_AMP * 0.38 * outer;
            py += s * LIP_SMILE_AMP * 0.12 * arch; // center presses toward lower
            px += s * LIP_SMILE_AMP * 0.55 * u * (0.35 + 0.65 * outer);
          } else if (role === 'lower') {
            // Lower rises into upper at center (closed smile); outer follows corners up
            py -= s * LIP_SMILE_AMP * (0.42 * arch + 0.38 * outer);
            px += s * LIP_SMILE_AMP * 0.5 * u * (0.3 + 0.7 * cornerW);
          } else if (role === 'soft') {
            // Cheek soft tissue lifts with smile — sells it as face not just mouth
            py -= s * LIP_SMILE_AMP * 0.22 * cornerW;
            px += s * LIP_SMILE_AMP * 0.18 * side * cornerW;
          }
        }

        // --- PUCKER: corners in, lips toward center (O/U) ---
        if (role === 'cornerL' || role === 'cornerR') {
          px -= pucker * LIP_PUCKER_AMP * side * w;
          py += pucker * LIP_PUCKER_AMP * 0.12 * w;
        } else if (role === 'upper' || role === 'lower') {
          px -= pucker * LIP_PUCKER_AMP * u * w * 0.65;
          py += (role === 'upper' ? 1 : -1) * pucker * LIP_PUCKER_AMP * 0.2 * w * arch;
        }

        // Flutter only for speech open — not during closed smile
        if (talk > 0.2 && smileAmt < 0.4 && (role === 'upper' || role === 'lower')) {
          const flutter = Math.sin(sayPhase * 4.1 + p.phase) * talk * w * (1 - smileClose);
          py += flutter * (role === 'upper' ? -0.45 : 0.5);
          px += Math.sin(sayPhase * 3.2 + p.phase * 1.3) * talk * 0.35 * u * w * (1 - smileClose);
        }
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
    const keys = ['open', 'wide', 'smile', 'pucker', 'roll'];
    if (sayTimer > 0 || ttsActive) {
      if (sayTimer > 0) sayTimer -= dt;
      sayPhase += dt * 18;
      // When TTS timestamps are live, driveTimestampMouth owns targets.
      // Otherwise phoneme from spoken text.
      if (!ttsActive || !ttsTimestamps) {
        const shape = lipShape(saying[Math.floor(sayPhase) % Math.max(1, saying.length)] || ' ');
        const smileHeavy = shape.smile > 0.45;
        const micro = smileHeavy ? 0 : (0.08 + 0.12 * Math.abs(Math.sin(sayPhase * 6.2)));
        let o = Math.max(shape.open, micro);
        // Don't stack open on smile shapes
        if (smileHeavy) o = Math.min(o, 0.14);
        lipT.open = o * MOUTH_SCALE;
        lipT.wide = (smileHeavy ? shape.wide * 0.5 : Math.max(shape.wide, micro * 0.45)) * MOUTH_SCALE;
        lipT.smile = shape.smile * MOUTH_SCALE;
        lipT.pucker = shape.pucker * MOUTH_SCALE;
        lipT.roll = shape.roll * MOUTH_SCALE;
      }
      speakEnergy = Math.max(speakEnergy * 0.92, 0.55 + Math.sin(sayPhase * 3.2) * 0.28);
    } else if (mouthTest <= 0) {
      speakEnergy *= 0.9;
      for (let i = 0; i < keys.length; i++) lipT[keys[i]] *= 0.82;
    }
    if (mouthTest > 0) {
      mouthTest = Math.max(0, mouthTest - dt);
      // Cycle open → closed smile → pucker
      const phase = (3 - mouthTest) / 3;
      if (phase < 0.33) {
        lipT.open = MOUTH_SCALE;
        lipT.wide = 0.35 * MOUTH_SCALE;
        lipT.smile = 0.05 * MOUTH_SCALE;
        lipT.pucker = 0.04 * MOUTH_SCALE;
        lipT.roll = 0.08 * MOUTH_SCALE;
      } else if (phase < 0.66) {
        // Closed human smile — almost no open
        lipT.open = 0.02 * MOUTH_SCALE;
        lipT.wide = 0.2 * MOUTH_SCALE;
        lipT.smile = 0.95 * MOUTH_SCALE;
        lipT.pucker = 0.02 * MOUTH_SCALE;
        lipT.roll = 0.12 * MOUTH_SCALE;
      } else {
        lipT.open = 0.55 * MOUTH_SCALE;
        lipT.wide = 0.15 * MOUTH_SCALE;
        lipT.smile = 0.03 * MOUTH_SCALE;
        lipT.pucker = 0.9 * MOUTH_SCALE;
        lipT.roll = 0.2 * MOUTH_SCALE;
      }
      speakEnergy = Math.max(speakEnergy, 0.85);
    }
    const snap = Math.min(1, dt * 26);
    for (let i = 0; i < keys.length; i++) {
      const k = keys[i];
      lip[k] += (lipT[k] - lip[k]) * snap;
      if (lip[k] < 0.002 && lipT[k] < 0.002) lip[k] = 0;
    }
    mouthOpen = lip.open;
    mouthWide = lip.wide;
    jawTarget = lipT.open;
    wideTarget = lipT.wide;
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
    if (amp > 0.05) {
      lipT.open = Math.max(lipT.open, amp * 0.65 * MOUTH_SCALE);
      lipT.wide = Math.max(lipT.wide, amp * 0.3 * MOUTH_SCALE);
      lipT.smile = Math.max(lipT.smile, amp * 0.12 * MOUTH_SCALE);
    }
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
      speakEnergy = 0.9;
      statusEl.textContent = 'lip test · open→smile→pucker';
    }
  });

  micBtn.addEventListener('click', function () {
    if (micOn) { stopMic(); recognition && recognition.stop(); }
    else startMic().then(function () { recognition && recognition.start(); }).catch(function () {});
  });

  function setMouth(open, wide, extra) {
    const o = Math.max(0, Math.min(1, open || 0));
    const w = Math.max(0, Math.min(1, wide != null ? wide : o * 0.55));
    const ex = extra || {};
    pumpLips({
      open: o,
      wide: w,
      smile: ex.smile != null ? ex.smile : w * 0.4,
      pucker: ex.pucker != null ? ex.pucker : 0,
      roll: ex.roll != null ? ex.roll : 0,
    }, Math.max(0.5, o * 0.85));
    sayTimer = Math.max(sayTimer, 0.25);
  }

  function driveAudioLevel(amp) {
    const a = Math.max(0, Math.min(1, amp || 0));
    if (a < 0.02) return;
    setMouth(0.25 + a * 0.75, 0.15 + a * 0.45, { smile: a * 0.2, pucker: a * 0.1 });
  }

  window.__liraHologramSpeak = speakLine;
  window.__liraHologramMouth = setMouth;
  window.liraHologram = {
    setMouth: setMouth,
    setLips: function (drivers) { pumpLips(drivers || {}, 0.8); sayTimer = Math.max(sayTimer, 0.3); },
    driveAudioLevel: driveAudioLevel,
    speak: speakLine,
    MOUTH: MOUTH,
    get mouthOpen() { return mouthOpen; },
    get mouthWide() { return mouthWide; },
    get lips() { return { open: lip.open, wide: lip.wide, smile: lip.smile, pucker: lip.pucker, roll: lip.roll }; },
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