window.LiraParticleFace = function (opts) {
  const getActive = (opts && opts.isActive) || (function () { return true; });
  const assetUrl = (opts && opts.assetUrl) || (function (n) { return n; });

  const canvas = document.getElementById('particleC');
  const statusEl = document.getElementById('status');
  const voiceBar = document.getElementById('voiceBar');
  const sayInput = document.getElementById('say');
  const micBtn = document.getElementById('micBtn');
  const countSel = document.getElementById('countSel');
  const speakBtn = document.getElementById('speakBtn');

  const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(2, devicePixelRatio || 1));
  renderer.setClearColor(0x040608, 1);

  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x040608, 0.018);
  const camera = new THREE.PerspectiveCamera(42, innerWidth / innerHeight, 0.1, 100);
  camera.position.z = 3.15;

  const portrait = new Image();
  portrait.crossOrigin = 'anonymous';
  portrait.src = assetUrl('lira-face.jpg');

  let points = null, geom = null, basePos = null, regions = null;
  let colors = null, baseColors = null, particleCount = 0;
  let pt = 0, pBlink = 0, pBlinkT = 2.5 + Math.random() * 3;
  let mouthOpen = 0, speakEnergy = 0, jawTarget = 0, browLift = 0;
  let saying = '', sayPhase = 0, sayTimer = 0;
  let micOn = false, audioCtx = null, analyser = null, micStream = null, recognition = null;
  let running = false, portraitReady = false, pLast = performance.now(), pRaf = 0;
  let speakPollCursor = 0;
  let speakPollTimer = 0;

  const vowelOpen = { a: 0.9, e: 0.55, i: 0.25, o: 0.85, u: 0.45, y: 0.35 };
  function vowelFromChar(ch) {
    const c = ch.toLowerCase();
    if ('aáàâ'.includes(c)) return vowelOpen.a;
    if ('eéèê'.includes(c)) return vowelOpen.e;
    if ('iíìî'.includes(c)) return vowelOpen.i;
    if ('oóòô'.includes(c)) return vowelOpen.o;
    if ('uúùû'.includes(c)) return vowelOpen.u;
    if ('yw'.includes(c)) return vowelOpen.y;
    if ('bmp'.includes(c)) return 0.08;
    if ('fv'.includes(c)) return 0.18;
    if ('lr'.includes(c)) return 0.22;
    if ('szx'.includes(c)) return 0.15;
    if (c === ' ') return 0.05;
    return 0.28;
  }

  function regionAt(nx, ny) {
    if (ny < 0.24) return 0;
    if (ny < 0.48 && nx > 0.18 && nx < 0.82) return 1;
    if (ny > 0.52 && ny < 0.78 && nx > 0.28 && nx < 0.72) return 2;
    if (ny > 0.78) return 3;
    return 4;
  }

  function particleSize(count) {
    if (count > 60000) return 0.028;
    if (count > 20000) return 0.038;
    return 0.052;
  }

  let typingUntil = 0;
  sayInput.addEventListener('focus', function () { typingUntil = Date.now() + 120000; });
  sayInput.addEventListener('keydown', function () { typingUntil = Date.now() + 8000; });

  function speakLine(line, source) {
    const text = (line || '').trim();
    if (!text) return;
    if (source !== 'you' && document.activeElement === sayInput && Date.now() < typingUntil) return;
    sayInput.value = text;
    sayInput.classList.add('live');
    setTimeout(function () { sayInput.classList.remove('live'); }, 1200);
    saying = text;
    sayPhase = 0;
    sayTimer = Math.max(1.4, text.length * 0.06);
    statusEl.textContent = (source || 'lira') + ' → ' + text.slice(0, 52) + (text.length > 52 ? '…' : '');
  }

  function buildParticles(targetCount) {
    if (!portraitReady) return;
    if (points) {
      scene.remove(points);
      geom && geom.dispose();
      points.material.dispose();
    }
    const samp = document.createElement('canvas');
    const sw = portrait.naturalWidth;
    const sh = portrait.naturalHeight;
    samp.width = sw;
    samp.height = sh;
    const sctx2 = samp.getContext('2d');
    sctx2.drawImage(portrait, 0, 0);
    const img = sctx2.getImageData(0, 0, sw, sh).data;
    const aspect = sw / sh;
    const candidates = [];
    const stride = Math.max(1, Math.floor(Math.sqrt((sw * sh) / (targetCount * 1.4))));
    for (let y = 0; y < sh; y += stride) {
      for (let x = 0; x < sw; x += stride) {
        const i = (y * sw + x) * 4;
        const r = img[i], g = img[i + 1], b = img[i + 2], a = img[i + 3];
        const lum = (r * 0.299 + g * 0.587 + b * 0.114) / 255;
        if (a < 40 || lum < 0.07) continue;
        const nx = x / sw, ny = y / sh;
        candidates.push({
          x: (nx - 0.5) * aspect * 1.65,
          y: (0.46 - ny) * 1.65,
          z: (Math.random() - 0.5) * 0.02,
          r: r / 255, g: g / 255, b: b / 255,
          nx: nx, ny: ny, reg: regionAt(nx, ny),
          seed: Math.random() * Math.PI * 2,
        });
      }
    }
    candidates.sort(function () { return Math.random() - 0.5; });
    const picked = candidates.slice(0, targetCount);
    particleCount = picked.length;
    if (!particleCount) {
      statusEl.textContent = 'no particles — portrait failed to sample';
      return;
    }
    geom = new THREE.BufferGeometry();
    basePos = new Float32Array(particleCount * 3);
    colors = new Float32Array(particleCount * 3);
    baseColors = new Float32Array(particleCount * 3);
    regions = new Uint8Array(particleCount);
    for (let i = 0; i < particleCount; i++) {
      const p = picked[i];
      basePos[i * 3] = p.x;
      basePos[i * 3 + 1] = p.y;
      basePos[i * 3 + 2] = p.z;
      colors[i * 3] = baseColors[i * 3] = p.r;
      colors[i * 3 + 1] = baseColors[i * 3 + 1] = p.g;
      colors[i * 3 + 2] = baseColors[i * 3 + 2] = p.b;
      regions[i] = p.reg;
    }
    geom.setAttribute('position', new THREE.BufferAttribute(basePos.slice(), 3));
    geom.setAttribute('color', new THREE.BufferAttribute(colors.slice(), 3));
    geom.userData.seeds = picked.map(function (p) { return p.seed; });
    const mat = new THREE.PointsMaterial({
      size: particleSize(particleCount),
      vertexColors: true, transparent: true, opacity: 0.95,
      depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true,
    });
    points = new THREE.Points(geom, mat);
    scene.add(points);
    statusEl.textContent = particleCount.toLocaleString() + ' particles · chosen face';
  }

  function tickPBlink(dt) {
    pBlinkT -= dt;
    if (pBlinkT <= 0 && pBlink <= 0) { pBlink = 1; pBlinkT = 0.12; }
    if (pBlink > 0) {
      pBlink -= dt * 8.5;
      if (pBlink < 0) { pBlink = 0; pBlinkT = 2.4 + Math.random() * 4; }
    }
  }

  function driveSpeech(dt) {
    if (sayTimer > 0) {
      sayTimer -= dt;
      jawTarget = vowelFromChar(saying[Math.floor(sayPhase * saying.length)] || ' ');
      sayPhase += dt * 11;
      if (sayPhase >= 1) { sayPhase = 0; sayTimer = 0; saying = ''; }
    } else if (sayInput.value.trim()) {
      jawTarget = vowelFromChar(sayInput.value[sayInput.value.length - 1] || ' ');
    } else {
      jawTarget *= 0.92;
    }
    const targetOpen = Math.min(1, jawTarget * 0.75 + speakEnergy * 0.85);
    mouthOpen += (targetOpen - mouthOpen) * 0.18;
    browLift += ((speakEnergy * 0.35) - browLift) * 0.1;
    voiceBar.style.width = Math.min(100, (speakEnergy * 70 + mouthOpen * 30) * 100) + '%';
  }

  function animateParticles() {
    if (!geom || !basePos) return;
    const pos = geom.attributes.position.array;
    const seeds = geom.userData.seeds;
    const breath = Math.sin(pt * 0.9) * 0.012;
    for (let i = 0; i < particleCount; i++) {
      const bx = basePos[i * 3], by = basePos[i * 3 + 1], bz = basePos[i * 3 + 2];
      const reg = regions[i], seed = seeds[i];
      let dx = 0, dy = 0, dz = 0;
      dx += Math.sin(pt * 1.3 + seed) * 0.0015;
      dy += Math.cos(pt * 1.1 + seed * 1.7) * 0.0012 + breath;
      if (reg === 1) dy -= pBlink * 0.85 * 0.12 * Math.abs(bx) * 2.2;
      if (reg === 2) {
        dx += bx * mouthOpen * 0.09;
        dy -= mouthOpen * 0.11 * (0.4 + Math.sin(seed * 3));
        dz += mouthOpen * 0.02 * Math.sin(pt * 14 + seed);
      }
      if (reg === 0) dy += browLift * 0.04;
      if (reg === 3) dy -= mouthOpen * 0.04;
      const lantern = 0.5 + Math.sin(pt * 1.7 + bx * 4) * 0.2;
      if (bx > 0.08 && by > -0.05 && by < 0.35) {
        colors[i * 3] = Math.min(1, baseColors[i * 3] + lantern * 0.1);
        colors[i * 3 + 1] = Math.min(1, baseColors[i * 3 + 1] * 0.9 + lantern * 0.07);
        colors[i * 3 + 2] = baseColors[i * 3 + 2] * 0.88;
      } else {
        colors[i * 3] = baseColors[i * 3];
        colors[i * 3 + 1] = baseColors[i * 3 + 1];
        colors[i * 3 + 2] = baseColors[i * 3 + 2];
      }
      pos[i * 3] = bx + dx;
      pos[i * 3 + 1] = by + dy;
      pos[i * 3 + 2] = bz + dz + Math.sin(pt * 0.8 + seed) * 0.003;
    }
    geom.attributes.position.needsUpdate = true;
    geom.attributes.color.needsUpdate = true;
  }

  async function pollChatSpeak() {
    speakPollTimer += 0.2;
    if (speakPollTimer < 0.25) return;
    speakPollTimer = 0;
    try {
      const res = await fetch(assetUrl('lira-speak.jsonl') + '?t=' + Date.now());
      if (!res.ok) return;
      const text = await res.text();
      const lines = text.trim().split('\n').filter(Boolean);
      if (lines.length <= speakPollCursor) return;
      for (let i = speakPollCursor; i < lines.length; i++) {
        try {
          const row = JSON.parse(lines[i]);
          if (row.text) speakLine(row.text, row.from || 'lira');
        } catch (e) { /* skip bad line */ }
      }
      speakPollCursor = lines.length;
    } catch (e) { /* offline ok */ }
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
      statusEl.textContent = particleCount.toLocaleString() + ' particles · listening';
    } catch (e) {
      statusEl.textContent = 'mic denied — type instead';
      micOn = false;
    }
  }

  function stopMic() {
    micOn = false;
    micBtn.textContent = 'mic off';
    micBtn.classList.remove('on');
    if (micStream) micStream.getTracks().forEach(function (tr) { tr.stop(); });
    micStream = null;
    speakEnergy = 0;
  }

  function pollMic() {
    if (!analyser) return;
    const buf = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(buf);
    let sum = 0;
    for (let i = 2; i < 48; i++) sum += buf[i];
    speakEnergy = Math.min(1, (sum / 46) / 140);
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

  try {
    const chan = new BroadcastChannel('lira-speak');
    chan.onmessage = function (ev) {
      if (ev.data && ev.data.text) speakLine(ev.data.text, ev.data.from || 'lira');
    };
  } catch (e) { /* ok */ }

  micBtn.addEventListener('click', function () {
    if (micOn) { stopMic(); recognition && recognition.stop(); }
    else startMic().then(function () { recognition && recognition.start(); }).catch(function () {});
  });
  function sendFromInput() {
    const line = sayInput.value.trim();
    if (!line) return;
    typingUntil = 0;
    speakLine(line, 'you');
  }
  speakBtn.addEventListener('click', sendFromInput);
  var sayForm = document.getElementById('sayForm');
  if (sayForm) {
    sayForm.addEventListener('submit', function (e) {
      e.preventDefault();
      sendFromInput();
    });
  }
  sayInput.addEventListener('input', function () {
    typingUntil = Date.now() + 8000;
    const line = sayInput.value.trim();
    if (line) jawTarget = vowelFromChar(line[line.length - 1]);
  });
  countSel.addEventListener('change', function () { buildParticles(parseInt(countSel.value, 10)); });

  function particleFrame(now) {
    if (!running) return;
    const dt = Math.min(0.05, (now - pLast) / 1000);
    pLast = now;
    pt += dt;
    if (micOn) pollMic();
    pollChatSpeak();
    tickPBlink(dt);
    driveSpeech(dt);
    animateParticles();
    if (points) points.rotation.y = Math.sin(pt * 0.15) * 0.02;
    renderer.render(scene, camera);
    pRaf = requestAnimationFrame(particleFrame);
  }

  function resizeRenderer() {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight, false);
  }
  addEventListener('resize', resizeRenderer);

  function onPortraitReady() {
    portraitReady = true;
    setupSpeechRec();
    resizeRenderer();
    buildParticles(parseInt(countSel.value, 10));
    if (getActive()) {
      running = true;
      pLast = performance.now();
      cancelAnimationFrame(pRaf);
      pRaf = requestAnimationFrame(particleFrame);
    }
  }

  portrait.onload = onPortraitReady;
  portrait.onerror = function () {
    statusEl.textContent = 'portrait load failed — check lira-face.jpg';
  };
  if (portrait.complete && portrait.naturalWidth) onPortraitReady();

  return {
    resume: function () {
      resizeRenderer();
      if (portraitReady && !geom) buildParticles(parseInt(countSel.value, 10));
      running = true;
      pLast = performance.now();
      cancelAnimationFrame(pRaf);
      pRaf = requestAnimationFrame(particleFrame);
    },
    pause: function () {
      running = false;
      cancelAnimationFrame(pRaf);
      stopMic();
      if (recognition) recognition.stop();
    },
    speak: speakLine,
  };
};