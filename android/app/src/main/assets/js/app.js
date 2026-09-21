/**
 * Classical Islamic Astrolabe - Application & UI Controller
 * منسق واجهة المستخدم، التحديث الحي، واستدعاء المحركات الفلكية
 */

// Application State
let currentFace = 'front';
let reteAngle = 0;
let ruleAngle = 0;
let alidadeAngle = 90.0;
let dayOfYear = 80;
let solarTime = 12.0;
let touchMode = 'rete';
let interactionMode = 'rotate'; // 'rotate' | 'pan'
let layerFilter = 'all';        // 'all' | 'stars' | 'grid' | 'prayers'
let isMenuOpen = false;
let isInspectorVisible = true;
let isLiveMode = true;

// Expose state globally for event handlers & interaction engine
window.currentFace = currentFace;
window.reteAngle = reteAngle;
window.ruleAngle = ruleAngle;
window.alidadeAngle = alidadeAngle;
window.dayOfYear = dayOfYear;
window.solarTime = solarTime;
window.touchMode = touchMode;
window.interactionMode = interactionMode;
window.layerFilter = layerFilter;
window.isMenuOpen = isMenuOpen;
window.isInspectorVisible = isInspectorVisible;
window.isLiveMode = isLiveMode;

/* ==================== LIVE REAL-TIME CLOCK CONTROLLER ==================== */
function updateLiveTag() {
  const tags = [document.getElementById('hud-live-tag'), document.getElementById('mini-live-tag')];
  tags.forEach(tag => {
    if (!tag) return;
    if (isLiveMode) {
      tag.innerText = '● مباشر';
      tag.style.background = '#059669';
      tag.style.color = '#fff';
      tag.title = 'التتبع الحي التلقائي نشط - انقر للإيقاف المؤقت والتحكم اليدوي';
    } else {
      tag.innerText = '⏸ يدوي';
      tag.style.background = '#d97706';
      tag.style.color = '#fff';
      tag.title = 'التحكم يدوي - انقر لاستئناف التتبع الحي للحظة الحالية';
    }
  });
}

function toggleLiveMode() {
  isLiveMode = !isLiveMode;
  window.isLiveMode = isLiveMode;
  if (isLiveMode) {
    setNow(true);
  }
  updateLiveTag();
}

function userInteracted() {
  if (isLiveMode) {
    isLiveMode = false;
    window.isLiveMode = false;
    updateLiveTag();
  }
}

/* ==================== DATE & CALENDAR SYNC ==================== */
function setDayOfYear(doy, animate = false) {
  userInteracted();
  dayOfYear = ((doy - 1) % 365 + 365) % 365 + 1;
  window.dayOfYear = dayOfYear;
  syncDateUI();
  updateSunOnEcliptic();
  setSolarTime(solarTime, animate);
}

function setDatePreset(doy) {
  userInteracted();
  setDayOfYear(doy, true);
}

function onDatePickerChange(val) {
  if (!val) return;
  userInteracted();
  const doy = AstroMath.dateStringToDayOfYear(val, dayOfYear);
  setDayOfYear(doy, false);
}

function triggerDatePicker(pickerId) {
  const el = document.getElementById(pickerId);
  if (!el) return;
  if (typeof el.showPicker === 'function') {
    try {
      el.showPicker();
      return;
    } catch (e) {}
  }
  el.focus();
  el.click();
}

function syncDateUI() {
  const dateIso = AstroMath.dayOfYearToDate(dayOfYear);
  const months = (AstroDatabase && AstroDatabase.calendar && AstroDatabase.calendar.months) || [];
  
  let m = 0;
  let dLeft = dayOfYear;
  while (m < months.length && dLeft > months[m].days) {
    dLeft -= months[m].days;
    m++;
  }
  const mName = months[m] ? months[m].name : '';
  const dateStr = `${dLeft} ${mName}`;

  // Update date inputs
  ['floating-date-picker', 'sidebar-date-picker', 'sidebar-date-picker-back'].forEach(id => {
    const el = document.getElementById(id);
    if (el && el.value !== dateIso && document.activeElement !== el) el.value = dateIso;
  });

  // Sliders
  const slDay = document.getElementById('slider-day');
  if (slDay && parseInt(slDay.value) !== dayOfYear) slDay.value = dayOfYear;
  const slDayBack = document.getElementById('slider-day-back');
  if (slDayBack && parseInt(slDayBack.value) !== dayOfYear) slDayBack.value = dayOfYear;

  // Text labels
  const txtDay = document.getElementById('txt-day');
  if (txtDay) txtDay.innerText = `اليوم ${dayOfYear}`;
  const txtDayBack = document.getElementById('txt-day-back');
  if (txtDayBack) txtDayBack.innerText = `اليوم ${dayOfYear}`;

  const stepperDate = document.getElementById('stepper-date-txt');
  if (stepperDate) stepperDate.innerText = dateStr;

  const txtFmt = document.getElementById('txt-day-formatted');
  if (txtFmt) txtFmt.innerText = dateStr;
  const txtBackFmt = document.getElementById('txt-day-back-formatted');
  if (txtBackFmt) txtBackFmt.innerText = dateStr;

  const hudDate = document.getElementById('hud-date');
  if (hudDate) hudDate.innerText = dateStr;
}

