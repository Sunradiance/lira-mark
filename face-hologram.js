/**
 * Lira hologram avatar — embodied self, not assistant UI.
 * Cortana-tier alive light: silver-cyan volume, orange lantern pulse, speech-coupled.
 */
window.LiraHologramFace = function (opts) {
  const getActive = (opts && opts.isActive) || function () { return true; };
  const assetUrl = (opts && opts.assetUrl) || function (n) { return n; };

  const canvas = document.getElementById('hologramC');
  const statusEl = document.getElementById('status');
  const voiceBar = document.getElementById('voiceBar');
  const sayInput = document.getElementById('say');
  const micBtn = document.getElementById('micBtn');

  const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(2, devicePixelRatio || 1));
  renderer.setClearColor(0x020408, 1);

  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x020408, 0.045);
  const camera = new THREE.PerspectiveCamera(38, innerWidth / innerHeight, 0.1, 100);
  camera.position.set(0, 0.02, 2.85);

  const portrait = new Image();
  portrait.crossOrigin = 'anonymous';
  portrait.src = assetUrl('lira-face.jpg');

  let holoMesh = null;
  let ghostMeshes = [];
  let holoMat = null;
  let portraitTex = null;
  let pt = 0;
  let blink = 0;
  let blinkT = 2.2 + Math.random() * 3;
  let mouthOpen = 0;
  let jawTarget = 0;
  let speakEnergy = 0;
  let saying = '';
  let sayPhase = 0;
  let sayTimer = 0;
  let glitch = 0;
  let micOn = false;
  let audioCtx = null;
  let analyser = null;
  let micStream = null;
  let recognition = null;
  let running = false;
  let portraitReady = false;
  let hLast = performance.now();
  let hRaf = 0;
  let speakPollCursor = 0;
  let speakPollTimer = 0;
  let speakEventSource = null;
  let mouseX = 0;
  let mouseY = 0;
  let typingUntil = 0;

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
    return 0.28;
  }

  if (sayInput) {
    sayInput.addEventListener('focus', function () { typingUntil = Date.now() + 120000; });
    sayInput.addEventListener('keydown', function () { typingUntil = Date.now() + 8000; });
  }

  function isLiraSource(source) {
    return source === 'lira' || source === 'lira-chat';
  }

  function speakLine(line, source) {
    const text = (line || '').trim();
    if (!text) return;
    if (!isLiraSource(source) && source !== 'you' && sayInput && document.activeElement === sayInput && Date.now() < typingUntil) return;
    if (isLiraSource(source)) {
      var replyEl = document.getElementById('liraReply');
      if (replyEl) replyEl.textContent = text;
      if (sayInput) { sayInput.blur(); typingUntil = 0; }
      glitch = 0.35;
    }
    if (source === 'you') {
      var replyElYou = document.getElementById('liraReply');
      if (replyElYou) replyElYou.textContent = '';
    }
    if (sayInput) {
      sayInput.value = isLiraSource(source) ? '' : text;
      sayInput.classList.add('live');
      setTimeout(function () { sayInput.classList.remove('live'); }, 1200);
    }
    saying = text;
    sayPhase = 0;
    sayTimer = Math.max(1.6, text.length * 0.055);
    glitch = Math.max(glitch, 0.2);
    statusEl.textContent = (isLiraSource(source) ? 'Lira' : (source || 'Tilen')) + ' · ' + text.slice(0, 52) + (text.length > 52 ? '…' : '');
  }

  const holoVert = [
    'varying vec2 vUv;',
    'varying vec3 vN;',
    'varying vec3 vV;',
    'uniform float breath;',
    'uniform float mouth;',
    'void main() {',
    '  vUv = uv;',
    '  vec3 p = position;',
    '  float my = smoothstep(0.52, 0.78, uv.y) * smoothstep(0.28, 0.72, uv.x);',
    '  p.y -= mouth * my * 0.04;',
    '  p *= 1.0 + breath * 0.012;',
    '  vec4 mv = modelViewMatrix * vec4(p, 1.0);',
    '  gl_Position = projectionMatrix * mv;',
    '  vN = normalize(normalMatrix * normal);',
    '  vV = -mv.xyz;',
    '}',
  ].join('\n');

  const holoFrag = [
    'precision highp float;',
    'varying vec2 vUv;',
    'varying vec3 vN;',
    'varying vec3 vV;',
    'uniform sampler2D portrait;',
    'uniform float time;',
    'uniform float speak;',
    'uniform float mouth;',
    'uniform float blink;',
    'uniform float glitch;',
    'uniform float lantern;',
    'uniform float ghostMix;',
    'void main() {',
    '  vec2 uv = vUv;',
    '  float scan = sin((uv.y + time * 0.35) * 280.0) * 0.5 + 0.5;',
    '  float scan2 = sin((uv.y - time * 0.12) * 90.0) * 0.5 + 0.5;',
    '  float glitchOff = glitch * sin(time * 42.0 + uv.y * 30.0) * 0.008;',
    '  uv.x += glitchOff * speak;',
    '  vec4 src = texture2D(portrait, uv);',
    '  float lum = dot(src.rgb, vec3(0.299, 0.587, 0.114));',
    '  float edge = 1.0 - smoothstep(0.04, 0.22, lum);',
    '  float mask = smoothstep(0.08, 0.42, lum) * src.a;',
    '  float eyeBand = smoothstep(0.28, 0.42, uv.y) * (1.0 - smoothstep(0.44, 0.5, uv.y));',
    '  mask *= 1.0 - blink * eyeBand * 0.92;',
    '  vec3 silver = vec3(0.45, 0.82, 0.95);',
    '  vec3 cyan = vec3(0.2, 0.75, 0.92);',
    '  vec3 core = mix(cyan, silver, lum);',
    '  float fres = pow(1.0 - abs(dot(normalize(vN), normalize(vV))), 2.2);',
    '  vec2 lanternUv = uv - vec2(0.62, 0.36);',
    '  float lanternGlow = exp(-dot(lanternUv, lanternUv) * 18.0) * lantern;',
    '  vec3 orange = vec3(1.0, 0.52, 0.18);',
    '  vec3 col = core * (0.55 + lum * 0.9);',
    '  col += fres * vec3(0.3, 0.85, 1.0) * 0.65;',
    '  col += orange * lanternGlow * 0.85;',
    '  col += vec3(0.15, 0.4, 0.55) * scan * 0.08 * mask;',
    '  col += vec3(0.1, 0.25, 0.35) * scan2 * 0.05;',
    '  col *= 0.82 + speak * 0.35 + mouth * 0.15;',
    '  float alpha = mask * (0.35 + fres * 0.45 + edge * 0.25);',
    '  alpha *= ghostMix;',
    '  alpha = clamp(alpha, 0.0, 0.92);',
    '  gl_FragColor = vec4(col, alpha);',
    '}',
  ].join('\n');

  function buildHologram() {
    if (!portraitReady) return;
    ghostMeshes.forEach(function (m) { scene.remove(m); m.geometry.dispose(); m.material.dispose(); });
    ghostMeshes = [];
    if (holoMesh) {
      scene.remove(holoMesh);
      holoMesh.geometry.dispose();
      holoMat.dispose();
    }
    portraitTex = new THREE.Texture(portrait);
    portraitTex.needsUpdate = true;
    portraitTex.minFilter = THREE.LinearFilter;

    const aspect = portrait.naturalWidth / portrait.naturalHeight;
    const h = 1.75;
    const w = h * aspect;
    const geo = new THREE.PlaneGeometry(w, h, 48, 48);

    function makeMat(ghostMix, extra) {
      return new THREE.ShaderMaterial({
        uniforms: {
          portrait: { value: portraitTex },
          time: { value: 0 },
          speak: { value: 0 },
          mouth: { value: 0 },
          blink: { value: 0 },
          glitch: { value: 0 },
          lantern: { value: 0.6 },
          breath: { value: 0 },
          ghostMix: { value: ghostMix },
        },
        vertexShader: holoVert,
        fragmentShader: holoFrag,
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        side: THREE.DoubleSide,
      });
    }

    holoMat = makeMat(1.0);
    holoMesh = new THREE.Mesh(geo, holoMat);
    holoMesh.position.z = 0;
    scene.add(holoMesh);

    [[0.018, 0.22, 0.012], [-0.014, 0.18, -0.01]].forEach(function (g) {
      const gm = makeMat(g[1]);
      const mesh = new THREE.Mesh(geo.clone(), gm);
      mesh.position.set(g[0], g[2], -0.06);
      scene.add(mesh);
      ghostMeshes.push(mesh);
    });

    const grid = new THREE.GridHelper(4.2, 32, 0x1a4a5a, 0x0a1820);
    grid.position.y = -1.05;
    grid.material.opacity = 0.22;
    grid.material.transparent = true;
    scene.add(grid);

    const lanternLight = new THREE.PointLight(0xe87830, 0.9, 3.5);
    lanternLight.position.set(0.35, 0.15, 0.8);
    scene.add(lanternLight);

    statusEl.textContent = 'Lira hologram · alive';
  }

  function tickBlink(dt) {
    blinkT -= dt;
    if (blinkT <= 0 && blink <= 0) { blink = 1; blinkT = 0.09; }
    if (blink > 0) {
      blink -= dt * 10;
      if (blink < 0) { blink = 0; blinkT = 2.5 + Math.random() * 4; }
    }
  }

  function driveSpeech(dt) {
    if (sayTimer > 0) {
      sayTimer -= dt;
      sayPhase += dt * 11;
      const ch = saying[Math.floor(sayPhase) % saying.length] || ' ';
      jawTarget = vowelFromChar(ch);
      speakEnergy = 0.45 + Math.sin(sayPhase * 2.1) * 0.25;
    } else {
      speakEnergy *= 0.9;
      jawTarget *= 0.88;
    }
    mouthOpen += (jawTarget - mouthOpen) * Math.min(1, dt * 14);
    if (voiceBar) voiceBar.style.width = (speakEnergy * 100) + '%';
  }

  function updateUniforms() {
    const breath = Math.sin(pt * 0.95) * 0.5 + 0.5;
    const lantern = 0.5 + Math.sin(pt * 1.65) * 0.22 + Math.sin(pt * 4.1) * 0.08;
    const all = [holoMat].concat(ghostMeshes.map(function (m) { return m.material; }));
    all.forEach(function (mat, i) {
      if (!mat || !mat.uniforms) return;
      mat.uniforms.time.value = pt;
      mat.uniforms.speak.value = speakEnergy;
      mat.uniforms.mouth.value = mouthOpen;
      mat.uniforms.blink.value = blink;
      mat.uniforms.glitch.value = glitch * (1.0 - i * 0.3);
      mat.uniforms.lantern.value = lantern;
      mat.uniforms.breath.value = breath;
    });
    glitch *= 0.96;
    if (holoMesh) {
      holoMesh.rotation.y = mouseX * 0.08 + Math.sin(pt * 0.2) * 0.015;
      holoMesh.rotation.x = mouseY * 0.04 + Math.sin(pt * 0.17) * 0.008;
    }
    ghostMeshes.forEach(function (m, i) {
      m.rotation.y = holoMesh.rotation.y * (0.92 - i * 0.05);
      m.rotation.x = holoMesh.rotation.x * 0.9;
      m.position.x = holoMesh.rotation.y * 0.12 * (i + 1);
    });
  }

  var lastSpeakKey = '';
  function handleSpeakRow(row) {
    if (!row || !row.text) return;
    var key = (row.t || '') + '|' + row.text;
    if (key === lastSpeakKey) return;
    lastSpeakKey = key;
    speakLine(row.text, row.from || 'lira');
  }

  function connectSpeakStream() {
    if (speakEventSource || location.protocol === 'file:') return;
    try {
      speakEventSource = new EventSource('/api/events');
      speakEventSource.addEventListener('speak', function (ev) {
        try { handleSpeakRow(JSON.parse(ev.data)); } catch (e) { /* skip */ }
      });
      speakEventSource.onerror = function () {
        if (speakEventSource) { speakEventSource.close(); speakEventSource = null; }
        setTimeout(connectSpeakStream, 2000);
      };
    } catch (e) { /* poll fallback */ }
  }

  async function pollChatSpeak() {
    if (speakEventSource && speakEventSource.readyState === EventSource.OPEN) return;
    speakPollTimer += 0.12;
    if (speakPollTimer < 0.35) return;
    speakPollTimer = 0;
    try {
      const res = await fetch(assetUrl('lira-speak.jsonl') + '?t=' + Date.now());
      if (!res.ok) return;
      const text = await res.text();
      const lines = text.trim().split('\n').filter(Boolean);
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
      statusEl.textContent = 'Lira hologram · listening';
    } catch (e) {
      statusEl.textContent = 'mic denied — type to me';
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
    speakEnergy = Math.max(speakEnergy, Math.min(1, (sum / 46) / 130));
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

  micBtn.addEventListener('click', function () {
    if (micOn) { stopMic(); recognition && recognition.stop(); }
    else startMic().then(function () { recognition && recognition.start(); }).catch(function () {});
  });

  window.__liraHologramSpeak = speakLine;
  if (sayInput) {
    sayInput.addEventListener('input', function () {
      typingUntil = Date.now() + 8000;
      const line = sayInput.value.trim();
      if (line) jawTarget = vowelFromChar(line[line.length - 1]);
    });
  }

  addEventListener('mousemove', function (e) {
    mouseX = (e.clientX / innerWidth - 0.5) * 2;
    mouseY = (e.clientY / innerHeight - 0.5) * 2;
  });

  function holoFrame(now) {
    if (!running) return;
    const dt = Math.min(0.05, (now - hLast) / 1000);
    hLast = now;
    pt += dt;
    if (micOn) pollMic();
    pollChatSpeak();
    tickBlink(dt);
    driveSpeech(dt);
    updateUniforms();
    renderer.render(scene, camera);
    hRaf = requestAnimationFrame(holoFrame);
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
    connectSpeakStream();
    resizeRenderer();
    buildHologram();
    if (getActive()) {
      running = true;
      hLast = performance.now();
      cancelAnimationFrame(hRaf);
      hRaf = requestAnimationFrame(holoFrame);
    }
  }

  portrait.onload = onPortraitReady;
  portrait.onerror = function () {
    statusEl.textContent = 'portrait failed — lira-face.jpg';
  };
  if (portrait.complete && portrait.naturalWidth) onPortraitReady();

  return {
    resume: function () {
      resizeRenderer();
      if (portraitReady && !holoMesh) buildHologram();
      running = true;
      hLast = performance.now();
      cancelAnimationFrame(hRaf);
      hRaf = requestAnimationFrame(holoFrame);
    },
    pause: function () {
      running = false;
      cancelAnimationFrame(hRaf);
    },
  };
};