// app.js
// Vars
let tg = null;
let user = { first_name: "Друг" };

/* =========================
   🧠 HELPERS
========================= */

function isTelegramWebApp() {
  return (
    typeof window !== "undefined" &&
    window.Telegram &&
    window.Telegram.WebApp &&
    typeof window.Telegram.WebApp.initData === "string" &&
    window.Telegram.WebApp.initData.length > 0
  );
}

/* =========================
   🎨 THEME
========================= */

function initTheme() {
  const from_tg = isTelegramWebApp();
  console.log("🎨 Theme init. From TG:", from_tg);

  const themeLink = document.getElementById("theme-style");
  if (!themeLink) {
    console.warn("🎨 theme-style link not found");
    return null;
  }

  // fallback (не Telegram)
  if (!from_tg) {
    themeLink.href = "/static/css/light.css";
    return null;
  }

  tg = window.Telegram.WebApp;
  tg.ready();
  tg.expand();

  const applyTheme = () => {
    const isDark = tg.colorScheme === "dark";
    themeLink.href = isDark
      ? "/static/css/dark.css"
      : "/static/css/light.css";

    console.log("🎨 Theme applied:", isDark ? "dark" : "light");
  };

  tg.onEvent("themeChanged", applyTheme);
  applyTheme();

  return tg;
}

/* =========================
   🔐 AUTH (JWT)
========================= */

async function auth(initData) {
  console.log("🔐 Auth started");

  const stored = localStorage.getItem("token");
  if (stored) return stored;

  if (!initData) {
    throw new Error("initData is empty");
  }

  const res = await fetch("/api/auth", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ initData })
  });

  if (!res.ok) {
    throw new Error("Auth failed");
  }

  const data = await res.json();
  localStorage.setItem("token", data.access_token);
  return data.access_token;
}

/* =========================
   ⭐ BALANCE
========================= */

async function loadBalance(token) {
  const res = await fetch("/api/loyalty/balance", {
    headers: { Authorization: "Bearer " + token }
  });

  if (!res.ok) {
    throw new Error("Failed to load balance");
  }

  const balance = await res.json();

  const userInfo = document.getElementById("user-info");
  userInfo.innerHTML = `
    <div id="user-link">
      ${user.first_name} · ⭐ ${balance.balance}
    </div>
  `;

  document.getElementById("user-link").onclick = () => {
    alert("Профиль в разработке");
  };
}

/* =========================
   🔄 LOADER
========================= */

function showLoader() {
  const loaderElement = document.getElementById("loader");
  if (loaderElement) {
    loaderElement.style.display = "flex";
    loaderElement.innerHTML = `
      <div style="display:flex;flex-direction:column;align-items:center;">
        <span class="loader"></span>
        <p style="margin-top:20px;color:var(--tg-theme-text-color,#e7f976ff);"></p>
      </div>
    `;
  }
}

function hideLoader() {
  document.getElementById("loader")?.style.setProperty("display", "none");
  document.getElementById("content")?.style.setProperty("display", "block");
}

/* =========================
   📦 IMPORTS
========================= */

import { getData } from "/static/scripts/get_data.js";
import { loadContent } from "/static/scripts/content.js";
import { loadFooterMenu } from "/static/scripts/footer-menu.js";
import { ProfileMenu } from "/static/scripts/profile-menu.js";

/* =========================
   🚀 APP INIT
========================= */

(async function initApp() {
  console.log("🚀 App init started");
  showLoader();

  try {
    // 🎨 Theme
    // tg = initTheme();

    // 📦 Data & UI
    await getData();
    
    ProfileMenu.init({
      tonManifestUrl: '/tonconnect-manifest.json'
    });
    document.getElementById('pmBtn')    // ✔️ button
    document.getElementById('pmAvatar') // ✔️ img
    loadFooterMenu();
    loadContent();

    // 🔐 Auth & user data
    if (tg) {
      user = tg.initDataUnsafe?.user || user;
      const token = await auth(tg.initData);
      await loadBalance(token);
    }

    console.log("✅ App init finished");
  } catch (e) {
    console.error("❌ Init error:", e);
  } finally {
    hideLoader();
  }
})();
