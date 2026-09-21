/**
 * Classical Islamic Astrolabe - Astronomical Mathematics Engine
 * خوارزميات الحسابات الفلكية، موقع الشمس، معادلة الوقت ومواقيت الصلاة
 */

const AstroMath = {
  /**
   * High-precision solar coordinates and Equation of Time
   * (NOAA / Jean Meeus Astronomical Algorithms)
   */
  computeSunCoords(doy, year = (new Date()).getFullYear()) {
    const dt = new Date(year, 0, 1);
    dt.setDate(dt.getDate() + doy - 1);
    let y = dt.getFullYear();
    let m = dt.getMonth() + 1;
    const d = dt.getDate();

    if (m <= 2) {
      y -= 1;
      m += 12;
    }
    const A = Math.floor(y / 100);
    const B_val = 2 - A + Math.floor(A / 4);
    // Julian Day at 12:00 UTC
    const jd = Math.floor(365.25 * (y + 4716)) + Math.floor(30.6001 * (m + 1)) + d + B_val - 1524.5 + 0.5;
    const T = (jd - 2451545.0) / 36525.0;

    // Geometric mean longitude of the Sun (deg)
    const L0 = (280.46646 + 36000.76983 * T + 0.0003032 * T * T) % 360.0;
    // Mean anomaly of the Sun (deg)
    const M = (357.52911 + 35999.05029 * T - 0.0001537 * T * T) % 360.0;
    const M_rad = M * Math.PI / 180.0;

    // Equation of center (deg)
    const C = (1.914602 - 0.004817 * T) * Math.sin(M_rad)
      + (0.019993 - 0.000101 * T) * Math.sin(2 * M_rad)
      + 0.000289 * Math.sin(3 * M_rad);

    // True longitude of the Sun (deg)
    const sunTrueLon = (L0 + C) % 360.0;

    // Apparent longitude (corrected for nutation and aberration)
    const omega = 125.04 - 1934.136 * T;
    const lambdaSun = ((sunTrueLon - 0.00569 - 0.00478 * Math.sin(omega * Math.PI / 180.0)) % 360.0 + 360.0) % 360.0;

    // Mean obliquity of the ecliptic
    const eps0 = 23.439291 - 0.0130042 * T;
    const eps = eps0 + 0.00256 * Math.cos(omega * Math.PI / 180.0);
    const epsRad = eps * Math.PI / 180.0;
    const lamRad = lambdaSun * Math.PI / 180.0;

    // Declination
    const sinDec = Math.sin(epsRad) * Math.sin(lamRad);
    const sunDecRad = Math.asin(Math.max(-1.0, Math.min(1.0, sinDec)));
    const sunDecDeg = sunDecRad * 180.0 / Math.PI;

    // Right Ascension
    const y_ra = Math.cos(epsRad) * Math.sin(lamRad);
    const x_ra = Math.cos(lamRad);
    let sunRA = Math.atan2(y_ra, x_ra);
    let sunRADeg = (sunRA * 180.0 / Math.PI + 360.0) % 360.0;

    // Equation of Time (minutes)
    const y2 = Math.tan(epsRad / 2.0) * Math.tan(epsRad / 2.0);
    const L0_rad = L0 * Math.PI / 180.0;
    const eotRad = y2 * Math.sin(2 * L0_rad)
      - 2 * 0.016708634 * Math.sin(M_rad)
      + 4 * 0.016708634 * y2 * Math.sin(M_rad) * Math.cos(2 * L0_rad)
      - 0.5 * (y2 * y2) * Math.sin(4 * L0_rad)
      - 1.25 * (0.016708634 * 0.016708634) * Math.sin(2 * M_rad);
    const eotMin = (eotRad * 180.0 / Math.PI) * 4.0;

    return { lambdaSun, sunDec: sunDecDeg, sunDecRad, sunRA, sunRADeg, eotMin };
  },

  /**
   * Convert Civil Clock Time (e.g. GMT+0) to Apparent Local Solar Time
   */
  clockToSolarTime(clockHour, dayOfYear, lonDeg = -5.81, tzOffset = 0.0) {
    const { eotMin } = this.computeSunCoords(dayOfYear);
    const lonOffsetHours = -lonDeg / 15.0;
    return ((clockHour + eotMin / 60.0 - lonOffsetHours - tzOffset) % 24.0 + 24.0) % 24.0;
  },

  /**
   * Convert Apparent Local Solar Time to Civil Clock Time
   */
  solarToClockTime(solarHour, dayOfYear, lonDeg = -5.81, tzOffset = 0.0) {
    const { eotMin } = this.computeSunCoords(dayOfYear);
    const lonOffsetHours = -lonDeg / 15.0;
    return ((solarHour - eotMin / 60.0 + lonOffsetHours + tzOffset) % 24.0 + 24.0) % 24.0;
  },

  /**
   * Convert Rete orientation angle (deg) to Apparent Local Solar Time (hours [0, 24))
   */
  reteToSolarTime(reteAngle, dayOfYear) {
    const { sunRADeg } = this.computeSunCoords(dayOfYear);
    let H = (reteAngle - sunRADeg - 270.0) % 360.0;
    if (H > 180.0) H -= 360.0;
    if (H < -180.0) H += 360.0;
    return ((12.0 + H / 15.0) % 24.0 + 24.0) % 24.0;
  },

  /**
   * Convert Apparent Local Solar Time (hours) to Rete orientation angle (deg [0, 360))
   */
  solarTimeToRete(solarHour, dayOfYear) {
    const { sunRADeg } = this.computeSunCoords(dayOfYear);
    const H = (solarHour - 12.0) * 15.0;
    return ((sunRADeg + H + 270.0) % 360.0 + 360.0) % 360.0;
  },

  /**
   * Calendar conversion helpers
   */
  dayOfYearToDate(doy, year = new Date().getFullYear()) {
    const dt = new Date(year, 0, 1);
    dt.setDate(dt.getDate() + doy - 1);
    const m = String(dt.getMonth() + 1).padStart(2, '0');
    const d = String(dt.getDate()).padStart(2, '0');
    return `${dt.getFullYear()}-${m}-${d}`;
  },

  dateStringToDayOfYear(dateStr, fallbackDoy = 80) {
    if (!dateStr) return fallbackDoy;
    const parts = dateStr.split('-');
    const y = parseInt(parts[0], 10);
    const m = parseInt(parts[1], 10) - 1;
    const d = parseInt(parts[2], 10);
    const target = new Date(y, m, d);
    const start = new Date(y, 0, 1);
    const diff = target - start;
    const oneDay = 1000 * 60 * 60 * 24;
    let doy = Math.round(diff / oneDay) + 1;
    if (doy < 1) doy = 1;
    if (doy > 365) doy = 365;
    return doy;
  },

  /**
   * Solar Altitude and Azimuth for current solar time and latitude
   */
  calcSunAltAz(solarTime, dayOfYear, latDeg = 35.78) {
    const { sunDec } = this.computeSunCoords(dayOfYear);
    const phi = latDeg * Math.PI / 180.0;
    const dec = sunDec * Math.PI / 180.0;
    const H = (solarTime - 12.0) * 15.0 * Math.PI / 180.0;

    const sinAlt = Math.sin(phi) * Math.sin(dec) + Math.cos(phi) * Math.cos(dec) * Math.cos(H);
    const altRad = Math.asin(Math.max(-1.0, Math.min(1.0, sinAlt)));
    const altDeg = altRad * 180.0 / Math.PI;

    const cosAz = (Math.sin(dec) - Math.sin(phi) * Math.sin(altRad)) / (Math.cos(phi) * Math.cos(altRad) + 1e-6);
    let azDeg = Math.acos(Math.max(-1.0, Math.min(1.0, cosAz))) * 180.0 / Math.PI;
    if (Math.sin(H) > 0) azDeg = 360.0 - azDeg;

    return { altDeg, azDeg };
  },

  /**
   * Calculate Solar Time corresponding to a specific solar altitude (for prayer times)
   */
  calcPrayerSolarTime(altDeg, isAfternoon, dayOfYear, latDeg = 35.78) {
    const { sunDec } = this.computeSunCoords(dayOfYear);
    const phi = latDeg * Math.PI / 180.0;
    const dec = sunDec * Math.PI / 180.0;
    const altRad = altDeg * Math.PI / 180.0;
    const denom = Math.cos(phi) * Math.cos(dec);
    if (Math.abs(denom) < 1e-6) return 12.0;

    let cosH = (Math.sin(altRad) - Math.sin(phi) * Math.sin(dec)) / denom;
    cosH = Math.max(-1.0, Math.min(1.0, cosH));
    const Hdeg = Math.acos(cosH) * 180.0 / Math.PI;
    return isAfternoon ? ((12.0 + Hdeg / 15.0) % 24.0) : (((12.0 - Hdeg / 15.0) % 24.0 + 24.0) % 24.0);
  },

  /**
   * Calculate Asr Prayer Solar Altitude based on midday shadow (Shāfiʿī / Jumhūr)
   */
  calcAsrAltitude(dayOfYear, latDeg = 35.78) {
    const { sunDec } = this.computeSunCoords(dayOfYear);
    const phi = latDeg * Math.PI / 180.0;
    const dec = sunDec * Math.PI / 180.0;
    const aNoon = Math.PI / 2.0 - Math.abs(phi - dec);
    const cotNoon = 1.0 / Math.tan(aNoon);
    const aAsr = Math.atan(1.0 / (cotNoon + 1.0));
    return aAsr * 180.0 / Math.PI;
  },

  /**
   * Identify celestial body sighted along the fiducial line of the Rule
   */
  findObjectUnderRule(ruleAngle, reteAngle, dayOfYear) {
    const sightedRA = (ruleAngle - reteAngle + 720.0) % 360.0;
    const stars = (window.AstroDatabase && window.AstroDatabase.stars) || window.majorStars || [];
    const zodiacNames = (window.AstroDatabase && window.AstroDatabase.zodiac.map(z => z.name)) || window.zodiacNamesAr || [];

    let closestStar = null;
    let minDiff = 999;
    stars.forEach(s => {
      let diff = Math.abs(s.ra - sightedRA);
      if (diff > 180) diff = 360 - diff;
      if (diff < minDiff) {
        minDiff = diff;
        closestStar = s;
      }
    });

    const { lambdaSun } = this.computeSunCoords(dayOfYear);
    let sunDiff = Math.abs(lambdaSun - sightedRA);
    if (sunDiff > 180) sunDiff = 360 - sunDiff;

    if (sunDiff < 5.0) {
      return { type: 'sun', label: 'الشمس المباشرة ☉', nearest: closestStar };
    } else if (minDiff < 6.0 && closestStar) {
      return { type: 'star', label: closestStar.name, nearest: closestStar };
    } else {
      const signIdx = Math.floor(sightedRA / 30.0);
      const degInSign = Math.floor(sightedRA % 30.0);
      return { type: 'zodiac', label: `درجة ${degInSign}° من برج ${zodiacNames[signIdx % 12]}`, nearest: closestStar };
    }
  }
};

// Global Backwards-Compatibility Bindings
window.AstroMath = AstroMath;
window.computeSunCoords = AstroMath.computeSunCoords.bind(AstroMath);
window.clockToSolarTime = AstroMath.clockToSolarTime.bind(AstroMath);
window.dayOfYearToDate = AstroMath.dayOfYearToDate.bind(AstroMath);
window.dateStringToDayOfYear = AstroMath.dateStringToDayOfYear.bind(AstroMath);
window.findObjectUnderRule = function () {
  return AstroMath.findObjectUnderRule(window.ruleAngle, window.reteAngle, window.dayOfYear);
};
