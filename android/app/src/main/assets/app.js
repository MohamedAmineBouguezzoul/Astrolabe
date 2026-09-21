/**
 * Classical Islamic Astrolabe - Web Application Main Entry Point
 * يحمل الوحدات النمطية المنظمة: قاعدة البيانات، المحرك الفلكي، محرك الرسوميات، ومراقب الواجهة
 */
(function () {
  // If modules are already loaded via HTML script tags, skip duplicate loading
  if (window.AstroDatabase && window.AstroMath && window.initAstrolabeInteractions) {
    return;
  }

  // Fallback loader if app.js is included standalone
  const modules = [
    'js/database.js',
    'js/astronomy.js',
    'js/astrolabe.js',
    'js/app.js'
  ];

  modules.forEach(src => {
    const s = document.createElement('script');
    s.src = src;
    s.async = false;
    document.head.appendChild(s);
  });
})();