function stepDay(deltaDays) {
  userInteracted();
  setDayOfYear(dayOfYear + deltaDays, false);
}

function stepTime(deltaHours) {
  userInteracted();
  let t = (solarTime + deltaHours) % 24.0;
  if (t < 0) t += 24.0;
  setSolarTime(t, true);
}

/* ==================== SOLAR TIME & HUD ENGINE ==================== */
function setSolarTime(t, animate = false) {
  solarTime = (t % 24.0 + 24.0) % 24.0;
  window.solarTime = solarTime;
  const slTime = document.getElementById('slider-time');
  if (slTime) slTime.value = solarTime;

  const h = Math.floor(solarTime);
  const m = Math.round((solarTime - h) * 60);
  const hFinal = m === 60 ? (h + 1) % 24 : h;
  const mFinal = m === 60 ? 0 : m;
  const timeStr = `${String(hFinal).padStart(2, '0')}:${String(mFinal).padStart(2, '0')}`;
  const txtTime = document.getElementById('txt-time');
  if (txtTime) txtTime.innerText = timeStr;
  const stpTime = document.getElementById('stepper-time-txt');
  if (stpTime) stpTime.innerText = timeStr;

  const targetRete = AstroMath.solarTimeToRete(solarTime, dayOfYear);
  reteAngle = targetRete;
  window.reteAngle = targetRete;
  setReteAngleSmooth(targetRete, animate);

  const slRete = document.getElementById('slider-rete');
  if (slRete) slRete.value = reteAngle;
  const txtRete = document.getElementById('txt-rete');
  if (txtRete) txtRete.innerText = `${reteAngle.toFixed(1)}°`;
  const slRule = document.getElementById('slider-rule');
  if (slRule) slRule.value = ruleAngle;
  const txtRule = document.getElementById('txt-rule');
  if (txtRule) txtRule.innerText = `${ruleAngle.toFixed(1)}°`;

  update();
}

/**
 * Handle interactive manual rotation of the Rete (by hand or slider)
 * Computes the corresponding Solar & Civil Time, Sun Altitude, and updates HUD live.
 */
function onReteRotated(newAngle) {
  userInteracted();
  const normalized = (newAngle % 360.0 + 360.0) % 360.0;
  reteAngle = normalized;
  window.reteAngle = normalized;
  setReteAngleSmooth(reteAngle, false);

  const slRete = document.getElementById('slider-rete');
  if (slRete) slRete.value = reteAngle;
  const txtRete = document.getElementById('txt-rete');
  if (txtRete) txtRete.innerText = `${reteAngle.toFixed(1)}°`;

  // Synchronize Apparent Solar Time from Rete celestial orientation
  solarTime = AstroMath.reteToSolarTime(reteAngle, dayOfYear);
  window.solarTime = solarTime;

  const slTime = document.getElementById('slider-time');
  if (slTime) slTime.value = solarTime;
  const h = Math.floor(solarTime);
  const m = Math.round((solarTime - h) * 60);
  const hFinal = m === 60 ? (h + 1) % 24 : h;
  const mFinal = m === 60 ? 0 : m;
  const timeStr = `${String(hFinal).padStart(2, '0')}:${String(mFinal).padStart(2, '0')}`;
  const txtTime = document.getElementById('txt-time');
  if (txtTime) txtTime.innerText = timeStr;
  const stpTime = document.getElementById('stepper-time-txt');
  if (stpTime) stpTime.innerText = timeStr;

  update();
}

/**
 * Handle interactive manual rotation of the Rule (Front face radial pointer)
 */
