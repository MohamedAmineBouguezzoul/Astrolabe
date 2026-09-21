/**
 * Classical Islamic Astrolabe - Astronomical Database & Star Catalog
 * قاعدة البيانات الفلكية وفهرس النجوم ومنازل القمر والبروج
 */

const AstroDatabase = {
  // Geographical & Astronomical Constants (Default: Tangier / طنجة)
  constants: {
    latDeg: 35.78,     // Tangier Latitude (عرض طنجة)
    lonDeg: -5.81,     // Tangier Longitude (طول طنجة)
    obliqDeg: 23.44,   // Obliquity of the Ecliptic (ميل فلك البروج)
    tzOffset: 0.0      // Civil Time Zone GMT+0 (غرينتش)
  },

  // 12 Classical Zodiac Constellations (البروج الاثنا عشر)
  zodiac: [
    { id: 'aries', name: 'الحمل', nameEn: 'Aries', symbol: '♈', startDeg: 0, endDeg: 30, season: 'الربيع' },
    { id: 'taurus', name: 'الثور', nameEn: 'Taurus', symbol: '♉', startDeg: 30, endDeg: 60, season: 'الربيع' },
    { id: 'gemini', name: 'الجوزاء', nameEn: 'Gemini', symbol: '♊', startDeg: 60, endDeg: 90, season: 'الربيع' },
    { id: 'cancer', name: 'السرطان', nameEn: 'Cancer', symbol: '♋', startDeg: 90, endDeg: 120, season: 'الصيف' },
    { id: 'leo', name: 'الأسد', nameEn: 'Leo', symbol: '♌', startDeg: 120, endDeg: 150, season: 'الصيف' },
    { id: 'virgo', name: 'السنبلة', nameEn: 'Virgo', symbol: '♍', startDeg: 150, endDeg: 180, season: 'الصيف' },
    { id: 'libra', name: 'الميزان', nameEn: 'Libra', symbol: '♎', startDeg: 180, endDeg: 210, season: 'الخريف' },
    { id: 'scorpio', name: 'العقرب', nameEn: 'Scorpio', symbol: '♏', startDeg: 210, endDeg: 240, season: 'الخريف' },
    { id: 'sagittarius', name: 'القوس', nameEn: 'Sagittarius', symbol: '♐', startDeg: 240, endDeg: 270, season: 'الخريف' },
    { id: 'capricorn', name: 'الجدي', nameEn: 'Capricorn', symbol: '♑', startDeg: 270, endDeg: 300, season: 'الشتاء' },
    { id: 'aquarius', name: 'الدلو', nameEn: 'Aquarius', symbol: '♒', startDeg: 300, endDeg: 330, season: 'الشتاء' },
    { id: 'pisces', name: 'الحوت', nameEn: 'Pisces', symbol: '♓', startDeg: 330, endDeg: 360, season: 'الشتاء' }
  ],

  // 28 Classical Arabic Lunar Mansions (منازل القمر الثمانية والعشرون)
  mansions: [
    { index: 1, name: 'الشرطان', star: 'Sheratan', raApprox: 28.66 },
    { index: 2, name: 'البطين', star: 'Botein', raApprox: 42.50 },
    { index: 3, name: 'الثريا', star: 'Alcyone / Pleiades', raApprox: 56.87 },
    { index: 4, name: 'الدبران', star: 'Aldebaran', raApprox: 68.98 },
    { index: 5, name: 'الهقعة', star: 'Meissa', raApprox: 83.78 },
    { index: 6, name: 'الهنعة', star: 'Alhena', raApprox: 99.43 },
    { index: 7, name: 'الذراع', star: 'Procyon / Castor', raApprox: 114.83 },
    { index: 8, name: 'النثرة', star: 'Praesepe', raApprox: 131.17 },
    { index: 9, name: 'الطرف', star: 'Subra', raApprox: 146.46 },
    { index: 10, name: 'الجبهة', star: 'Algieba / Regulus', raApprox: 154.99 },
    { index: 11, name: 'الزبرة', star: 'Zosma', raApprox: 168.53 },
    { index: 12, name: 'الصرفة', star: 'Denebola', raApprox: 177.26 },
    { index: 13, name: 'العواء', star: 'Zavijava', raApprox: 177.67 },
    { index: 14, name: 'السماك', star: 'Spica', raApprox: 201.30 },
    { index: 15, name: 'الغفر', star: 'Syrma', raApprox: 214.00 },
    { index: 16, name: 'الزبانى', star: 'Zubeneschamali', raApprox: 229.25 },
    { index: 17, name: 'الإكليل', star: 'Acrab', raApprox: 241.36 },
    { index: 18, name: 'القلب', star: 'Antares', raApprox: 247.35 },
    { index: 19, name: 'الشولة', star: 'Shaula', raApprox: 263.40 },
    { index: 20, name: 'النعائم', star: 'Nunki', raApprox: 283.82 },
    { index: 21, name: 'البلدة', star: 'Al-Balda', raApprox: 294.00 },
    { index: 22, name: 'سعد الذابح', star: 'Dabih', raApprox: 305.25 },
    { index: 23, name: 'سعد بلع', star: 'Albali', raApprox: 311.92 },
    { index: 24, name: 'سعد السعود', star: 'Sadalsuud', raApprox: 322.89 },
    { index: 25, name: 'سعد الأخبية', star: 'Sadachbia', raApprox: 335.41 },
    { index: 26, name: 'الفرغ المقدم', star: 'Alpheratz', raApprox: 2.10 },
    { index: 27, name: 'الفرغ المؤخر', star: 'Markab', raApprox: 346.19 },
    { index: 28, name: 'الرشاء', star: 'Alrescha', raApprox: 30.51 }
  ],

  // Solar Calendar Months & Days (الشهور الشمسية)
  calendar: {
    months: [
      { name: 'يناير', days: 31 },
      { name: 'فبراير', days: 28 },
      { name: 'مارس', days: 31 },
      { name: 'أبريل', days: 30 },
      { name: 'مايو', days: 31 },
      { name: 'يونيو', days: 30 },
      { name: 'يوليو', days: 31 },
      { name: 'أغسطس', days: 31 },
      { name: 'سبتمبر', days: 30 },
      { name: 'أكتوبر', days: 31 },
      { name: 'نوفمبر', days: 30 },
      { name: 'ديسمبر', days: 31 }
    ],
    // Key Astronomical Presets (Day of Year)
    presets: {
      springEquinox: 80,   // March 21 (الاعتدال الربيعي)
      summerSolstice: 172, // June 21 (الانقلاب الصيفي)
      autumnEquinox: 266,  // September 23 (الاعتدال الخريفي)
      winterSolstice: 355  // December 21 (الانقلاب الشتوي)
    }
  },

  // Historical & Classical Astrolabe Centers (مراكز الرصد الفلكي التاريخية)
  cities: [
    { name: 'طنجة (المغرب)', lat: 35.78, lon: -5.81, region: 'Morocco' },
    { name: 'مراكش (المغرب)', lat: 31.63, lon: -7.98, region: 'Morocco' },
    { name: 'فاس (المغرب)', lat: 34.03, lon: -5.00, region: 'Morocco' },
    { name: 'قرطبة (الأندلس)', lat: 37.88, lon: -4.78, region: 'Andalusia' },
    { name: 'طليطلة (الأندلس)', lat: 39.86, lon: -4.02, region: 'Andalusia' },
    { name: 'إشبيلية (الأندلس)', lat: 37.38, lon: -5.98, region: 'Andalusia' },
    { name: 'القاهرة (مصر)', lat: 30.04, lon: 31.23, region: 'Egypt' },
    { name: 'دمشق (الشام)', lat: 33.51, lon: 36.29, region: 'Levant' },
    { name: 'بغداد (العراق)', lat: 33.31, lon: 44.36, region: 'Mesopotamia' },
    { name: 'سمرقند (آسيا الوسطى)', lat: 39.65, lon: 66.97, region: 'Central Asia' },
    { name: 'مكة المكرمة', lat: 21.42, lon: 39.82, region: 'Hijaz' },
    { name: 'المدينة المنورة', lat: 24.47, lon: 39.61, region: 'Hijaz' },
    { name: 'إسطنبول (القسطنطينية)', lat: 41.01, lon: 28.97, region: 'Turkey' }
  ],

  // Fixed Star Catalog on the Rete (فهرس النجوم الثابتة على شبكة الأسطرلاب)
  stars: [
    { id: 'betelgeuse', name: 'يد الجوزاء (Betelgeuse)', ra: 88.79, dec: 7.41, mag: 0.5, mansion: '' },
    { id: 'rigel', name: 'رجل الجوزاء (Rigel)', ra: 78.63, dec: -8.20, mag: 0.13, mansion: '' },
    { id: 'bellatrix', name: 'المرزم (Bellatrix)', ra: 81.28, dec: 6.35, mag: 1.64, mansion: '' },
    { id: 'aldebaran', name: 'الدبران (Aldebaran) - منزلة 4', ra: 68.98, dec: 16.51, mag: 0.85, mansion: 'الدبران' },
    { id: 'capella', name: 'العيوق (Capella)', ra: 79.17, dec: 45.99, mag: 0.08, mansion: '' },
    { id: 'sirius', name: 'الشعرى اليمانية (Sirius)', ra: 101.29, dec: -16.72, mag: -1.46, mansion: '' },
    { id: 'procyon', name: 'الشعرى الشامية (Procyon) - منزلة 7 الذراع', ra: 114.83, dec: 5.22, mag: 0.38, mansion: 'الذراع' },
    { id: 'pollux', name: 'رأس التوأم المؤخر (Pollux)', ra: 116.33, dec: 28.03, mag: 1.14, mansion: '' },
    { id: 'castor', name: 'رأس التوأم المقدم (Castor)', ra: 113.65, dec: 31.89, mag: 1.58, mansion: '' },
    { id: 'alhena', name: 'الهنعة (Alhena) - منزلة 6', ra: 99.43, dec: 16.40, mag: 1.93, mansion: 'الهنعة' },
    { id: 'meissa', name: 'ميسان (Meissa) - منزلة 5 الهقعة', ra: 83.78, dec: 9.93, mag: 3.39, mansion: 'الهقعة' },
    { id: 'alcyone', name: 'الثريا (Alcyone) - منزلة 3', ra: 56.87, dec: 24.11, mag: 2.85, mansion: 'الثريا' },
    { id: 'hamal', name: 'الناطح (Hamal)', ra: 31.79, dec: 23.46, mag: 2.01, mansion: '' },
    { id: 'sheratan', name: 'الشرطان (Sheratan) - منزلة 1', ra: 28.66, dec: 20.81, mag: 2.64, mansion: 'الشرطان' },
    { id: 'botein', name: 'البطين (Botein) - منزلة 2', ra: 42.50, dec: 27.26, mag: 3.61, mansion: 'البطين' },
    { id: 'praesepe', name: 'النثرة (Asellus / Praesepe) - منزلة 8', ra: 131.17, dec: 18.15, mag: 3.94, mansion: 'النثرة' },
    { id: 'subra', name: 'الطرف (Subra) - منزلة 9', ra: 146.46, dec: 23.77, mag: 2.97, mansion: 'الطرف' },
    { id: 'algieba', name: 'الجبهة (Algieba) - منزلة 10', ra: 154.99, dec: 19.84, mag: 2.01, mansion: 'الجبهة' },
    { id: 'regulus', name: 'قلب الأسد (Regulus) - منزلة 10', ra: 152.09, dec: 11.97, mag: 1.36, mansion: 'الجبهة' },
    { id: 'zosma', name: 'الزبرة (Zosma) - منزلة 11', ra: 168.53, dec: 20.52, mag: 2.56, mansion: 'الزبرة' },
    { id: 'denebola', name: 'الصرفة (Denebola) - منزلة 12', ra: 177.26, dec: 14.57, mag: 2.14, mansion: 'الصرفة' },
    { id: 'zavijava', name: 'العواء (Zavijava) - منزلة 13', ra: 177.67, dec: 1.76, mag: 3.59, mansion: 'العواء' },
    { id: 'spica', name: 'السماك الأعزل (Spica) - منزلة 14', ra: 201.30, dec: -11.16, mag: 0.98, mansion: 'السماك' },
    { id: 'syrma', name: 'الغفر (Syrma) - منزلة 15', ra: 214.00, dec: -6.00, mag: 4.07, mansion: 'الغفر' },
    { id: 'zubeneschamali', name: 'الزبانى الشمالي (Zubeneschamali) - منزلة 16', ra: 229.25, dec: -9.38, mag: 2.61, mansion: 'الزبانى' },
    { id: 'acrab', name: 'الإكليل (Acrab) - منزلة 17', ra: 241.36, dec: -19.81, mag: 2.56, mansion: 'الإكليل' },
    { id: 'antares', name: 'قلب العقرب (Antares) - منزلة 18', ra: 247.35, dec: -26.43, mag: 0.96, mansion: 'القلب' },
    { id: 'shaula', name: 'الشولة (Shaula) - منزلة 19', ra: 263.40, dec: -37.10, mag: 1.62, mansion: 'الشولة' },
    { id: 'nunki', name: 'النعائم (Nunki) - منزلة 20', ra: 283.82, dec: -26.30, mag: 2.05, mansion: 'النعائم' },
    { id: 'dabih', name: 'سعد الذابح (Dabih) - منزلة 22', ra: 305.25, dec: -14.78, mag: 3.05, mansion: 'سعد الذابح' },
    { id: 'albali', name: 'سعد بلع (Albali) - منزلة 23', ra: 311.92, dec: -9.50, mag: 3.78, mansion: 'سعد بلع' },
    { id: 'sadalsuud', name: 'سعد السعود (Sadalsuud) - منزلة 24', ra: 322.89, dec: -5.57, mag: 2.90, mansion: 'سعد السعود' },
    { id: 'sadachbia', name: 'سعد الأخبية (Sadachbia) - منزلة 25', ra: 335.41, dec: -1.39, mag: 3.86, mansion: 'سعد الأخبية' },
    { id: 'alpheratz', name: 'الفرغ المقدم (Alpheratz) - منزلة 26', ra: 2.10, dec: 29.09, mag: 2.07, mansion: 'الفرغ المقدم' },
    { id: 'markab', name: 'الفرغ المؤخر (Markab) - منزلة 27', ra: 346.19, dec: 15.21, mag: 2.49, mansion: 'الفرغ المؤخر' },
    { id: 'alrescha', name: 'الرشاء (Alrescha) - منزلة 28', ra: 30.51, dec: 2.76, mag: 3.82, mansion: 'الرشاء' },
    { id: 'arcturus', name: 'السماك الرامح (Arcturus)', ra: 213.92, dec: 19.18, mag: -0.05, mansion: '' },
    { id: 'alphecca', name: 'نير الفكة (Alphecca)', ra: 233.67, dec: 26.71, mag: 2.22, mansion: '' },
    { id: 'vega', name: 'النسر الواقع (Vega)', ra: 279.23, dec: 38.78, mag: 0.03, mansion: '' },
    { id: 'altair', name: 'النسر الطائر (Altair)', ra: 297.70, dec: 8.87, mag: 0.77, mansion: '' },
    { id: 'deneb', name: 'ذنب الدجاجة (Deneb)', ra: 310.36, dec: 45.28, mag: 1.25, mansion: '' },
    { id: 'rasalhague', name: 'رأس الحواء (Rasalhague)', ra: 263.73, dec: 12.56, mag: 2.08, mansion: '' },
    { id: 'polaris', name: 'نجم القطب (Polaris)', ra: 37.95, dec: 89.26, mag: 1.98, mansion: '' },
    { id: 'algol', name: 'رأس الغول (Algol)', ra: 47.11, dec: 40.96, mag: 2.12, mansion: '' }
  ]
};

// Global Backwards-Compatibility Aliases
window.AstroDatabase = AstroDatabase;
window.majorStars = AstroDatabase.stars;
window.zodiacNamesAr = AstroDatabase.zodiac.map(z => z.name);
window.mansionsAr = AstroDatabase.mansions.map(m => m.name);
window.monthNamesAr = AstroDatabase.calendar.months.map(m => m.name);
window.monthDays = AstroDatabase.calendar.months.map(m => m.days);
window.latDeg = AstroDatabase.constants.latDeg;
window.obliqDeg = AstroDatabase.constants.obliqDeg;
