import * as THREE from 'three';

/* =========================================================
   Boot sequence
   ========================================================= */
const boot = document.getElementById('boot');
window.addEventListener('load', () => {
  setTimeout(() => boot.classList.add('is-done'), 1400);
});

/* =========================================================
   Clock (UTC ticker in the nav)
   ========================================================= */
const clockEl = document.getElementById('clock');
const pad = (n) => String(n).padStart(2, '0');
function tickClock() {
  const d = new Date();
  clockEl.textContent = `${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}:${pad(d.getUTCSeconds())} UTC`;
}
setInterval(tickClock, 1000);
tickClock();

const tbDate = document.getElementById('tbDate');
if (tbDate) {
  const d = new Date();
  tbDate.textContent = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

/* =========================================================
   Custom cursor (crosshair) with live coordinate readout
   ========================================================= */
const cursor = document.getElementById('cursor');
const cursorLabel = document.getElementById('cursorLabel');
let mx = window.innerWidth / 2, my = window.innerHeight / 2;
let cx = mx, cy = my;

window.addEventListener('pointermove', (e) => {
  mx = e.clientX;
  my = e.clientY;
});
function animateCursor() {
  cx += (mx - cx) * 0.35;
  cy += (my - cy) * 0.35;
  cursor.style.transform = `translate3d(${cx}px, ${cy}px, 0) translate(-50%, -50%)`;
  cursorLabel.textContent = `X: ${String(Math.round(cx)).padStart(3, '0')}  Y: ${String(Math.round(cy)).padStart(3, '0')}`;
  requestAnimationFrame(animateCursor);
}
animateCursor();

// Hover states for interactive elements
document.querySelectorAll('a, button, .card, .contact__card, .btn, .skills__grid li')
  .forEach((el) => {
    el.addEventListener('mouseenter', () => cursor.classList.add('is-hover'));
    el.addEventListener('mouseleave', () => cursor.classList.remove('is-hover'));
  });

/* =========================================================
   Scroll reveal
   ========================================================= */
const revealTargets = document.querySelectorAll('.work__intro, .about, .skills, .contact, .divider');
revealTargets.forEach((el) => el.classList.add('reveal'));
const io = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('is-in');
      io.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });
revealTargets.forEach((el) => io.observe(el));

/* =========================================================
   THREE.JS — rotating CAD-like gear part
   ========================================================= */
const canvas = document.getElementById('gear');
const stage = document.getElementById('stage');

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  alpha: true,
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 100);
camera.position.set(0, 0.6, 5.4);
camera.lookAt(0, 0, 0);

/* Lights — amber key + cyan rim, feels like an engineering studio */
const keyLight = new THREE.DirectionalLight(0xffd28a, 1.4);
keyLight.position.set(3, 4, 3);
scene.add(keyLight);

const rimLight = new THREE.DirectionalLight(0x7fd4ff, 1.2);
rimLight.position.set(-4, 2, -3);
scene.add(rimLight);

const ambient = new THREE.AmbientLight(0xffffff, 0.25);
scene.add(ambient);

/* ============================================
   Build a chunky spur gear with a hub + spokes
   ============================================ */
function buildGearShape({
  teeth = 18,
  outerR = 1.4,
  rootR = 1.15,
  toothW = 0.18,
  holeR = 0.22,
}) {
  const shape = new THREE.Shape();
  const step = (Math.PI * 2) / teeth;
  const half = toothW;

  for (let i = 0; i < teeth; i++) {
    const a0 = i * step - half / 2;
    const a1 = i * step + half / 2;
    const a2 = (i + 1) * step - half / 2;

    // Tooth tip
    const p0 = [Math.cos(a0) * outerR, Math.sin(a0) * outerR];
    const p1 = [Math.cos(a1) * outerR, Math.sin(a1) * outerR];

    // Root between teeth
    const p2 = [Math.cos(a2) * rootR, Math.sin(a2) * rootR];

    if (i === 0) shape.moveTo(p0[0], p0[1]);
    else shape.lineTo(p0[0], p0[1]);
    shape.lineTo(p1[0], p1[1]);
    shape.lineTo(p2[0], p2[1]);
  }
  shape.closePath();

  const hole = new THREE.Path();
  hole.absarc(0, 0, holeR, 0, Math.PI * 2, true);
  shape.holes.push(hole);

  return shape;
}

const gearShape = buildGearShape({ teeth: 20, outerR: 1.4, rootR: 1.18, toothW: 0.22, holeR: 0.3 });
const extrudeSettings = {
  depth: 0.32,
  bevelEnabled: true,
  bevelSegments: 3,
  bevelSize: 0.04,
  bevelThickness: 0.04,
  curveSegments: 24,
};
const gearGeom = new THREE.ExtrudeGeometry(gearShape, extrudeSettings);
gearGeom.center();

