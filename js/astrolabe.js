/**
 * Classical Islamic Astrolabe - Interactive Graphics & Viewport Engine
 * معالجة طبقات المتجهات، التحريك السلس، الزووم واللمس المتعدد
 */

// Viewport Pan & Zoom state
let currentZoom = 1.0;
let panX = 0;
let panY = 0;
let isSpacePressed = false;
let isPointerDown = false;
window.isPointerDown = false;
let isMultiTouchPinch = false;
let lastPointerX = 0;
let lastPointerY = 0;
let lastPointerAngle = 0;
let initialPinchDist = 0;
let initialPinchZoom = 1.0;
let lastPinchMidX = 0;
let lastPinchMidY = 0;

/* ==================== VIEWPORT PAN & ZOOM ENGINE ==================== */
function applyViewportTransform() {
  const viewport = document.getElementById('astrolabe-viewport');
  if (!viewport) return;
  viewport.style.transform = `translate(${panX}px, ${panY}px) scale(${currentZoom})`;
  viewport.style.willChange = 'auto';
  const pct = Math.round(currentZoom * 100);
  const badge = document.getElementById('dock-zoom-badge');
  if (badge) badge.innerText = `${pct}%`;
  const txtZ = document.getElementById('txt-zoom');
  if (txtZ) txtZ.innerText = `${pct}%`;
  const sliderZ = document.getElementById('slider-zoom');
  if (sliderZ) sliderZ.value = pct;
}

function setZoom(val, centerX = null, centerY = null) {
  const workspace = document.getElementById('workspace');
  if (!workspace) return;
  const prevZoom = currentZoom;
  currentZoom = Math.max(0.70, Math.min(5.50, val));

  // Zoom toward specific screen coordinate if provided
  if (centerX !== null && centerY !== null) {
    const rect = workspace.getBoundingClientRect();
    const wsX = centerX - rect.left - rect.width / 2;
    const wsY = centerY - rect.top - rect.height / 2;
    panX = wsX - (wsX - panX) * (currentZoom / prevZoom);
    panY = wsY - (wsY - panY) * (currentZoom / prevZoom);
  }
  applyViewportTransform();
}

function zoomBy(delta) {
  setZoom(currentZoom + delta);
}

function resetView() {
  currentZoom = 1.0;
  panX = 0;
  panY = 0;
  applyViewportTransform();
}

/* ==================== LAYER ROTATIONS & POSITIONING ==================== */
function updateSunOnEcliptic() {
  const doy = window.dayOfYear || 80;
  const { sunDecRad, sunRA } = AstroMath.computeSunCoords(doy);
  const rSun = Math.tan((Math.PI / 2.0 - sunDecRad) / 2.0);
  const xMath = rSun * Math.cos(sunRA);
  const yMath = rSun * Math.sin(sunRA);

  const cxSvg = 284.4;
  const cySvg = 284.4;
  const scale = 125.4813;
  const xSvg = cxSvg + xMath * scale;
  const ySvg = cySvg - yMath * scale;

  const group = document.getElementById('sun-marker-group');
  if (group) {
    group.setAttribute('transform', `translate(${xSvg - cxSvg}, ${ySvg - cySvg})`);
  }
}

function setReteAngleSmooth(deg, animate = false) {
  const normalized = (deg % 360 + 360) % 360;
  window.reteAngle = normalized;
  const layer = document.getElementById('rete-layer');
  const eclipticLayer = document.getElementById('ecliptic-layer');
  const sunLayer = document.getElementById('sun-layer');
  if (!layer) return;

  if (animate) {
    layer.style.transition = 'transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)';
    if (eclipticLayer) eclipticLayer.style.transition = 'transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)';
    if (sunLayer) sunLayer.style.transition = 'transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)';
    setTimeout(() => {
      layer.style.transition = '';
      if (eclipticLayer) eclipticLayer.style.transition = '';
      if (sunLayer) sunLayer.style.transition = '';
    }, 450);
  }
  layer.style.transform = `rotate(${window.reteAngle}deg)`;
  if (eclipticLayer) eclipticLayer.style.transform = `rotate(${window.reteAngle}deg)`;
  if (sunLayer) sunLayer.style.transform = `rotate(${window.reteAngle}deg)`;
}

function setRuleAngleSmooth(deg, animate = false) {
  const normalized = (deg % 360 + 360) % 360;
  window.ruleAngle = normalized;
  const layer = document.getElementById('rule-layer');
  if (!layer) return;

  if (animate) {
    layer.style.transition = 'transform 0.35s cubic-bezier(0.16, 1, 0.3, 1)';
    setTimeout(() => { layer.style.transition = ''; }, 400);
  }
  layer.style.transform = `rotate(${window.ruleAngle}deg)`;
}

function setAlidadeAngleSmooth(deg, animate = false) {
  const normalized = (deg % 360 + 360) % 360;
  window.alidadeAngle = normalized;
  const layer = document.getElementById('alidade-layer');
  if (!layer) return;

  if (animate) {
    layer.style.transition = 'transform 0.35s cubic-bezier(0.16, 1, 0.3, 1)';
    setTimeout(() => { layer.style.transition = ''; }, 400);
  }
  layer.style.transform = `rotate(${window.alidadeAngle}deg)`;
}