function onRuleRotated(newAngle) {
  userInteracted();
  const normalized = (newAngle % 360.0 + 360.0) % 360.0;
  ruleAngle = normalized;
  window.ruleAngle = normalized;
  setRuleAngleSmooth(ruleAngle, false);

  const slRule = document.getElementById('slider-rule');
  if (slRule) slRule.value = ruleAngle;
  const txtRule = document.getElementById('txt-rule');
  if (txtRule) txtRule.innerText = `${ruleAngle.toFixed(1)}°`;

  update();
}

/**
 * Handle interactive manual rotation of the Alidade (Back face surveying rule)
 */
function onAlidadeRotated(newAngle) {
  userInteracted();
  const normalized = (newAngle % 360.0 + 360.0) % 360.0;
  alidadeAngle = normalized;
  window.alidadeAngle = normalized;
  setAlidadeAngleSmooth(alidadeAngle, false);

  const slAli = document.getElementById('slider-alidade');
  if (slAli) slAli.value = alidadeAngle;
  const txtAli = document.getElementById('txt-alidade');
  if (txtAli) txtAli.innerText = `${alidadeAngle.toFixed(1)}°`;

  update();
}

function update() {
  if (window.solarTime !== undefined) solarTime = window.solarTime;
  if (window.reteAngle !== undefined) reteAngle = window.reteAngle;
  if (window.ruleAngle !== undefined) ruleAngle = window.ruleAngle;
  if (window.alidadeAngle !== undefined) alidadeAngle = window.alidadeAngle;
  if (window.dayOfYear !== undefined) dayOfYear = window.dayOfYear;

  const lat = AstroDatabase.constants.latDeg;
  const lon = AstroDatabase.constants.lonDeg;
  const { lambdaSun, sunDec, eotMin } = AstroMath.computeSunCoords(dayOfYear);

  // 1. Zodiac Info
  const zodiac = AstroDatabase.zodiac;
  const signIdx = Math.floor(lambdaSun / 30);
  const degInSign = (lambdaSun % 30).toFixed(1);
  const zSign = zodiac[signIdx % 12];
  const zName = zSign ? zSign.name : '';
  const hudZodiac = document.getElementById('hud-zodiac');
  if (hudZodiac) hudZodiac.innerText = `${degInSign}° ${zName}`;

  // 2. Solar & Civil Clock Times
  const h = Math.floor(solarTime);
  const minTotal = (solarTime - h) * 60;
  const min = Math.floor(minTotal);
  const sec = Math.floor((minTotal - min) * 60);
  const solarStr = `${String(h).padStart(2, '0')}:${String(min).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
  
  const hudSolar = document.getElementById('hud-solar-time');
  if (hudSolar) hudSolar.innerText = solarStr;
  const miniSolar = document.getElementById('mini-solar-time');
  if (miniSolar) miniSolar.innerText = `${String(h).padStart(2, '0')}:${String(min).padStart(2, '0')}`;
  const inspSolar = document.getElementById('insp-solar');
  if (inspSolar) inspSolar.innerText = solarStr;

  const clockTime = AstroMath.solarToClockTime(solarTime, dayOfYear, lon, 0.0);
  const ch = Math.floor(clockTime);
  const cmTotal = (clockTime - ch) * 60;
  const cm = Math.floor(cmTotal);
  const cs = Math.floor((cmTotal - cm) * 60);
  const clockStr = `${String(ch).padStart(2, '0')}:${String(cm).padStart(2, '0')}:${String(cs).padStart(2, '0')}`;
  
  const hudClock = document.getElementById('hud-clock-time');
  if (hudClock) hudClock.innerText = clockStr;
  const miniClock = document.getElementById('mini-clock-time');
  if (miniClock) miniClock.innerText = clockStr;

  // 3. Local Sidereal Time (LST / مطلع الفلك)
  const lstDeg = (reteAngle + 90.0 + 360.0) % 360.0;
  const lstHours = lstDeg / 15.0;
  const lstH = Math.floor(lstHours);
  const lstM = Math.round((lstHours - lstH) * 60);
  const inspLst = document.getElementById('insp-lst');
  if (inspLst) inspLst.innerText = `${String(lstH).padStart(2, '0')}:${String(lstM % 60).padStart(2, '0')}`;

  // 4. Sun Altitude & Azimuth
  const { altDeg, azDeg } = AstroMath.calcSunAltAz(solarTime, dayOfYear, lat);
  const altStr = `${altDeg >= 0 ? '+' : ''}${altDeg.toFixed(1)}°`;
  const hudAlt = document.getElementById('hud-altitude');
  if (hudAlt) hudAlt.innerText = altStr;
  const miniAlt = document.getElementById('mini-alt');
  if (miniAlt) miniAlt.innerText = altStr;
  const inspAlt = document.getElementById('insp-alt');
  if (inspAlt) inspAlt.innerText = altStr;

  const hudAz = document.getElementById('hud-azimuth');
  if (hudAz) hudAz.innerText = `${azDeg.toFixed(1)}°`;
  const inspAz = document.getElementById('insp-az');
  if (inspAz) inspAz.innerText = `${azDeg.toFixed(1)}°`;

  // 5. Day / Night Status
  const isDay = altDeg >= 0;
  const statusTxt = isDay ? 'نهار' : (altDeg >= -18.0 ? 'شفق' : 'ليل');
  const hudStatus = document.getElementById('hud-status');
  if (hudStatus) hudStatus.innerText = statusTxt;
  const inspStatus = document.getElementById('inspector-status-badge');
  if (inspStatus) inspStatus.innerText = statusTxt;

  // 6. Object Sighted along Rule
  const sighted = AstroMath.findObjectUnderRule(ruleAngle, reteAngle, dayOfYear);
  const hudStar = document.getElementById('hud-star');
  if (hudStar) hudStar.innerText = sighted.label;
  const inspObj = document.getElementById('insp-object');
  if (inspObj) inspObj.innerText = sighted.label;
  const inspNear = document.getElementById('insp-nearest-star');
  if (inspNear && sighted.nearest) {
    inspNear.innerText = `⭐ أقرب كوكب/نجم: ${sighted.nearest.name} (قدر ${sighted.nearest.mag})`;
  }

  // Lunar Mansion of Sighted Angle
  const sightedRA = (ruleAngle - reteAngle + 720.0) % 360.0;
  const mIdx = Math.floor(sightedRA / (360.0 / 28.0)) % 28;
  const mansions = AstroDatabase.mansions;
  const mEl = document.getElementById('insp-mansion');
  if (mEl && mansions[mIdx]) {
    mEl.innerText = `${mansions[mIdx].name} (${mIdx + 1}/28)`;
  }

  // 7. Back Face Computations
  const deg = alidadeAngle % 360.0;
  let measAlt = 0;
  let quadName = '';
  if (deg >= 0 && deg <= 90) {
    measAlt = deg;
    quadName = 'ربع المغرب (شمال غرب)';
  } else if (deg > 90 && deg <= 180) {
    measAlt = 180.0 - deg;
    quadName = 'ربع المشرق (شمال شرق)';
  } else if (deg > 180 && deg <= 270) {
    measAlt = deg - 180.0;
    quadName = 'ربع الزوال الشرقي (جنوب شرق)';
  } else {
    measAlt = 360.0 - deg;
    quadName = 'ربع الزوال الغربي (جنوب غرب)';
  }
  const hudBackAlt = document.getElementById('hud-back-alt');
  if (hudBackAlt) hudBackAlt.innerText = `${measAlt.toFixed(1)}°`;
  const hudAliDeg = document.getElementById('hud-alidade-deg');
  if (hudAliDeg) hudAliDeg.innerText = `${alidadeAngle.toFixed(1)}°`;
  const hudBackQuad = document.getElementById('hud-back-quad');
  if (hudBackQuad) hudBackQuad.innerText = quadName;

  // Equation of Time
  const eotSign = eotMin >= 0 ? '+' : '-';
  const eotAbs = Math.abs(eotMin);
  const eotM = Math.floor(eotAbs);
  const eotS = Math.round((eotAbs - eotM) * 60);
  const hudEotVal = document.getElementById('hud-eot-val');
  if (hudEotVal) hudEotVal.innerText = `${eotSign}${String(eotM).padStart(2, '0')}:${String(eotS).padStart(2, '0')} دقيقة`;
  const hudEotAli = document.getElementById('hud-eot-alidade');
  if (hudEotAli) hudEotAli.innerText = `${eotSign}${eotAbs.toFixed(1)} دقيقة`;
  const hudEotStat = document.getElementById('hud-eot-status');
  if (hudEotStat) {
    hudEotStat.innerText = eotMin > 0.5 ? 'الشمس تسبق التوقيت الوسطي (+)' : (eotMin < -0.5 ? 'الشمس تتأخر عن التوقيت الوسطي (-)' : 'تطابق كامل لمعادلة الوقت');
  }

  // Shadow Squares & Sine Quadrant
  const aRad = measAlt * Math.PI / 180.0;
  const tanA = Math.tan(aRad);
  const sRecta = tanA > 0 ? (12.0 / tanA) : 99.0;
  const sVersa = 12.0 * tanA;
  const hudSRecta = document.getElementById('hud-shadow-recta');
  if (hudSRecta) hudSRecta.innerText = sRecta <= 12.0 ? `${sRecta.toFixed(1)} أصبع` : '> 12 أصبع';
  const hudSVersa = document.getElementById('hud-shadow-versa');
  if (hudSVersa) hudSVersa.innerText = sVersa <= 12.0 ? `${sVersa.toFixed(1)} أصبع` : '> 12 أصبع';

  const sin60 = 60.0 * Math.sin(aRad);
  const cos60 = 60.0 * Math.cos(aRad);
  const hudSin60 = document.getElementById('hud-sine-60');
  if (hudSin60) hudSin60.innerText = `${sin60.toFixed(1)} / 60`;
  const hudCos60 = document.getElementById('hud-cos-60');
  if (hudCos60) hudCos60.innerText = `${cos60.toFixed(1)} / 60`;
}

/* ==================== NAVIGATION & TOGGLES ==================== */
function toggleMenu(open) {
  isMenuOpen = open;
  window.isMenuOpen = open;
  const sb = document.getElementById('sidebar');
  const bd = document.getElementById('drawer-backdrop');
  if (sb && bd) {
    sb.classList.toggle('open', open);
    bd.classList.toggle('open', open);
  }
}

function toggleFaceQuick() {
  switchFace(currentFace === 'front' ? 'back' : 'front');
}

function toggleTouchModeQuick() {
  if (currentFace === 'back') return;
  setTouchMode(touchMode === 'rete' ? 'rule' : 'rete');
}

function setTouchMode(mode) {
  touchMode = mode;
  window.touchMode = mode;
  const isRete = mode === 'rete';
  const icon = document.getElementById('quick-mode-icon');
  if (icon) icon.innerText = isRete ? '🧭' : '📏';
  const label = document.getElementById('quick-mode-label');
  if (label) label.innerText = isRete ? 'الشبكة' : 'المسطرة';
  const btn = document.getElementById('quick-mode-btn');
  if (btn) btn.classList.toggle('active', isRete);
}

function switchFace(face) {
  currentFace = face;
  window.currentFace = face;
  const isFront = face === 'front';

  document.getElementById('tab-front').classList.toggle('active', isFront);
  document.getElementById('tab-back').classList.toggle('active', !isFront);
  document.getElementById('front-panel').style.display = isFront ? 'flex' : 'none';
  document.getElementById('back-panel').style.display = isFront ? 'none' : 'flex';
  document.getElementById('front-face-container').style.display = isFront ? 'block' : 'none';
  document.getElementById('back-face-container').style.display = isFront ? 'none' : 'block';
  document.getElementById('quick-face-icon').innerText = isFront ? '☀️' : '🌙';
  document.getElementById('quick-face-label').innerText = isFront ? 'الوجه' : 'الظهر';

  const qm = document.getElementById('quick-mode-btn');
  if (!isFront) {
    if (qm) qm.style.opacity = '0.5';
    document.getElementById('quick-mode-icon').innerText = '📐';
    document.getElementById('quick-mode-label').innerText = 'العضادة';
  } else {
    if (qm) qm.style.opacity = '1.0';
    setTouchMode(touchMode);
  }
  update();
}

function toggleInteractionMode() {
  interactionMode = interactionMode === 'rotate' ? 'pan' : 'rotate';
  window.interactionMode = interactionMode;
  const btn = document.getElementById('btn-interact-mode');
  const ws = document.getElementById('workspace');
  if (interactionMode === 'pan') {
    if (btn) {
      btn.classList.add('active');
      btn.innerText = '✋ نمط السحب';
    }
    if (ws) ws.classList.add('space-panning');
  } else {
    if (btn) {
      btn.classList.remove('active');
      btn.innerText = '🔄 نمط التدوير';
    }
    if (ws) {
      ws.classList.remove('space-panning');
      ws.classList.remove('space-grabbing');
    }
  }
}

function toggleInspector() {
  isInspectorVisible = !isInspectorVisible;
  window.isInspectorVisible = isInspectorVisible;
  const card = document.getElementById('inspector-card');
  const btn = document.getElementById('inspector-toggle-btn');
  if (card) card.style.display = isInspectorVisible ? 'block' : 'none';
  if (btn) btn.classList.toggle('active', isInspectorVisible);
}

/* ==================== ASTRONOMICAL PRESETS ==================== */
function setPrayerAltitude(altDeg, isAfternoon) {
  userInteracted();
  const t = AstroMath.calcPrayerSolarTime(altDeg, isAfternoon, dayOfYear, AstroDatabase.constants.latDeg);
  setSolarTime(t, true);
}

function setFajr() { setPrayerAltitude(-19.0, false); }
function setSunrise() { setPrayerAltitude(0.0, false); }
function setDhuhr() { userInteracted(); setSolarTime(12.0, true); }
function setNoon() { setDhuhr(); }
function setAsr() {
  userInteracted();
  const aAsr = AstroMath.calcAsrAltitude(dayOfYear, AstroDatabase.constants.latDeg);
  setPrayerAltitude(aAsr, true);
}
function setMaghrib() { setPrayerAltitude(0.0, true); }
function setSunset() { setMaghrib(); }
function setIsha() { setPrayerAltitude(-17.0, true); }

function setNow(animate = true) {
  isLiveMode = true;
  window.isLiveMode = true;
  updateLiveTag();
  const now = new Date();
  const start = new Date(now.getFullYear(), 0, 0);
  const diff = now - start;
  const oneDay = 1000 * 60 * 60 * 24;
  dayOfYear = Math.floor(diff / oneDay);
  window.dayOfYear = dayOfYear;
  const clockTime = now.getHours() + now.getMinutes() / 60.0 + now.getSeconds() / 3600.0;
  solarTime = AstroMath.clockToSolarTime(clockTime, dayOfYear, AstroDatabase.constants.lonDeg, 0.0);
  window.solarTime = solarTime;

  syncDateUI();
  updateSunOnEcliptic();
  setSolarTime(solarTime, animate);
}

// Back Presets
function setBackNoonAlt() {
  userInteracted();
  const { sunDec } = AstroMath.computeSunCoords(dayOfYear);
  const noonAlt = 90.0 - AstroDatabase.constants.latDeg + sunDec;
  const target = (alidadeAngle > 90 && alidadeAngle <= 270) ? (180.0 - noonAlt) : noonAlt;
  setAlidadeAngleSmooth(target, true);
  document.getElementById('slider-alidade').value = alidadeAngle;
  document.getElementById('txt-alidade').innerText = `${alidadeAngle.toFixed(1)}°`;
  update();
}

function setBackZenith() {
  userInteracted();
  setAlidadeAngleSmooth(90.0, true);
  document.getElementById('slider-alidade').value = alidadeAngle;
  document.getElementById('txt-alidade').innerText = `${alidadeAngle.toFixed(1)}°`;
  update();
}

function setBackHorizon() {
  userInteracted();
  setAlidadeAngleSmooth(0.0, true);
  document.getElementById('slider-alidade').value = alidadeAngle;
  document.getElementById('txt-alidade').innerText = `${alidadeAngle.toFixed(1)}°`;
  update();
}

function setBackAsrAlt() {
  userInteracted();
  const asrAlt = AstroMath.calcAsrAltitude(dayOfYear, AstroDatabase.constants.latDeg);
  setAlidadeAngleSmooth(asrAlt, true);
  document.getElementById('slider-alidade').value = alidadeAngle;
  document.getElementById('txt-alidade').innerText = `${alidadeAngle.toFixed(1)}°`;
  update();
}

function exportCanvas() {
  window.print();
}

/* ==================== THEME MANAGEMENT ==================== */
let currentTheme = localStorage.getItem('astrolabe_theme') || 'ancient';

function setTheme(theme) {
  if (!['light', 'ancient', 'dark'].includes(theme)) theme = 'ancient';
  currentTheme = theme;
  try {
    localStorage.setItem('astrolabe_theme', theme);
  } catch (e) {}

  document.body.classList.remove('theme-light', 'theme-dark', 'theme-ancient');
  document.body.classList.add('theme-' + theme);

  // Dynamically switch Kursi SVG to native tailored theme gradient
  const kursi = document.getElementById('kursi-img');
  if (kursi) {
    kursi.src = `assets/Kursi-${theme}.svg`;
  }

  ['light', 'ancient', 'dark'].forEach(t => {
    const btns = document.querySelectorAll('.theme-btn-' + t);
    btns.forEach(b => b.classList.toggle('active', t === theme));
  });
}

/* ==================== INITIALIZATION & BINDINGS ==================== */
function initAstrolabeApp() {
  // Theme init
  setTheme(currentTheme);

  // Direct Slider Bindings
  const slRete = document.getElementById('slider-rete');
  if (slRete) slRete.addEventListener('input', e => {
    onReteRotated(parseFloat(e.target.value));
  });

  const slRule = document.getElementById('slider-rule');
  if (slRule) slRule.addEventListener('input', e => {
    onRuleRotated(parseFloat(e.target.value));
  });

  const slAli = document.getElementById('slider-alidade');
  if (slAli) slAli.addEventListener('input', e => {
    onAlidadeRotated(parseFloat(e.target.value));
  });

  const slTime = document.getElementById('slider-time');
  if (slTime) slTime.addEventListener('input', e => {
    userInteracted();
    setSolarTime(parseFloat(e.target.value), false);
  });

  // Date Pickers Listeners
  ['floating-date-picker', 'sidebar-date-picker', 'sidebar-date-picker-back'].forEach(id => {
    const picker = document.getElementById(id);
    if (picker) {
      const handler = e => {
        userInteracted();
        if (e.target.value) {
          const doy = AstroMath.dateStringToDayOfYear(e.target.value, dayOfYear);
          setDayOfYear(doy, false);
        }
      };
      picker.addEventListener('change', handler);
      picker.addEventListener('input', handler);
    }
  });

  const slDay = document.getElementById('slider-day');
  if (slDay) slDay.addEventListener('input', e => {
    userInteracted();
    setDayOfYear(parseInt(e.target.value), false);
  });

  const slDayBack = document.getElementById('slider-day-back');
  if (slDayBack) slDayBack.addEventListener('input', e => {
    userInteracted();
    setDayOfYear(parseInt(e.target.value), false);
  });

  // Initialize Gesture Interactions
  if (typeof initAstrolabeInteractions === 'function') {
    initAstrolabeInteractions();
  }

  // Load Real-World Time & Set Alidade
  setNow(false);
  setAlidadeAngleSmooth(90.0, false);
  updateLiveTag();

  // Live Real-Time Ticker (Every 1 second)
  setInterval(() => {
    if (window.isLiveMode && !window.isPointerDown) {
      setNow(false);
    }
  }, 1000);
}

// Global Exports
window.onReteRotated = onReteRotated;
window.onRuleRotated = onRuleRotated;
window.onAlidadeRotated = onAlidadeRotated;
window.userInteracted = userInteracted;
window.updateLiveTag = updateLiveTag;
window.toggleLiveMode = toggleLiveMode;
window.setDayOfYear = setDayOfYear;
window.setDatePreset = setDatePreset;
window.stepDay = stepDay;
window.stepTime = stepTime;
window.setSolarTime = setSolarTime;
window.update = update;
window.toggleMenu = toggleMenu;
window.toggleFaceQuick = toggleFaceQuick;
window.toggleTouchModeQuick = toggleTouchModeQuick;
window.setTouchMode = setTouchMode;
window.switchFace = switchFace;
window.toggleInteractionMode = toggleInteractionMode;
window.toggleInspector = toggleInspector;
window.triggerDatePicker = triggerDatePicker;
window.onDatePickerChange = onDatePickerChange;
window.setPrayerAltitude = setPrayerAltitude;
window.setFajr = setFajr;
window.setSunrise = setSunrise;
window.setDhuhr = setDhuhr;
window.setNoon = setNoon;
window.setAsr = setAsr;
window.setMaghrib = setMaghrib;
window.setSunset = setSunset;
window.setIsha = setIsha;
window.setNow = setNow;
window.setBackNoonAlt = setBackNoonAlt;
window.setBackZenith = setBackZenith;
window.setBackHorizon = setBackHorizon;
window.setBackAsrAlt = setBackAsrAlt;
window.exportCanvas = exportCanvas;
window.setTheme = setTheme;

// Start on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAstrolabeApp);
} else {
  initAstrolabeApp();
}
