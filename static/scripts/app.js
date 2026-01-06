
// Vars

let tg = null;
let user = { first_name: "Друг" };

/* =========================
   🎨 THEME
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
//main
const from_tg = isTelegramWebApp();
console.log("🎨 Theme init started from tg", from_tg);
if (from_tg) {
  tg = window.Telegram.WebApp;
  tg.ready();
  tg.expand();
  console.log("🎨 Theme init started from tg", tg);
  console.log("🎨 Theme init started");
  const themeLink = document.getElementById("theme-style");
  function applyTheme() {
    const isDark = tg.colorScheme === "dark";
    themeLink.href  = isDark ? "/static/css/dark.css" : "/static/css/light.css";
  }
  tg.onEvent("themeChanged", applyTheme);
  applyTheme();
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
   ⭐ loadBalance
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
   🔄 LOADER (HATCH)
========================= */

function showLoader() {
  const loaderElement = document.getElementById("loader");
  if (loaderElement) {
    loaderElement.style.display = "flex";
    loaderElement.innerHTML = `
      <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
        <span class="loader"></span>
        <p style="margin-top: 20px; color: var(--tg-theme-text-color, #e7f976ff); font-size: 16px;"></p>
      </div>
    `;
  }
}

function hideLoader() {
  const loaderElement = document.getElementById("loader");
  const contentElement = document.getElementById("content");
  
  if (loaderElement) {
    loaderElement.style.display = "none";
  }
  if (contentElement) {
    contentElement.style.display = "block";
  }
}

import { getData } from "/static/scripts/get_data.js";
import { loadTopMenu } from "/static/scripts/top-menu.js";
import { loadContent } from "/static/scripts/content.js";
import { loadFooterMenu } from "/static/scripts/footer-menu.js";


// основной старт
(async function initApp() {
  console.log("🚀 App init started");
  
  // Show loader at the beginning
  showLoader();
  
  try {
    await getData();
    loadTopMenu();
    loadFooterMenu();
    loadContent();
    console.log("� Appo init finished") ;
    if (from_tg && tg) {
      user = tg.initDataUnsafe?.user || user;

      console.log("📊 Loading auth...", tg.initData);
      const token = await auth(tg.initData);

      console.log("📊 Loading balance...");
      await loadBalance(token);
    }
  } catch (e) {
    console.error("❌ Init error:", e);
  } finally {
    console.log("✅ All loaded successfully");
    // Hide loader when everything is done
    hideLoader();
  }
})();