function setLayerFilter(mode) {
  window.layerFilter = mode;
  document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
  const activeBtn = document.getElementById('filter-' + mode);
  if (activeBtn) activeBtn.classList.add('active');

  const plate = document.getElementById('plate-layer');
  const rete = document.getElementById('rete-layer');
  const ecliptic = document.getElementById('ecliptic-layer');
  const sun = document.getElementById('sun-layer');
  const rule = document.getElementById('rule-layer');

  if (!plate || !rete || !sun || !rule) return;

  if (mode === 'all') {
    plate.style.opacity = '1.0';
    rete.style.opacity = '1.0';
    if (ecliptic) ecliptic.style.opacity = '0.0';
    sun.style.opacity = '1.0';
    rule.style.opacity = '1.0';
  } else if (mode === 'stars') {
    plate.style.opacity = '0.015';
    rete.style.opacity = '1.0';
    if (ecliptic) ecliptic.style.opacity = '0.0';
    sun.style.opacity = '1.0';
    rule.style.opacity = '0.015';
  } else if (mode === 'grid') {
    plate.style.opacity = '1.0';
    rete.style.opacity = '0.015';
    if (ecliptic) ecliptic.style.opacity = '0.015';
    sun.style.opacity = '0.015';
    rule.style.opacity = '0.015';
  } else if (mode === 'prayers') {
    plate.style.opacity = '1.0';
    rete.style.opacity = '0.015';
    if (ecliptic) ecliptic.style.opacity = '1.0';
    sun.style.opacity = '1.0';
    rule.style.opacity = '1.0';
  }
}

/* ==================== INTERACTION GESTURES (TOUCH, WHEEL, SPACEBAR) ==================== */
function getPointerCenterAngle(clientX, clientY) {
  const viewport = document.getElementById('astrolabe-viewport');
  if (!viewport) return 0;
  const rect = viewport.getBoundingClientRect();
  const cx = rect.left + rect.width / 2;
  const cy = rect.top + rect.height / 2;
  return Math.atan2(clientY - cy, clientX - cx) * 180 / Math.PI;
}

function getTouchDistance(t1, t2) {
  const dx = t2.clientX - t1.clientX;
  const dy = t2.clientY - t1.clientY;
  return Math.hypot(dx, dy);
}

function getTouchMidpoint(t1, t2) {
  return {
    x: (t1.clientX + t2.clientX) / 2,
    y: (t1.clientY + t2.clientY) / 2
  };
}

