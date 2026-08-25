// Exoplanet presets from planets.csv
const PLANET_PRESETS = {
  "Earth": { luminosity: 1.0, distance: 1.0, radius: 1.0, mass: 1.0, density: 1.0, eccentricity: 0.017, albedo: 0.30 },
  "Kepler-186f": { luminosity: 0.0412, distance: 0.432, radius: 1.17, mass: 1.71, density: 1.07, eccentricity: 0.04, albedo: 0.30 },
  "Proxima Centauri b": { luminosity: 0.00155, distance: 0.0485, radius: 1.03, mass: 1.17, density: 1.07, eccentricity: 0.11, albedo: 0.30 },
  "TRAPPIST-1e": { luminosity: 0.000553, distance: 0.0293, radius: 0.92, mass: 0.69, density: 0.89, eccentricity: 0.008, albedo: 0.30 },
  "Kepler-22b": { luminosity: 0.79, distance: 0.849, radius: 2.38, mass: 9.1, density: 0.67, eccentricity: 0.0, albedo: 0.30 },
  "HD 209458 b": { luminosity: 1.61, distance: 0.0475, radius: 15.5, mass: 219.0, density: 0.06, eccentricity: 0.0, albedo: 0.10 },
  "Kepler-452b": { luminosity: 1.2, distance: 1.046, radius: 1.63, mass: 5.0, density: 1.15, eccentricity: 0.035, albedo: 0.30 },
  "WASP-12b": { luminosity: 2.1, distance: 0.0229, radius: 21.3, mass: 467.0, density: 0.05, eccentricity: 0.0, albedo: 0.06 },
  "Gliese 667 C c": { luminosity: 0.0137, distance: 0.125, radius: 1.54, mass: 3.8, density: 1.04, eccentricity: 0.27, albedo: 0.30 },
  "TOI-700 d": { luminosity: 0.023, distance: 0.163, radius: 1.14, mass: 1.72, density: 1.16, eccentricity: 0.03, albedo: 0.30 }
};

// Setup greenhouse warming function
function estimateGreenhouseWarming(massEarth, radiusEarth, tEqKelvin) {
  if (radiusEarth <= 0) return 0;
  const surfaceGravity = massEarth / (radiusEarth * radiusEarth);
  let atmoFactor = 0.1;
  if (radiusEarth < 0.5 || surfaceGravity < 0.2) {
    atmoFactor = 0.1;
  } else if (radiusEarth <= 1.6) {
    atmoFactor = (surfaceGravity * 0.6) + (radiusEarth * 0.4);
  } else {
    atmoFactor = 3.5 * Math.pow(radiusEarth / 1.6, 1.5);
  }
  const fluxScaling = Math.pow(tEqKelvin / 255.0, 0.5);
  const deltaT = 33.3 * atmoFactor * fluxScaling;
  return Math.round(deltaT * 10) / 10;
}

// DOM elements
const selectPreset = document.getElementById("planet-select");
const inputStarLum = document.getElementById("star-lum");
const inputPlanetDist = document.getElementById("planet-dist");
const inputPlanetRadius = document.getElementById("planet-radius");
const inputPlanetMass = document.getElementById("planet-mass");
const inputEccentricity = document.getElementById("eccentricity");
const inputAlbedo = document.getElementById("albedo");

const valStarLum = document.getElementById("val-star-lum");
const valPlanetDist = document.getElementById("val-planet-dist");
const valPlanetRadius = document.getElementById("val-planet-radius");
const valPlanetMass = document.getElementById("val-planet-mass");
const valEccentricity = document.getElementById("val-eccentricity");
const valAlbedo = document.getElementById("val-albedo");

const verdictContainer = document.getElementById("verdict-container");
const verdictIcon = document.getElementById("verdict-icon");
const verdictTitle = document.getElementById("verdict-title");
const verdictDesc = document.getElementById("verdict-desc");

