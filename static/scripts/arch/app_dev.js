
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
//🚀 BOOTSTRAP*
function removeSplash() {
  const splash = document.getElementById("splash");
  if (!splash) return;
  splash.remove(); // 🔥 без display:none
}
// ⏱ splash живёт ровно 1.1 сек
setTimeout(removeSplash, 1100);
// основной старт
import { getData } from "/static/get_data.js";
import { loadTopMenu } from "/static/top-menu.js";
import { loadContent } from "/static/content.js";
// основной старт
(async function initApp() {
  console.log("🚀 App init started");
  try {
    await getData();
    loadTopMenu();
    loadContent();
    console.log("🚀 App init finished") ;
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
  }
})();

