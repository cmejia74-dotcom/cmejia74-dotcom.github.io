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
   THREE.JS — fighter jet flight simulation
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

const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
camera.position.set(0, 0.8, 5.6);
camera.lookAt(0, 0, 0);

/* Lighting — warm key + cool rim, a bit more intense than the gear version */
const keyLight = new THREE.DirectionalLight(0xffd28a, 1.5);
keyLight.position.set(3, 4, 3);
scene.add(keyLight);

const rimLight = new THREE.DirectionalLight(0x7fd4ff, 1.3);
rimLight.position.set(-4, 2, -3);
scene.add(rimLight);

const fillLight = new THREE.DirectionalLight(0xffffff, 0.35);
fillLight.position.set(0, -3, 2);
scene.add(fillLight);

const ambient = new THREE.AmbientLight(0xffffff, 0.22);
scene.add(ambient);

/* =========================================================
   Build a stylized delta-wing fighter jet
   ========================================================= */
function buildJet() {
  const jet = new THREE.Group();

  const bodyMat = new THREE.MeshStandardMaterial({
    color: 0xb4bdc7,
    metalness: 0.82,
    roughness: 0.34,
  });
  const darkMat = new THREE.MeshStandardMaterial({
    color: 0x2a2f38,
    metalness: 0.5,
    roughness: 0.5,
  });
  const canopyMat = new THREE.MeshStandardMaterial({
    color: 0x0a1220,
    metalness: 0.2,
    roughness: 0.1,
    envMapIntensity: 1.0,
  });
  const glowMat = new THREE.MeshStandardMaterial({
    color: 0xffb020,
    emissive: 0xff5a20,
    emissiveIntensity: 2.4,
    roughness: 0.9,
  });

  /* Fuselage — long slender cylinder, oriented along +X (nose forward) */
  const fuseGeom = new THREE.CylinderGeometry(0.22, 0.26, 2.6, 20);
  const fuselage = new THREE.Mesh(fuseGeom, bodyMat);
  fuselage.rotation.z = Math.PI / 2;
  jet.add(fuselage);

  /* Nose cone */
  const noseGeom = new THREE.ConeGeometry(0.22, 0.8, 20);
  const nose = new THREE.Mesh(noseGeom, bodyMat);
  nose.rotation.z = -Math.PI / 2;
  nose.position.x = 1.7;
  jet.add(nose);

  /* Pitot tube tip */
  const pitotGeom = new THREE.CylinderGeometry(0.015, 0.015, 0.18, 8);
  const pitot = new THREE.Mesh(pitotGeom, darkMat);
  pitot.rotation.z = -Math.PI / 2;
  pitot.position.x = 2.18;
  jet.add(pitot);

  /* Engine exhaust ring */
  const tailGeom = new THREE.CylinderGeometry(0.24, 0.18, 0.36, 20);
  const tail = new THREE.Mesh(tailGeom, darkMat);
  tail.rotation.z = Math.PI / 2;
  tail.position.x = -1.5;
  jet.add(tail);

  /* Afterburner glow */
  const glowGeom = new THREE.CylinderGeometry(0.17, 0.14, 0.22, 18);
  const glow = new THREE.Mesh(glowGeom, glowMat);
  glow.rotation.z = Math.PI / 2;
  glow.position.x = -1.76;
  jet.add(glow);

  /* Delta wings — modeled as triangular extrusion, mirrored for L/R */
  const wingShape = new THREE.Shape();
  wingShape.moveTo(0.7, 0);
  wingShape.lineTo(-0.9, 0);
  wingShape.lineTo(-0.9, 1.55);
  wingShape.lineTo(0.1, 0.25);
  wingShape.closePath();

  const wingGeom = new THREE.ExtrudeGeometry(wingShape, {
    depth: 0.08,
    bevelEnabled: true,
    bevelSegments: 2,
    bevelSize: 0.02,
    bevelThickness: 0.02,
    curveSegments: 6,
  });

  const rightWing = new THREE.Mesh(wingGeom, bodyMat);
  rightWing.rotation.x = -Math.PI / 2;
  rightWing.position.set(-0.1, -0.02, 0.08);
  jet.add(rightWing);

  const leftWing = new THREE.Mesh(wingGeom, bodyMat);
  leftWing.rotation.x = -Math.PI / 2;
  leftWing.scale.z = -1;
  leftWing.position.set(-0.1, -0.02, -0.08);
  jet.add(leftWing);

  /* Horizontal stabilizers (smaller deltas) near the tail */
  const stabShape = new THREE.Shape();
  stabShape.moveTo(0.25, 0);
  stabShape.lineTo(-0.35, 0);
  stabShape.lineTo(-0.35, 0.55);
  stabShape.lineTo(-0.05, 0.12);
  stabShape.closePath();
  const stabGeom = new THREE.ExtrudeGeometry(stabShape, {
    depth: 0.05,
    bevelEnabled: true,
    bevelSegments: 1,
    bevelSize: 0.01,
    bevelThickness: 0.01,
  });

  const rightStab = new THREE.Mesh(stabGeom, bodyMat);
  rightStab.rotation.x = -Math.PI / 2;
  rightStab.position.set(-1.25, -0.02, 0.1);
  jet.add(rightStab);

  const leftStab = new THREE.Mesh(stabGeom, bodyMat);
  leftStab.rotation.x = -Math.PI / 2;
  leftStab.scale.z = -1;
  leftStab.position.set(-1.25, -0.02, -0.1);
  jet.add(leftStab);

  /* Vertical tail fin */
  const finShape = new THREE.Shape();
  finShape.moveTo(-1.35, 0);
  finShape.lineTo(-0.4, 0);
  finShape.lineTo(-0.95, 0.8);
  finShape.lineTo(-1.35, 0.8);
  finShape.closePath();
  const finGeom = new THREE.ExtrudeGeometry(finShape, {
    depth: 0.05,
    bevelEnabled: true,
    bevelSegments: 1,
    bevelSize: 0.01,
    bevelThickness: 0.01,
  });
  const fin = new THREE.Mesh(finGeom, bodyMat);
  fin.position.set(0, 0.16, -0.025);
  jet.add(fin);

  /* Canopy — stretched half-sphere */
  const canopyGeom = new THREE.SphereGeometry(
    0.22, 20, 14, 0, Math.PI * 2, 0, Math.PI / 2
  );
  const canopy = new THREE.Mesh(canopyGeom, canopyMat);
  canopy.position.set(0.55, 0.22, 0);
  canopy.scale.set(1.8, 0.7, 1.1);
  jet.add(canopy);

  /* Wireframe overlay for a technical-drawing vibe */
  const overlayGeom = new THREE.EdgesGeometry(wingGeom, 15);
  const overlayMat = new THREE.LineBasicMaterial({
    color: 0x7fd4ff,
    transparent: true,
    opacity: 0.14,
  });
  const overlayR = new THREE.LineSegments(overlayGeom, overlayMat);
  overlayR.rotation.copy(rightWing.rotation);
  overlayR.position.copy(rightWing.position);
  jet.add(overlayR);
  const overlayL = new THREE.LineSegments(overlayGeom, overlayMat.clone());
  overlayL.rotation.copy(leftWing.rotation);
  overlayL.scale.z = -1;
  overlayL.position.copy(leftWing.position);
  jet.add(overlayL);

  /* Reference points used for contrails + animation hooks */
  jet.userData.leftTipLocal = new THREE.Vector3(-0.9, 0, -1.5);
  jet.userData.rightTipLocal = new THREE.Vector3(-0.9, 0, 1.5);
  jet.userData.glowLocal = new THREE.Vector3(-1.9, 0, 0);
  jet.userData.afterburner = glow;

  return jet;
}