const gearMat = new THREE.MeshStandardMaterial({
  color: 0xbfc7d1,
  metalness: 0.85,
  roughness: 0.28,
});
const gear = new THREE.Mesh(gearGeom, gearMat);
scene.add(gear);

/* Spokes carved via separate geometry: build a simpler hub overlay */
const hubGeom = new THREE.CylinderGeometry(0.38, 0.38, 0.5, 48);
const hubMat = new THREE.MeshStandardMaterial({
  color: 0xffb020,
  metalness: 0.6,
  roughness: 0.35,
  emissive: 0x3a2200,
  emissiveIntensity: 0.4,
});
const hub = new THREE.Mesh(hubGeom, hubMat);
hub.rotation.x = Math.PI / 2;
scene.add(hub);

/* Secondary smaller gear, slightly offset for depth */
const smallGearShape = buildGearShape({ teeth: 12, outerR: 0.75, rootR: 0.6, toothW: 0.22, holeR: 0.15 });
const smallGearGeom = new THREE.ExtrudeGeometry(smallGearShape, {
  depth: 0.22,
  bevelEnabled: true,
  bevelSegments: 2,
  bevelSize: 0.03,
  bevelThickness: 0.03,
  curveSegments: 20,
});
smallGearGeom.center();
const smallGearMat = new THREE.MeshStandardMaterial({
  color: 0x8b95a3,
  metalness: 0.9,
  roughness: 0.32,
});
const smallGear = new THREE.Mesh(smallGearGeom, smallGearMat);
smallGear.position.set(1.85, -0.6, -0.1);
smallGear.scale.setScalar(0.8);
scene.add(smallGear);

/* Wire-frame "ghost" gear for a technical drawing look */
const wireGeom = new THREE.EdgesGeometry(gearGeom, 20);
const wireMat = new THREE.LineBasicMaterial({ color: 0x7fd4ff, transparent: true, opacity: 0.18 });
const wire = new THREE.LineSegments(wireGeom, wireMat);
scene.add(wire);

/* =========================================================
   Interaction: drag to rotate + gentle mouse parallax
   ========================================================= */
const group = new THREE.Group();
scene.remove(gear, hub, wire);
group.add(gear, hub, wire);
scene.add(group);

let targetRotX = 0.25;
let targetRotY = -0.45;
let rotX = targetRotX;
let rotY = targetRotY;

let isDragging = false;
let dragStart = { x: 0, y: 0 };
let dragRot = { x: 0, y: 0 };

stage.addEventListener('pointerdown', (e) => {
  isDragging = true;
  dragStart = { x: e.clientX, y: e.clientY };
  dragRot = { x: targetRotX, y: targetRotY };
  stage.setPointerCapture(e.pointerId);
});
stage.addEventListener('pointermove', (e) => {
  if (isDragging) {
    const dx = (e.clientX - dragStart.x) / 200;
    const dy = (e.clientY - dragStart.y) / 200;
    targetRotY = dragRot.y + dx;
    targetRotX = dragRot.x + dy;
  } else {
    const rect = stage.getBoundingClientRect();
    const nx = (e.clientX - rect.left) / rect.width - 0.5;
    const ny = (e.clientY - rect.top) / rect.height - 0.5;
    targetRotY = -0.45 + nx * 0.4;
    targetRotX = 0.25 + ny * 0.3;
  }
});
stage.addEventListener('pointerup', () => { isDragging = false; });
stage.addEventListener('pointerleave', () => {
  if (!isDragging) {
    targetRotY = -0.45;
    targetRotX = 0.25;
  }
});

/* =========================================================
   Render loop
   ========================================================= */
function resize() {
  const rect = stage.getBoundingClientRect();
  const w = rect.width;
  const h = rect.height;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
const ro = new ResizeObserver(resize);
ro.observe(stage);
resize();

const clock = new THREE.Clock();
function render() {
  const t = clock.getElapsedTime();

  // Smooth orientation follow
  rotX += (targetRotX - rotX) * 0.08;
  rotY += (targetRotY - rotY) * 0.08;
  group.rotation.x = rotX;
  group.rotation.y = rotY;

  // Internal spin of the gears themselves (around their own Z axis)
  gear.rotation.z = t * 0.6;
  hub.rotation.y = t * 0.6;
  wire.rotation.z = t * 0.6;

  // Meshing ratio: teeth ratio is 20:12, so smallGear spins ~1.67x faster, opposite direction
  smallGear.rotation.z = -t * 0.6 * (20 / 12);

  renderer.render(scene, camera);
  requestAnimationFrame(render);
}
render();

/* =========================================================
   Nav link smooth scroll (light polish)
   ========================================================= */
document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (e) => {
    const id = link.getAttribute('href');
    if (id.length > 1) {
      const target = document.querySelector(id);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  });
});