function initAstrolabeInteractions() {
  const workspace = document.getElementById('workspace');
  if (!workspace) return;

  // Mouse Wheel Zoom
  workspace.addEventListener('wheel', e => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.15 : 0.87;
    setZoom(currentZoom * zoomFactor, e.clientX, e.clientY);
  }, { passive: false });

  // Mouse Drag Events
  workspace.addEventListener('mousedown', e => {
    if (window.isMenuOpen) return;
    if (isSpacePressed || window.interactionMode === 'pan' || e.button === 1 || e.button === 2 || e.altKey) {
      e.preventDefault();
    }
    isPointerDown = true;
    window.isPointerDown = true;
    lastPointerX = e.clientX;
    lastPointerY = e.clientY;
    lastPointerAngle = getPointerCenterAngle(e.clientX, e.clientY);
    if (isSpacePressed || window.interactionMode === 'pan') {
      workspace.classList.add('space-grabbing');
    }
  });

  window.addEventListener('mousemove', e => {
    if (!isPointerDown || isMultiTouchPinch) return;

    if (isSpacePressed || window.interactionMode === 'pan' || e.buttons === 2 || e.buttons === 4 || e.altKey) {
      e.preventDefault();
      const dx = e.clientX - lastPointerX;
      const dy = e.clientY - lastPointerY;
      panX += dx;
      panY += dy;
      lastPointerX = e.clientX;
      lastPointerY = e.clientY;
      applyViewportTransform();
      return;
    }

    // Rotation mode
    const currentAngle = getPointerCenterAngle(e.clientX, e.clientY);
    let delta = currentAngle - lastPointerAngle;
    if (delta > 180) delta -= 360;
    if (delta < -180) delta += 360;
    lastPointerAngle = currentAngle;
    lastPointerX = e.clientX;
    lastPointerY = e.clientY;

    if (window.currentFace === 'back') {
      if (typeof window.onAlidadeRotated === 'function') {
        window.onAlidadeRotated(window.alidadeAngle + delta);
      } else {
        setAlidadeAngleSmooth(window.alidadeAngle + delta, false);
      }
    } else {
      const activeMode = e.shiftKey ? 'rule' : window.touchMode;
      if (activeMode === 'rule') {
        if (typeof window.onRuleRotated === 'function') {
          window.onRuleRotated(window.ruleAngle + delta);
        } else {
          setRuleAngleSmooth(window.ruleAngle + delta, false);
        }
      } else {
        if (typeof window.onReteRotated === 'function') {
          window.onReteRotated(window.reteAngle + delta);
        } else {
          setReteAngleSmooth(window.reteAngle + delta, false);
        }
      }
    }
  });

  window.addEventListener('mouseup', () => {
    isPointerDown = false;
    window.isPointerDown = false;
    workspace.classList.remove('space-grabbing');
  });

  // Spacebar Pan Navigation
  window.addEventListener('keydown', e => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;
    if (e.code === 'Space' || e.key === ' ') {
      e.preventDefault();
      if (document.activeElement && document.activeElement.blur) {
        document.activeElement.blur();
      }
      if (!isSpacePressed) {
        isSpacePressed = true;
        workspace.classList.add('space-panning');
      }
    }
  });

  window.addEventListener('keyup', e => {
    if (e.code === 'Space' || e.key === ' ') {
      isSpacePressed = false;
      workspace.classList.remove('space-panning');
      workspace.classList.remove('space-grabbing');
    }
  });

  window.addEventListener('blur', () => {
    isSpacePressed = false;
    isPointerDown = false;
    window.isPointerDown = false;
    workspace.classList.remove('space-panning');
    workspace.classList.remove('space-grabbing');
  });

  // Touch Events
  workspace.addEventListener('touchstart', e => {
    if (window.isMenuOpen) return;
    if (e.touches.length >= 2) {
      isMultiTouchPinch = true;
      initialPinchDist = getTouchDistance(e.touches[0], e.touches[1]);
      initialPinchZoom = currentZoom;
      const mid = getTouchMidpoint(e.touches[0], e.touches[1]);
      lastPinchMidX = mid.x;
      lastPinchMidY = mid.y;
    } else if (e.touches.length === 1) {
      isMultiTouchPinch = false;
      isPointerDown = true;
      window.isPointerDown = true;
      lastPointerX = e.touches[0].clientX;
      lastPointerY = e.touches[0].clientY;
      lastPointerAngle = getPointerCenterAngle(e.touches[0].clientX, e.touches[0].clientY);
    }
  }, { passive: false });

  workspace.addEventListener('touchmove', e => {
    if (window.isMenuOpen) return;
    e.preventDefault();

    if (e.touches.length >= 2) {
      const currentDist = getTouchDistance(e.touches[0], e.touches[1]);
      const mid = getTouchMidpoint(e.touches[0], e.touches[1]);
      const newZoom = initialPinchZoom * (currentDist / (initialPinchDist || 1));
      panX += (mid.x - lastPinchMidX);
      panY += (mid.y - lastPinchMidY);
      lastPinchMidX = mid.x;
      lastPinchMidY = mid.y;
      setZoom(newZoom);
      return;
    }

    if (e.touches.length === 1 && !isMultiTouchPinch) {
      const touch = e.touches[0];
      if (window.interactionMode === 'pan') {
        panX += (touch.clientX - lastPointerX);
        panY += (touch.clientY - lastPointerY);
        lastPointerX = touch.clientX;
        lastPointerY = touch.clientY;
        applyViewportTransform();
        return;
      }

      const currentAngle = getPointerCenterAngle(touch.clientX, touch.clientY);
      let delta = currentAngle - lastPointerAngle;
      if (delta > 180) delta -= 360;
      if (delta < -180) delta += 360;
      lastPointerAngle = currentAngle;
      lastPointerX = touch.clientX;
      lastPointerY = touch.clientY;

      if (window.currentFace === 'back') {
        if (typeof window.onAlidadeRotated === 'function') {
          window.onAlidadeRotated(window.alidadeAngle + delta);
        } else {
          setAlidadeAngleSmooth(window.alidadeAngle + delta, false);
        }
      } else {
        if (window.touchMode === 'rule') {
          if (typeof window.onRuleRotated === 'function') {
            window.onRuleRotated(window.ruleAngle + delta);
          } else {
            setRuleAngleSmooth(window.ruleAngle + delta, false);
          }
        } else {
          if (typeof window.onReteRotated === 'function') {
            window.onReteRotated(window.reteAngle + delta);
          } else {
            setReteAngleSmooth(window.reteAngle + delta, false);
          }
        }
      }
    }
  }, { passive: false });

  workspace.addEventListener('touchend', e => {
    if (e.touches.length < 2) isMultiTouchPinch = false;
    if (e.touches.length === 0) {
      isPointerDown = false;
      window.isPointerDown = false;
    }
  });
}

// Global Exports
window.applyViewportTransform = applyViewportTransform;
window.setZoom = setZoom;
window.zoomBy = zoomBy;
window.resetView = resetView;
window.updateSunOnEcliptic = updateSunOnEcliptic;
window.setReteAngleSmooth = setReteAngleSmooth;
window.setRuleAngleSmooth = setRuleAngleSmooth;
window.setAlidadeAngleSmooth = setAlidadeAngleSmooth;
window.setLayerFilter = setLayerFilter;
window.initAstrolabeInteractions = initAstrolabeInteractions;
