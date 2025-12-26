(function () {
  const VERSION_URL = "/static/version.txt";
  const FALLBACK_VERSION = Date.now().toString();

  function loadVersionSync() {
    const xhr = new XMLHttpRequest();
    try {
      xhr.open("GET", VERSION_URL + "?_=" + Date.now(), false); // sync
      xhr.send(null);
      if (xhr.status === 200) {
        return xhr.responseText.trim();
      }
    } catch (e) {}
    return FALLBACK_VERSION;
  }

  const version = loadVersionSync();
  console.log("🔄 Cache version:", version);

  window.__CACHE_VERSION__ = version;

  // 🔥 Переподключаем ВСЕ JS с версией
  document.querySelectorAll("script[data-cache]").forEach(script => {
    const src = script.getAttribute("data-src");
    if (src) {
      script.src = `${src}?v=${version}`;
    }
  });

  // 🔥 Переподключаем CSS
  document.querySelectorAll("link[data-cache]").forEach(link => {
    const href = link.getAttribute("data-href");
    if (href) {
      link.href = `${href}?v=${version}`;
    }
  });
})();
