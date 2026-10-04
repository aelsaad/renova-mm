/* RENOVA MM — 3D hero: a house in the brand colours that builds itself,
   the logo's towers behind it, and floating tools orbiting around. */
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

const canvas = document.getElementById("hero3d");
const host = document.getElementById("heroVisual");

try {
  if (canvas) init();
} catch (err) {
  console.warn("3D scene disabled:", err);
  document.documentElement.classList.add("no-webgl");
}

function init() {
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(renderer), 0.04).texture;

  const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 100);
  const LOOK = new THREE.Vector3(0, 1.55, 0);

  /* ---------- materials (brand palette) ---------- */
  const M = {
    gold: new THREE.MeshStandardMaterial({ color: 0xc99a3a, metalness: 1, roughness: 0.26 }),
    goldSoft: new THREE.MeshStandardMaterial({ color: 0xd8aa4a, metalness: 0.9, roughness: 0.38 }),
    char: new THREE.MeshStandardMaterial({ color: 0x272a2d, metalness: 0.25, roughness: 0.55 }),
    charMatte: new THREE.MeshStandardMaterial({ color: 0x23262a, roughness: 0.85 }),
    ivory: new THREE.MeshStandardMaterial({ color: 0xf1ebdf, roughness: 0.78 }),
    steel: new THREE.MeshStandardMaterial({ color: 0xd4d8dc, metalness: 1, roughness: 0.2 }),
    glow: new THREE.MeshStandardMaterial({ color: 0xffe2a0, emissive: 0xffc861, emissiveIntensity: 1.4, roughness: 0.3 }),
    bulb: new THREE.MeshStandardMaterial({ color: 0xfff4d6, emissive: 0xffd27a, emissiveIntensity: 2.2, roughness: 0.15 }),
    plinth: new THREE.MeshStandardMaterial({ color: 0x1b1d20, metalness: 0.3, roughness: 0.6 })
  };

  const root = new THREE.Group();
  scene.add(root);

  /* ---------- pedestal ---------- */
  const pedestal = new THREE.Group();
  root.add(pedestal);
  const ped = new THREE.Mesh(new THREE.CylinderGeometry(3.1, 3.25, 0.34, 96), M.plinth);
  ped.position.y = -0.17;
  ped.receiveShadow = true;
  pedestal.add(ped);
  const rim = new THREE.Mesh(new THREE.TorusGeometry(3.105, 0.028, 12, 200), M.gold);
  rim.rotation.x = Math.PI / 2;
  pedestal.add(rim);
  [2.2, 1.35].forEach((r) => {
    const ring = new THREE.Mesh(new THREE.RingGeometry(r - 0.012, r + 0.012, 160),
      new THREE.MeshBasicMaterial({ color: 0xc99a3a, transparent: true, opacity: 0.35 }));
    ring.rotation.x = -Math.PI / 2;
    ring.position.y = 0.002;
    pedestal.add(ring);
  });

  /* ---------- the house (built from parts that fall into place) ---------- */
  const house = new THREE.Group();
  root.add(house);
  const parts = [];
  const PITCH = THREE.MathUtils.degToRad(39); // same roof pitch as the logo

  function part(geo, mat, x, y, z, opts = {}) {
    const m = new THREE.Mesh(geo, mat);
    m.position.set(x, y, z);
    if (opts.rz) m.rotation.z = opts.rz;
    if (opts.ry) m.rotation.y = opts.ry;
    m.castShadow = opts.shadow !== false;
    m.receiveShadow = true;
    house.add(m);
    parts.push({ mesh: m, target: m.position.clone(), order: opts.order ?? parts.length });
    return m;
  }

  const W = 2.4, D = 2.0, H = 1.5, base = 0.12;
  part(new THREE.BoxGeometry(W + 0.18, base, D + 0.18), M.char, 0, base / 2, 0, { order: 0 });
  part(new THREE.BoxGeometry(W, H, D), M.ivory, 0, base + H / 2, 0, { order: 1 });

  const rise = (W / 2) * Math.tan(PITCH);
  const gable = new THREE.Shape();
  gable.moveTo(-W / 2, 0); gable.lineTo(W / 2, 0); gable.lineTo(0, rise); gable.closePath();
  const gableGeo = new THREE.ExtrudeGeometry(gable, { depth: D, bevelEnabled: false });
  gableGeo.translate(0, 0, -D / 2);
  part(gableGeo, M.ivory, 0, base + H, 0, { order: 2 });

  // roof panels at the logo's pitch
  const slope = (W / 2) / Math.cos(PITCH);
  const panelGeo = new THREE.BoxGeometry(slope + 0.32, 0.14, D + 0.4);
  const top = base + H;
  const nx = Math.sin(PITCH), ny = Math.cos(PITCH);
  part(panelGeo, M.char, -W / 4 - nx * 0.07 - 0.06, top + rise / 2 + ny * 0.07 - 0.04, 0, { rz: PITCH, order: 3 });
  part(panelGeo, M.char, W / 4 + nx * 0.07 + 0.06, top + rise / 2 + ny * 0.07 - 0.04, 0, { rz: -PITCH, order: 3 });
  // gold trim under the eaves (front), like the gold roof line in the logo
  const trimGeo = new THREE.BoxGeometry(slope * 0.86, 0.045, 0.05);
  part(trimGeo, M.gold, -W / 4 + 0.04, top + rise / 2 - 0.13, D / 2 + 0.03, { rz: PITCH, order: 4, shadow: false });
  part(trimGeo, M.gold, W / 4 - 0.04, top + rise / 2 - 0.13, D / 2 + 0.03, { rz: -PITCH, order: 4, shadow: false });
  // the logo's four-pane window on the gable
  [[-1, 1], [1, 1], [-1, -1], [1, -1]].forEach(([sx, sy]) => {
    part(new THREE.BoxGeometry(0.13, 0.13, 0.04), M.gold, sx * 0.08, top + 0.42 + sy * 0.08, D / 2 + 0.02, { order: 5, shadow: false });
  });
  // door + knob
  part(new THREE.BoxGeometry(0.5, 0.92, 0.06), M.char, 0.5, base + 0.46, D / 2 + 0.02, { order: 5 });
  part(new THREE.SphereGeometry(0.035, 16, 12), M.gold, 0.68, base + 0.46, D / 2 + 0.07, { order: 6, shadow: false });
  // lit windows
  function windowAt(x, y, z, ry = 0) {
    const frame = part(new THREE.BoxGeometry(0.52, 0.46, 0.05), M.char, x, y, z, { ry, order: 5 });
    const glass = part(new THREE.BoxGeometry(0.42, 0.36, 0.02), M.glow, x, y, z, { ry, order: 6, shadow: false });
    const off = 0.025;
    if (ry) { glass.position.x += off; parts[parts.length - 1].target.x += off; } else { glass.position.z += off; parts[parts.length - 1].target.z += off; }
    return frame;
  }
  windowAt(-0.5, base + 0.82, D / 2 + 0.02);
  windowAt(W / 2 + 0.02, base + 0.82, -0.45, Math.PI / 2);
  windowAt(W / 2 + 0.02, base + 0.82, 0.45, Math.PI / 2);
  // chimney
  part(new THREE.BoxGeometry(0.3, 0.7, 0.3), M.char, 0.62, top + 0.62, -0.45, { order: 7 });
  part(new THREE.BoxGeometry(0.38, 0.06, 0.38), M.gold, 0.62, top + 1.0, -0.45, { order: 8 });

  /* ---------- the logo's towers behind the house ---------- */
  const towers = [
    { x: -1.05, h: 2.9, m: M.gold }, { x: -0.55, h: 3.55, m: M.gold }, { x: -0.05, h: 4.15, m: M.gold },
    { x: 0.5, h: 3.75, m: M.char, step: true }, { x: 1.02, h: 3.0, m: M.char }
  ];
  towers.forEach((tw, i) => {
    const g = new THREE.BoxGeometry(0.4, tw.h, 0.4);
    part(g, tw.m, tw.x, tw.h / 2, -1.55, { order: 9 + i });
    if (tw.m === M.char) {
      // small lit windows on the anthracite towers
      for (let y = 2.2; y < tw.h - 0.3; y += 0.32) {
        part(new THREE.BoxGeometry(0.1, 0.16, 0.02), M.glow, tw.x, y, -1.34, { order: 14, shadow: false });
      }
    }
    if (tw.step) part(new THREE.BoxGeometry(0.4, 0.45, 0.4), M.char, tw.x + 0.06, tw.h + 0.32, -1.62, { order: 15 });
  });

  /* ---------- floating tools ---------- */
  const tools = new THREE.Group();
  root.add(tools);

  function screwdriver() {
    const g = new THREE.Group();
    const handle = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.17, 0.8, 32), M.char);
    g.add(handle);
    [-0.22, 0, 0.22].forEach((y) => {
      const r = new THREE.Mesh(new THREE.TorusGeometry(0.158, 0.022, 10, 40), M.gold);
      r.rotation.x = Math.PI / 2; r.position.y = y; g.add(r);
    });
    const ferrule = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.11, 0.14, 24), M.gold);
    ferrule.position.y = -0.47; g.add(ferrule);
    const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.95, 16), M.steel);
    shaft.position.y = -1.0; g.add(shaft);
    const tip = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.18, 0.025), M.steel);
    tip.position.y = -1.55; g.add(tip);
    return g;
  }

  function wrench() {
    const g = new THREE.Group();
    const R = 0.34, w = 0.12, yTop = Math.sqrt(R * R - w * w);
    const head = new THREE.Shape();
    head.moveTo(w, yTop);
    head.absarc(0, 0, R, Math.atan2(yTop, w), Math.atan2(yTop, -w), true);
    head.lineTo(-w, -0.04); head.lineTo(w, -0.04); head.lineTo(w, yTop);
    const ext = { depth: 0.08, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.02, bevelSegments: 2 };
    const h1 = new THREE.Mesh(new THREE.ExtrudeGeometry(head, ext), M.gold);
    h1.position.set(0, 0.85, -0.04); g.add(h1);
    const handle = new THREE.Mesh(new THREE.BoxGeometry(0.2, 1.5, 0.1), M.gold);
    handle.position.y = 0; g.add(handle);
    const ring = new THREE.Shape(); ring.absarc(0, 0, 0.24, 0, Math.PI * 2, false);
    const hole = new THREE.Path(); hole.absarc(0, 0, 0.12, 0, Math.PI * 2, true); ring.holes.push(hole);
    const h2 = new THREE.Mesh(new THREE.ExtrudeGeometry(ring, ext), M.gold);
    h2.position.set(0, -0.82, -0.04); g.add(h2);
    return g;
  }

  function hammer() {
    const g = new THREE.Group();
    const handle = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.075, 1.5, 20), M.char);
    g.add(handle);
    const grip = new THREE.Mesh(new THREE.CylinderGeometry(0.085, 0.09, 0.5, 20), M.gold);
    grip.position.y = -0.48; g.add(grip);
    const headMain = new THREE.Mesh(new THREE.BoxGeometry(0.62, 0.2, 0.2), M.steel);
    headMain.position.set(0.08, 0.78, 0); g.add(headMain);
    const face = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.13, 0.16, 24), M.steel);
    face.rotation.z = Math.PI / 2; face.position.set(0.45, 0.78, 0); g.add(face);
    const claw = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.1, 0.16), M.steel);
    claw.position.set(-0.33, 0.72, 0); claw.rotation.z = 0.5; g.add(claw);
    return g;
  }

  function screw() {
    const g = new THREE.Group();
    const head = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.2, 0.1, 32), M.gold);
    g.add(head);
    [0, Math.PI / 2].forEach((r) => {
      const slot = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.04, 0.05), M.charMatte);
      slot.position.y = 0.04; slot.rotation.y = r; g.add(slot);
    });
    const L = 1.0;
    const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.06, L, 20), M.steel);
    shaft.position.y = -L / 2 - 0.05; g.add(shaft);
    class Helix extends THREE.Curve {
      getPoint(t, out = new THREE.Vector3()) {
        const a = t * Math.PI * 2 * 9;
        const r = 0.085 - t * 0.02;
        return out.set(Math.cos(a) * r, -0.1 - t * (L - 0.1), Math.sin(a) * r);
      }
    }
    const thread = new THREE.Mesh(new THREE.TubeGeometry(new Helix(), 260, 0.022, 6, false), M.steel);
    g.add(thread);
    const tip = new THREE.Mesh(new THREE.ConeGeometry(0.06, 0.18, 20), M.steel);
    tip.rotation.x = Math.PI; tip.position.y = -L - 0.13; g.add(tip);
    return g;
  }

  function nut() {
    const g = new THREE.Group();
    const s = new THREE.Shape();
    for (let i = 0; i < 6; i++) {
      const a = (i / 6) * Math.PI * 2;
      const x = Math.cos(a) * 0.36, y = Math.sin(a) * 0.36;
      if (i === 0) s.moveTo(x, y); else s.lineTo(x, y);
    }
    s.closePath();
    const hole = new THREE.Path(); hole.absarc(0, 0, 0.16, 0, Math.PI * 2, true); s.holes.push(hole);
    const m = new THREE.Mesh(new THREE.ExtrudeGeometry(s, { depth: 0.22, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.03, bevelSegments: 3 }), M.gold);
    m.position.z = -0.11; g.add(m);
    return g;
  }

  function bulb() {
    const g = new THREE.Group();
    const glass = new THREE.Mesh(new THREE.SphereGeometry(0.34, 40, 30), M.bulb);
    glass.position.y = 0.2; g.add(glass);
    const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.24, 0.24, 32), M.bulb);
    neck.position.y = -0.12; g.add(neck);
    const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.26, 32), M.steel);
    cap.position.y = -0.36; g.add(cap);
    [-0.28, -0.36, -0.44].forEach((y) => {
      const r = new THREE.Mesh(new THREE.TorusGeometry(0.165, 0.02, 8, 32), M.steel);
      r.rotation.x = Math.PI / 2; r.position.y = y; g.add(r);
    });
    const tipC = new THREE.Mesh(new THREE.SphereGeometry(0.07, 16, 10), M.gold);
    tipC.position.y = -0.52; g.add(tipC);
    const light = new THREE.PointLight(0xffc861, 6, 4, 2);
    light.position.y = 0.2; g.add(light);
    return g;
  }

  const toolDefs = [
    { make: screwdriver, angle: 0.3, radius: 3.55, y: 2.6, tilt: [0.5, 0, 0.9], s: 0.85 },
    { make: wrench, angle: 1.45, radius: 3.65, y: 1.4, tilt: [0.3, 0.4, -0.6], s: 0.8 },
    { make: bulb, angle: 2.55, radius: 3.4, y: 3.3, tilt: [0.15, 0, -0.2], s: 0.9 },
    { make: hammer, angle: 3.6, radius: 3.6, y: 2.2, tilt: [0.2, 0.3, 0.7], s: 0.8 },
    { make: screw, angle: 4.6, radius: 3.5, y: 3.0, tilt: [0.4, 0, -0.5], s: 0.9 },
    { make: nut, angle: 5.5, radius: 3.45, y: 1.2, tilt: [1.0, 0.4, 0], s: 0.8 }
  ];
  const floaters = toolDefs.map((d, i) => {
    const pivot = new THREE.Group();
    const obj = d.make();
    obj.scale.setScalar(d.s);
    obj.rotation.set(...d.tilt);
    obj.traverse((o) => { if (o.isMesh) o.castShadow = true; });
    pivot.add(obj);
    tools.add(pivot);
    return { pivot, obj, ...d, phase: i * 1.3, spin: 0.25 + (i % 3) * 0.12 };
  });

  /* ---------- gold dust ---------- */
  const DUST = 260;
  const dpos = new Float32Array(DUST * 3);
  for (let i = 0; i < DUST; i++) {
    const r = 1.5 + Math.random() * 4.2, a = Math.random() * Math.PI * 2;
    dpos[i * 3] = Math.cos(a) * r;
    dpos[i * 3 + 1] = Math.random() * 5.2 - 0.2;
    dpos[i * 3 + 2] = Math.sin(a) * r;
  }
  const dustGeo = new THREE.BufferGeometry();
  dustGeo.setAttribute("position", new THREE.BufferAttribute(dpos, 3));
  const dotCanvas = document.createElement("canvas");
  dotCanvas.width = dotCanvas.height = 64;
  const dc = dotCanvas.getContext("2d");
  const grd = dc.createRadialGradient(32, 32, 0, 32, 32, 32);
  grd.addColorStop(0, "rgba(255,230,170,1)"); grd.addColorStop(0.4, "rgba(232,192,103,.5)"); grd.addColorStop(1, "rgba(0,0,0,0)");
  dc.fillStyle = grd; dc.fillRect(0, 0, 64, 64);
  const dust = new THREE.Points(dustGeo, new THREE.PointsMaterial({
    size: 0.09, map: new THREE.CanvasTexture(dotCanvas), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending
  }));
  root.add(dust);

  /* ---------- lights ---------- */
  scene.add(new THREE.HemisphereLight(0xfff4e0, 0x1a1c1f, 0.55));
  const key = new THREE.DirectionalLight(0xfff0d6, 2.4);
  key.position.set(5, 9, 6);
  key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024);
  Object.assign(key.shadow.camera, { left: -5, right: 5, top: 6, bottom: -4, near: 1, far: 30 });
  key.shadow.bias = -0.0008;
  key.shadow.radius = 4;
  key.shadow.camera.updateProjectionMatrix();
  scene.add(key);
  const rimLight = new THREE.DirectionalLight(0xe8c067, 1.6);
  rimLight.position.set(-6, 4, -6);
  scene.add(rimLight);

  /* ---------- layout ---------- */
  function resize() {
    const r = canvas.getBoundingClientRect();
    const w = Math.max(1, r.width), h = Math.max(1, r.height);
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    // keep the whole scene in frame on narrow screens
    const dist = w / h < 0.9 ? 17.5 : 15;
    camera.position.set(dist * 0.55, dist * 0.36, dist * 0.75);
    camera.lookAt(LOOK);
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(host);
  resize();

  /* ---------- interaction ---------- */
  let mx = 0, my = 0;
  addEventListener("pointermove", (e) => {
    mx = (e.clientX / innerWidth) * 2 - 1;
    my = (e.clientY / innerHeight) * 2 - 1;
  }, { passive: true });

  // build-in animation: every part drops into place in order
  const DROP = 3.2, STAGGER = 0.07, DUR = 0.75;
  parts.sort((a, b) => a.order - b.order);
  parts.forEach((p, i) => {
    p.delay = 0.3 + p.order * STAGGER * 1.6 + (i % 4) * 0.02;
    if (!reduceMotion) { p.mesh.position.y = p.target.y + DROP; p.mesh.visible = false; }
  });
  const landedAt = reduceMotion ? 0 : Math.max(...parts.map((p) => p.delay)) + DUR; // house fully assembled
  const badgesAt = reduceMotion ? 0 : Math.min(...parts.map((p) => p.delay)); // badges start with the first falling piece
  let badgesShown = false;
  const easeOutBack = (x) => { const c1 = 1.5, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
  floaters.forEach((f) => { f.pivot.scale.setScalar(reduceMotion ? 1 : 0.001); });

  /* ---------- render loop (paused when off-screen) ---------- */
  let visible = true;
  new IntersectionObserver((en) => { visible = en[0].isIntersecting; }).observe(host);
  const clock = new THREE.Clock();
  let rotY = -0.5;

  function frame() {
    requestAnimationFrame(frame);
    if (!visible) { clock.getDelta(); return; }
    const dt = Math.min(clock.getDelta(), 0.05);
    const t = clock.elapsedTime;

    // assemble
    for (const p of parts) {
      if (reduceMotion) break;
      const k = (t - p.delay) / DUR;
      if (k <= 0) continue;
      p.mesh.visible = true;
      const e = k >= 1 ? 1 : easeOutBack(k);
      p.mesh.position.y = p.target.y + DROP * (1 - e);
    }
    if (!badgesShown && t >= badgesAt) { badgesShown = true; host.classList.add("badges-in"); }
    const toolsIn = reduceMotion ? 1 : THREE.MathUtils.clamp((t - 2.6) / 1.2, 0, 1);

    // slow showcase rotation + mouse parallax
    if (!reduceMotion) rotY += dt * 0.12;
    root.rotation.y += ((rotY + mx * 0.35) - root.rotation.y) * 0.05;
    root.rotation.x += ((my * 0.06) - root.rotation.x) * 0.05;
    tools.rotation.y = reduceMotion ? 0 : -t * 0.08;

    floaters.forEach((f) => {
      const a = f.angle;
      f.pivot.position.set(Math.cos(a) * f.radius, f.y + Math.sin(t * 0.9 + f.phase) * 0.18, Math.sin(a) * f.radius);
      f.obj.rotation.y = f.tilt[1] + t * f.spin;
      const s = THREE.MathUtils.smoothstep(toolsIn, 0, 1);
      f.pivot.scale.setScalar(Math.max(0.001, s));
    });
    dust.rotation.y = t * 0.03;

    renderer.render(scene, camera);
  }
  frame();
}