const statTemp = document.getElementById("stat-temp");
const tempProgress = document.getElementById("temp-progress");
const statHzRange = document.getElementById("stat-hz-range");
const statHzPosition = document.getElementById("stat-hz-position");
const statEnergy = document.getElementById("stat-energy");
const statComposition = document.getElementById("stat-composition");
const statCompositionDesc = document.getElementById("stat-composition-desc");
const statEsiGlobal = document.getElementById("stat-esi-global");
const statEsiBreakdown = document.getElementById("stat-esi-breakdown");
const statPeriod = document.getElementById("stat-period");
const statPeriodYears = document.getElementById("stat-period-years");

const toggleAnimBtn = document.getElementById("toggle-orbit-anim");
const canvas = document.getElementById("orbit-canvas");
const ctx = canvas.getContext("2d");

// Interactive variables
let isRunning = true;
let orbitAngle = 0;
let lastTime = 0;

// Setup canvas size
function resizeCanvas() {
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * window.devicePixelRatio;
  canvas.height = rect.height * window.devicePixelRatio;
  ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
}
window.addEventListener("resize", resizeCanvas);
resizeCanvas();

// Populate / update values
function updateUI() {
  const L = parseFloat(inputStarLum.value);
  const d = parseFloat(inputPlanetDist.value);
  const r = parseFloat(inputPlanetRadius.value);
  const m = parseFloat(inputPlanetMass.value);
  const e = parseFloat(inputEccentricity.value);
  const albedo = parseFloat(inputAlbedo.value);

  // Update slider label values
  valStarLum.innerText = L.toFixed(4);
  valPlanetDist.innerText = d.toFixed(3);
  valPlanetRadius.innerText = r.toFixed(2);
  valPlanetMass.innerText = m.toFixed(2);
  valEccentricity.innerText = e.toFixed(3);
  valAlbedo.innerText = albedo.toFixed(2);

  // 1. Calculations
  const energyReceived = L / (d * d);
  const innerEdge = Math.sqrt(L / 1.11);
  const outerEdge = Math.sqrt(L / 0.36);

  const inHZ = d >= innerEdge && d <= outerEdge;
  const isRocky = r >= 0.5 && r <= 1.6;

  // Temperature estimation: Temp_kelvin = 278.5 * ((energy * (1 - albedo))^0.25) + greenhouse warming
  const tEqKelvin = 278.5 * Math.pow(energyReceived * (1 - albedo), 0.25);
  const deltaT = estimateGreenhouseWarming(m, r, tEqKelvin);
  const tempKelvin = tEqKelvin + deltaT;
  const tempCelsius = tempKelvin - 273.15;

  // 2. Verdict & Styling Update
  verdictContainer.className = "verdict-card"; // reset classes
  if (inHZ && isRocky) {
    verdictContainer.classList.add("habitable");
    verdictIcon.innerText = "❇️";
    verdictTitle.innerText = "POTENTIALLY HABITABLE";
    verdictDesc.innerText = `A rocky planet (${r} R⊕) within the Goldilocks zone. Temperatures average ${tempCelsius.toFixed(1)}°C, allowing liquid surface water.`;
  } else if (inHZ) {
    verdictContainer.classList.add("partially-habitable");
    verdictIcon.innerText = "💨";
    verdictTitle.innerText = "GAS GIANT IN HABITABLE ZONE";
    verdictDesc.innerText = `Orbiting in the right zone, but the planet is too large (${r} R⊕) and likely lacks a solid surface. Could host habitable moons.`;
  } else {
    verdictContainer.classList.add("not-habitable");
    if (d < innerEdge) {
      verdictIcon.innerText = "🔥";
      verdictTitle.innerText = "TOO HOT FOR LIFE";
      verdictDesc.innerText = `Orbiting too close to the star. Extreme solar radiation drives temperature to a scorching ${tempCelsius.toFixed(1)}°C.`;
    } else {
      verdictIcon.innerText = "❄️";
      verdictTitle.innerText = "TOO COLD FOR LIFE";
      verdictDesc.innerText = `Orbiting too far out. Extremely low solar flux results in a deep freeze of ${tempCelsius.toFixed(1)}°C.`;
    }
  }

  // 3. Update stats card
  statTemp.innerText = `${tempCelsius.toFixed(1)} °C`;
  // Temperature progress visual: map -100°C to 100°C to 0% to 100%
  const tempPct = Math.min(Math.max(((tempCelsius + 100) / 200) * 100, 0), 100);
  tempProgress.style.width = `${tempPct}%`;
  if (tempCelsius < 0) {
    tempProgress.style.backgroundColor = "#3b82f6"; // Blue
  } else if (tempCelsius > 45) {
    tempProgress.style.backgroundColor = "#ef4444"; // Red
  } else {
    tempProgress.style.backgroundColor = "#22c55e"; // Green (safe)
  }

  statHzRange.innerText = `${innerEdge.toFixed(3)} to ${outerEdge.toFixed(3)} AU`;
  if (d < innerEdge) {
    statHzPosition.innerText = "Inside the inner limit (too hot)";
    statHzPosition.style.color = "#ef4444";
  } else if (d > outerEdge) {
    statHzPosition.innerText = "Outside the outer limit (too cold)";
    statHzPosition.style.color = "#3b82f6";
  } else {
    statHzPosition.innerText = "Perfectly inside the habitable zone!";
    statHzPosition.style.color = "#22c55e";
  }

  statEnergy.innerText = `${energyReceived.toFixed(2)}x Earth's`;

  // Planetary composition
  if (r < 0.5) {
    statComposition.innerText = "Sub-Earth (Rocky / Ice)";
    statCompositionDesc.innerText = `Very light planet (${m} M⊕). Might struggle to retain an atmosphere.`;
  } else if (r <= 1.6) {
    statComposition.innerText = "Terrestrial (Rocky)";
    statCompositionDesc.innerText = `Standard rocky planet composition, similar to Earth.`;
  } else if (r <= 2.5) {
    statComposition.innerText = "Super-Earth / Mini-Neptune";
    statCompositionDesc.innerText = `Thick atmosphere, potentially a global deep ocean or gaseous envelop.`;
  } else {
    statComposition.innerText = "Gas Giant / Jovian";
    statCompositionDesc.innerText = `Massive world (${m} M⊕) dominated by hydrogen and helium gas.`;
  }

  // Dynamic calculations for ESI and Orbital Period
  const density = r > 0 ? (m / Math.pow(r, 3)) : 0.0;
  const escapeVel = r > 0 ? Math.sqrt(m / r) : 0.0;
  const starMass = Math.pow(L, 0.25); // M_star estimated as L^0.25

  // Individual similarity sub-scores
  const esiR = Math.pow(1 - Math.abs((r - 1.0) / (r + 1.0)), 0.57);
  const esiD = Math.pow(1 - Math.abs((density - 1.0) / (density + 1.0)), 1.07);
  const esiV = Math.pow(1 - Math.abs((escapeVel - 1.0) / (escapeVel + 1.0)), 0.70);
  const esiT = Math.pow(1 - Math.abs((tempKelvin - 288.0) / (tempKelvin + 288.0)), 5.58);

  const interiorEsi = Math.sqrt(esiR * esiD);
  const surfaceEsi = Math.sqrt(esiV * esiT);
  const globalEsi = Math.sqrt(interiorEsi * surfaceEsi);

  // Kepler's 3rd Law: T = sqrt(a^3 / M_star)
  let periodYears = 0.0;
  if (starMass > 0 && d > 0) {
    periodYears = Math.sqrt(Math.pow(d, 3) / starMass);
  }
  const periodDays = periodYears * 365.25;

  // Render to UI
  statEsiGlobal.innerText = isNaN(globalEsi) ? "0.000" : globalEsi.toFixed(3);
  statEsiBreakdown.innerText = `Interior: ${isNaN(interiorEsi) ? "0.000" : interiorEsi.toFixed(3)} | Surface: ${isNaN(surfaceEsi) ? "0.000" : surfaceEsi.toFixed(3)}`;

  statPeriod.innerText = `${periodDays.toFixed(1)} days`;
  statPeriodYears.innerText = `${periodYears.toFixed(2)} Earth years`;
}

