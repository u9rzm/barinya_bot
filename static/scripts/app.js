const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();
/* =========================
   🎨 THEME
========================= */

const themeLink = document.getElementById("theme-style");
// const pixelBlast = new PixelBlast('canvas-container', configs.diamond);
function applyTheme() {
  const isDark = tg.colorScheme === "dark";
  themeLink.href = isDark
    ? "/static/css/dark.css"
    : "/static/css/light.css";
}

applyTheme();
tg.onEvent("themeChanged", applyTheme);

/* =========================
   👤 USER
========================= */

const user = tg.initDataUnsafe?.user || {
  first_name: "Друг"
};;

if (!user) {
  document.body.innerHTML = "<h2>Ошибка Telegram авторизации</h2>";
  throw new Error("No Telegram user");
}




/* =========================
   🔐 AUTH (JWT)
========================= */

async function auth() {
  console.log("🔐 Auth started");
  const stored = localStorage.getItem("token");
  if (stored) {
    console.log("✅ Token found in storage");
    return stored;
  }

  console.log("📡 Fetching new token...");
  try {
    const res = await fetch("/api/auth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ initData: tg.initData })
    });

    if (!res.ok) {
      console.error("❌ Auth failed:", res.status, res.statusText);
      throw new Error("Auth failed");
    }

    const data = await res.json();
    console.log("✅ Auth success");
    localStorage.setItem("token", data.access_token);
    return data.access_token;
  } catch (e) {
    console.error("❌ Auth error:", e);
    throw e;
  }
}

/* =========================
   ⭐ HEADER
========================= */

async function loadHeader(token) {
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
   🚀 BOOTSTRAP
========================= */


function removeSplash() {
  const splash = document.getElementById("splash");
  if (!splash) return;
  splash.remove(); // 🔥 без display:none
}

// ⏱ splash живёт ровно 1.1 сек
setTimeout(removeSplash, 1100);



// основной старт
(async function initApp() {
  console.log("🚀 App init started");
  try {
    const token = await auth();
    console.log("📊 Loading header...");
    await loadHeader(token);
    console.log("📋 Loading menu...");
    await loadMenu(token);
    console.log("✅ All loaded successfully");
  } catch (e) {
    console.error("❌ Init error:", e);
  } finally {
    console.log("🎯 Calling hideLoader");
    hideLoader(); // 💯 В ЛЮБОМ СЛУЧАЕ
  }
})();