const jet = buildJet();

/* =========================================================
   Scene graph:
   scene
     └─ viewGroup (user drag orbit)
         ├─ trails (emitted in viewGroup-space; curve naturally as jet banks)
         └─ jetRig (gentle bob + banking animation)
             └─ jet
   ========================================================= */
const viewGroup = new THREE.Group();
scene.add(viewGroup);

const jetRig = new THREE.Group();
viewGroup.add(jetRig);
jetRig.add(jet);

/* =========================================================
   Contrails — two Line strips, one per wingtip, plus an exhaust streak
   Colors fade from white to dim to simulate dissipation
   ========================================================= */
const TRAIL_LEN = 90;

function makeTrail(color = 0xffffff, baseOpacity = 0.75) {
  const positions = new Float32Array(TRAIL_LEN * 3);
  const colors = new Float32Array(TRAIL_LEN * 3);
  const baseColor = new THREE.Color(color);
  for (let i = 0; i < TRAIL_LEN; i++) {
    // head (index 0) is brightest; tail fades to black (which reads as transparent on dark bg)
    const a = 1 - i / TRAIL_LEN;
    colors[i * 3 + 0] = baseColor.r * a * a;
    colors[i * 3 + 1] = baseColor.g * a * a;
    colors[i * 3 + 2] = baseColor.b * a * a;
  }
  const geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geom.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  const mat = new THREE.LineBasicMaterial({
    vertexColors: true,
    transparent: true,
    opacity: baseOpacity,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });
  return new THREE.Line(geom, mat);
}

const trailL = makeTrail(0xffffff, 0.6);
const trailR = makeTrail(0xffffff, 0.6);
const trailE = makeTrail(0xffb020, 0.8);
viewGroup.add(trailL, trailR, trailE);

/* Update a trail: drift every existing point backward (simulating the jet's
   airspeed carrying the exhaust away), shift indices by one, then stamp the
   current wingtip at the head. This creates proper streaming contrails even
   though the jet itself stays visually at the origin. */
