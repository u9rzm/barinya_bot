// app.js

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


import { getData } from "./scripts/get_data.js";
import { loadContent } from "./scripts/content.js";
import { loadFooterMenu } from "./scripts/footer-menu.js";
import { ProfileMenu } from "./scripts/profile.js";
import './css/base.css'
import './css/header.css'
import './css/menu.css'
import './css/content.css'
import './css/footer.css'
import './css/dark.css'
import './css/loader.css'

/* =========================
   🚀 APP INIT
========================= */

(async function initApp() {
  console.log("🚀 App init started");
  showLoader();

  try {
    // 📦 Data & UI
    await getData();
    console.log("Data Inited")
    ProfileMenu.init({
      tonManifestUrl: 'https://quantumforge.ton.run/tonconnect-manifest.json'
    });
    console.log("Profile Inited")
    document.getElementById('pmBtn')    // ✔️ button
    document.getElementById('pmAvatar') // ✔️ img
    loadFooterMenu();
    loadContent();

    console.log("✅ App init finished");
  } catch (e) {
    console.error("❌ Init error:", e);
  } finally {
    hideLoader();
  }
})();