// Preset selection hook
selectPreset.addEventListener("change", (e) => {
  const planetName = e.target.value;
  if (planetName && PLANET_PRESETS[planetName]) {
    const data = PLANET_PRESETS[planetName];
    inputStarLum.value = data.luminosity;
    inputPlanetDist.value = data.distance;
    inputPlanetRadius.value = data.radius;
    inputPlanetMass.value = data.mass;
    inputEccentricity.value = data.eccentricity;
    inputAlbedo.value = data.albedo;
    updateUI();
  }
});

// Slider inputs hook (forces custom Sandbox mode)
const inputs = [inputStarLum, inputPlanetDist, inputPlanetRadius, inputPlanetMass, inputEccentricity, inputAlbedo];
inputs.forEach(input => {
  input.addEventListener("input", () => {
    selectPreset.value = "custom";
    updateUI();
  });
});

// Pause / Resume animation
toggleAnimBtn.addEventListener("click", () => {
  isRunning = !isRunning;
  toggleAnimBtn.innerText = isRunning ? "Pause Animation" : "Resume Animation";
});

// Render 2D Orbit Visualization Loop
function drawScene(timestamp) {
  if (!lastTime) lastTime = timestamp;
  const elapsed = timestamp - lastTime;
  lastTime = timestamp;

  // Fetch current values
  const L = parseFloat(inputStarLum.value);
  const d = parseFloat(inputPlanetDist.value);
  const r = parseFloat(inputPlanetRadius.value);
  const m = parseFloat(inputPlanetMass.value);
  const e = parseFloat(inputEccentricity.value);
  const albedo = parseFloat(inputAlbedo.value);

  const innerEdge = Math.sqrt(L / 1.11);
  const outerEdge = Math.sqrt(L / 0.36);

  // Clear Canvas
  const width = canvas.width / window.devicePixelRatio;
  const height = canvas.height / window.devicePixelRatio;
  ctx.clearRect(0, 0, width, height);

  // Coordinate setup: center of the screen
  const cx = width / 2;
  const cy = height / 2;

  // Scale: Auto-scale system size or apply manual zoom factor
  const zoomSelect = document.getElementById("zoom-select");
  const zoomValue = zoomSelect ? zoomSelect.value : "auto";
  
  const maxSimDist = Math.max(d * (1 + e), outerEdge, 1.5);
  const baseScale = (Math.min(width, height) / 2) * 0.8;
  
  let scale = baseScale / maxSimDist; // Pixels per AU (default Auto Fit)
  
  if (zoomValue === "1x") {
    scale = baseScale / 4.0; // Fixed scale for 4.0 AU max limit
  } else if (zoomValue === "5x") {
    scale = (baseScale / 4.0) * 5;
  } else if (zoomValue === "10x") {
    scale = (baseScale / 4.0) * 10;
  } else if (zoomValue === "50x") {
    scale = (baseScale / 4.0) * 50;
  }

  // 1. Draw Goldilocks boundaries (HZ)
  // Inner limit (Red zone boundary)
  ctx.fillStyle = "rgba(239, 68, 68, 0.05)";
  ctx.beginPath();
  ctx.arc(cx, cy, innerEdge * scale, 0, Math.PI * 2);
  ctx.fill();

  // Habitable Zone (Green zone ring)
  ctx.fillStyle = "rgba(34, 197, 94, 0.12)";
  ctx.beginPath();
  ctx.arc(cx, cy, outerEdge * scale, 0, Math.PI * 2);
  ctx.arc(cx, cy, innerEdge * scale, 0, Math.PI * 2, true); // counterclockwise to hollow inner part
  ctx.fill();

  // Draw HZ boundaries as thin circles
  ctx.strokeStyle = "rgba(34, 197, 94, 0.25)";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.arc(cx, cy, innerEdge * scale, 0, Math.PI * 2);
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(cx, cy, outerEdge * scale, 0, Math.PI * 2);
  ctx.stroke();

  // 2. Draw Orbit Ellipse
  // Semimajor axis 'a' is planet distance (d) in AU.
  // Semiminor axis 'b' = a * sqrt(1 - e^2)
  const a = d * scale;
  const b = d * Math.sqrt(1 - e * e) * scale;
  // Focus offset due to eccentricity: c = a * e
  const c = a * e;

  ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
  ctx.lineWidth = 1.5;
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  // Drawing elliptical orbit with the star located at one focus (cx, cy)
  // So the center of the ellipse is at (cx - c, cy)
  ctx.ellipse(cx - c, cy, a, b, 0, 0, Math.PI * 2);
  ctx.stroke();
  ctx.setLineDash([]); // Reset dash

  // 3. Draw Center Star
  // Star size depends on luminosity
  const starRadius = Math.max(8, Math.min(45, 12 * Math.pow(L, 0.3)));
  const starGlow = ctx.createRadialGradient(cx, cy, 2, cx, cy, starRadius * 2);
  
  // Decide star color based on luminosity (M-dwarf is reddish/orange, Sun is white/yellow, bright is blueish)
  let starColor = "#f59e0b"; // Yellow/Orange
  let glowColor = "rgba(245, 158, 11, 0.3)";
  if (L < 0.05) {
    starColor = "#ef4444"; // Red M-dwarf
    glowColor = "rgba(239, 68, 68, 0.4)";
  } else if (L > 1.5) {
    starColor = "#38bdf8"; // Bright sky blue star
    glowColor = "rgba(56, 189, 248, 0.4)";
  }
  
  starGlow.addColorStop(0, "#fff");
  starGlow.addColorStop(0.3, starColor);
  starGlow.addColorStop(1, "transparent");

  ctx.fillStyle = starGlow;
  ctx.beginPath();
  ctx.arc(cx, cy, starRadius * 2, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = "#fff";
  ctx.beginPath();
  ctx.arc(cx, cy, starRadius * 0.7, 0, Math.PI * 2);
  ctx.fill();

  // 4. Update and Draw Planet
  if (isRunning) {
    // Visually, closer planets are slowed down to prevent stroboscopic/excessive speed effects
    const speed = 0.001 * elapsed * Math.sqrt(d);
    orbitAngle += speed;
  }

  // Position on the ellipse relative to the center of the ellipse (cx - c, cy)
  // To draw correctly with respect to the focus at (cx, cy):
  const px = cx - c + a * Math.cos(orbitAngle);
  const py = cy + b * Math.sin(orbitAngle);

  // Planet color based on temperature and composition
  // Calculate temperature kelvin (including dynamic greenhouse effect)
  const energyReceived = L / (d * d);
  const tEqKelvin = 278.5 * Math.pow(energyReceived * (1 - albedo), 0.25);
  const deltaT = estimateGreenhouseWarming(m, r, tEqKelvin);
  const tempKelvin = tEqKelvin + deltaT;
  const tempC = tempKelvin - 273.15;

  let planetColor = "#3b82f6"; // default Earth Blue
  if (r > 2.5) {
    planetColor = "#f97316"; // Gaseous Orange
  } else if (tempC > 50) {
    planetColor = "#e11d48"; // Hot Desert / Venus Red
  } else if (tempC < -20) {
    planetColor = "#e2e8f0"; // Frozen Ice World White
  } else if (r >= 0.5 && r <= 1.6) {
    planetColor = "#22c55e"; // Habitable Green/Blue
  }

  // Planet radius size scaled down so it fits
  const planetDrawRadius = Math.max(3, Math.min(25, 4 + Math.pow(r, 0.4) * 2));

  // Draw planet glow
  const planetGlow = ctx.createRadialGradient(px, py, 1, px, py, planetDrawRadius * 1.5);
  planetGlow.addColorStop(0, "#fff");
  planetGlow.addColorStop(0.4, planetColor);
  planetGlow.addColorStop(1, "transparent");

  ctx.fillStyle = planetGlow;
  ctx.beginPath();
  ctx.arc(px, py, planetDrawRadius * 1.8, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = planetColor;
  ctx.beginPath();
  ctx.arc(px, py, planetDrawRadius, 0, Math.PI * 2);
  ctx.fill();

  // Draw a subtle orbit pointer / indicator line from star to planet
  ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(cx, cy);
  ctx.lineTo(px, py);
  ctx.stroke();

  requestAnimationFrame(drawScene);
}

// Initial trigger
updateUI();
requestAnimationFrame(drawScene);