function updateTrail(trail, headPointViewLocal, forwardViewLocal, drift) {
  const pos = trail.geometry.attributes.position;
  const arr = pos.array;
  const dx = -forwardViewLocal.x * drift;
  const dy = -forwardViewLocal.y * drift;
  const dz = -forwardViewLocal.z * drift;
  for (let i = TRAIL_LEN - 1; i > 0; i--) {
    arr[i * 3 + 0] = arr[(i - 1) * 3 + 0] + dx;
    arr[i * 3 + 1] = arr[(i - 1) * 3 + 1] + dy;
    arr[i * 3 + 2] = arr[(i - 1) * 3 + 2] + dz;
  }
  arr[0] = headPointViewLocal.x;
  arr[1] = headPointViewLocal.y;
  arr[2] = headPointViewLocal.z;
  pos.needsUpdate = true;
}

/* Prime trails so they start as a straight tail receding behind the jet */
function primeTrail(trail, headViewLocal, forwardViewLocal, drift) {
  const pos = trail.geometry.attributes.position;
  const arr = pos.array;
  for (let i = 0; i < TRAIL_LEN; i++) {
    arr[i * 3 + 0] = headViewLocal.x - forwardViewLocal.x * drift * i;
    arr[i * 3 + 1] = headViewLocal.y - forwardViewLocal.y * drift * i;
    arr[i * 3 + 2] = headViewLocal.z - forwardViewLocal.z * drift * i;
  }
  pos.needsUpdate = true;
}

const AIRSPEED = 0.08; // viewGroup units per frame
{
  const head = new THREE.Vector3();
  const forward = new THREE.Vector3(1, 0, 0); // jet points +X at t=0
  jet.updateMatrixWorld(true);

  jet.localToWorld(head.copy(jet.userData.leftTipLocal));
  viewGroup.worldToLocal(head);
  primeTrail(trailL, head, forward, AIRSPEED);

  jet.localToWorld(head.copy(jet.userData.rightTipLocal));
  viewGroup.worldToLocal(head);
  primeTrail(trailR, head, forward, AIRSPEED);

  jet.localToWorld(head.copy(jet.userData.glowLocal));
  viewGroup.worldToLocal(head);
  primeTrail(trailE, head, forward, AIRSPEED);
}

/* =========================================================
   Interaction: drag to orbit + gentle mouse parallax
   ========================================================= */
let targetRotX = 0.15;
let targetRotY = -0.25;
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
    targetRotY = -0.25 + nx * 0.35;
    targetRotX = 0.15 + ny * 0.25;
  }
});
stage.addEventListener('pointerup', () => { isDragging = false; });
stage.addEventListener('pointerleave', () => {
  if (!isDragging) {
    targetRotY = -0.25;
    targetRotX = 0.15;
  }
});

/* =========================================================
   Render loop — flight sim + camera orbit + contrails
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

const _tmpV = new THREE.Vector3();
const _fwd = new THREE.Vector3();
const clock = new THREE.Clock();

function render() {
  const t = clock.getElapsedTime();

  // User orbit follow
  rotX += (targetRotX - rotX) * 0.08;
  rotY += (targetRotY - rotY) * 0.08;
  viewGroup.rotation.x = rotX;
  viewGroup.rotation.y = rotY;

  // Flight simulation — gentle figure-8 heading with banking
  // Fuselage points +X, so: yaw = rot.y, pitch = rot.z, roll = rot.x
  const yaw = Math.sin(t * 0.45) * 0.55;
  const yawRate = Math.cos(t * 0.45) * 0.45 * 0.55;
  const bankRoll = yawRate * 1.8;                  // bank into the turn
  const pitch = Math.sin(t * 0.7) * 0.08;          // gentle nose-up/down
  const bobY = Math.sin(t * 1.0) * 0.05;

  jetRig.rotation.y = yaw;                         // heading
  jetRig.rotation.z = pitch;                       // pitch
  jet.rotation.x = bankRoll;                       // bank (local roll along body +X)
  jetRig.position.y = bobY;

  // Afterburner flicker
  const ab = jet.userData.afterburner;
  if (ab) ab.material.emissiveIntensity = 2.1 + Math.sin(t * 18) * 0.4 + Math.random() * 0.15;

  // Contrails — compute the jet's forward axis in viewGroup-local coords so
  // old trail points drift backward along the body's velocity vector.
  jet.updateMatrixWorld(true);
  _fwd.set(1, 0, 0).applyQuaternion(jetRig.quaternion).normalize();

  jet.localToWorld(_tmpV.copy(jet.userData.leftTipLocal));
  viewGroup.worldToLocal(_tmpV);
  updateTrail(trailL, _tmpV, _fwd, AIRSPEED);

  jet.localToWorld(_tmpV.copy(jet.userData.rightTipLocal));
  viewGroup.worldToLocal(_tmpV);
  updateTrail(trailR, _tmpV, _fwd, AIRSPEED);

  jet.localToWorld(_tmpV.copy(jet.userData.glowLocal));
  viewGroup.worldToLocal(_tmpV);
  updateTrail(trailE, _tmpV, _fwd, AIRSPEED);

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
