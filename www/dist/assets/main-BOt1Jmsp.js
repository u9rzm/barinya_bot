(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const o of document.querySelectorAll('link[rel="modulepreload"]'))i(o);new MutationObserver(o=>{for(const r of o)if(r.type==="childList")for(const a of r.addedNodes)a.tagName==="LINK"&&a.rel==="modulepreload"&&i(a)}).observe(document,{childList:!0,subtree:!0});function n(o){const r={};return o.integrity&&(r.integrity=o.integrity),o.referrerPolicy&&(r.referrerPolicy=o.referrerPolicy),o.crossOrigin==="use-credentials"?r.credentials="include":o.crossOrigin==="anonymous"?r.credentials="omit":r.credentials="same-origin",r}function i(o){if(o.ep)return;o.ep=!0;const r=n(o);fetch(o.href,r)}})();async function C(){localStorage.removeItem("data");try{const e=await fetch("./data/menu.json");if(!e.ok)throw new Error(e.status);const t=await e.json();return localStorage.setItem("data",JSON.stringify(t)),t}catch(e){return console.error("fetch error:",e),null}}function I(e){function t(n){n.items&&!Array.isArray(n.items)&&(n.items=Object.values(n.items)),Object.values(n).forEach(i=>{typeof i=="object"&&i!==null&&t(i)})}return t(e),e}function T(){const e=document.getElementById("menu");if(!e)return;const t=localStorage.getItem("data");if(!t)return;const n=I(JSON.parse(t));e.innerHTML="",e.addEventListener("click",i=>{const o=i.target.closest(".item-name");if(!o||!e.contains(o))return;const r=o.closest(".item");e.querySelectorAll(".item.open").forEach(a=>{a!==r&&a.classList.remove("open")}),r.classList.toggle("open")}),Object.entries(n).forEach(([i,o])=>{const r=i.replace(/\s/g,"_"),a=document.createElement("section");a.id=r;const l=document.createElement("div");l.className="category-header";const c=document.createElement("div");c.className="imgCat",c.style.setProperty("--imgCat",'url("../img/category.svg")');const f=document.createElement("h2");f.textContent=i;const s=document.createElement("div");s.className="imgCat",s.style.setProperty("--imgCat",'url("../img/category.svg")'),l.append(c,f,s),a.appendChild(l),Object.entries(o).forEach(([m,p])=>{const d=document.createElement("h3");d.textContent=m;const u=document.createElement("div");u.className="subImg",u.style.setProperty("--subImg",'url("../img/subcategory.svg")'),a.append(d,u),w(p,a,4)}),e.appendChild(a)})}function w(e,t,n){Object.entries(e).forEach(([i,o])=>{if(i==="items"){o.forEach(a=>{t.insertAdjacentHTML("beforeend",`
          <div class="item">
            <div class="item-info">
              <div class="item-name">
                ${a.name}
              </div>
              ${a.description?`<div class="item-description">${a.description}</div>`:""}
            </div>
            <div class="item-price">
              ${a.weight?` ${a.weight} / `:""}${a.price} ₽
            </div>
          </div>
          `)});return}const r=document.createElement(`h${n}`);r.textContent=i,t.appendChild(r),w(o,t,Math.min(n+1,6))})}function S(){const e=localStorage.getItem("data");if(!e)return;const t=JSON.parse(e),n=document.getElementById("footer-menu"),i=document.getElementById("footer-categories"),o=document.getElementById("footer-subcategories");if(!n||!i||!o)return;i.innerHTML="",o.innerHTML="";let r=window.scrollY,a=!1,l=null;Object.entries(t).forEach(([s,m],p)=>{const d=s.replace(/\s/g,"_"),u=document.createElement("div");u.className="footer-category";const h=document.createElement("div");h.className="icon-mask";const g=`../img/icons/icon_${d}_bk.svg`;h.style.setProperty("--icon-mask",`url("${g}")`),console.log(g),u.appendChild(h),u.onclick=b=>{b.stopPropagation();const E=180,x=`${s}`.replace(/\s/g,"_"),y=document.getElementById(x);if(!y)return;const k=y.getBoundingClientRect().top+window.pageYOffset-E;window.scrollTo({top:k,behavior:"smooth"}),localStorage.setItem("activeCategory",s)},i.appendChild(u),setTimeout(()=>u.classList.add("show"),p*120)});function c(){a||(a=!0,n.style.pointerEvents="auto",[...i.children].forEach((s,m)=>{setTimeout(()=>s.classList.add("show"),m*120)}))}function f(){a&&(a=!1,n.style.pointerEvents="none",[...i.children].forEach(s=>{s.classList.remove("show")}),o.innerHTML="")}window.addEventListener("scroll",()=>{const s=window.scrollY;s>r+7?f():s<r-7&&c(),r=s,clearTimeout(l)}),l=setTimeout(c,3e3)}const L="modulepreload",A=function(e){return"/"+e},v={},_=function(t,n,i){let o=Promise.resolve();if(n&&n.length>0){let f=function(s){return Promise.all(s.map(m=>Promise.resolve(m).then(p=>({status:"fulfilled",value:p}),p=>({status:"rejected",reason:p}))))};var a=f;document.getElementsByTagName("link");const l=document.querySelector("meta[property=csp-nonce]"),c=l?.nonce||l?.getAttribute("nonce");o=f(n.map(s=>{if(s=A(s),s in v)return;v[s]=!0;const m=s.endsWith(".css"),p=m?'[rel="stylesheet"]':"";if(document.querySelector(`link[href="${s}"]${p}`))return;const d=document.createElement("link");if(d.rel=m?"stylesheet":L,m||(d.as="script"),d.crossOrigin="",d.href=s,c&&d.setAttribute("nonce",c),document.head.appendChild(d),m)return new Promise((u,h)=>{d.addEventListener("load",u),d.addEventListener("error",()=>h(new Error(`Unable to preload CSS for ${s}`)))})}))}function r(l){const c=new Event("vite:preloadError",{cancelable:!0});if(c.payload=l,window.dispatchEvent(c),!c.defaultPrevented)throw l}return o.then(l=>{for(const c of l||[])c.status==="rejected"&&r(c.reason);return t().catch(r)})},B=window.Telegram?.WebApp||null,M=window.TON_CONNECT_UI?.TonConnectUI||null,O="https://via.placeholder.com/64",P="ru";async function N(e){console.log("🔐 Auth started");const t=localStorage.getItem("access_token");if(t){if((await fetch("https://quantumforge.ton.run/api/auth/check",{method:"GET",headers:{Authorization:`Bearer ${t}`}})).ok)return t;localStorage.removeItem("access_token")}if(!e)throw new Error("initData is empty");console.log(e);const n=await fetch(`https://quantumforge.ton.run/api/auth?initData=${encodeURIComponent(e)}`,{method:"GET",headers:{"Content-Type":"application/json"},cache:"no-store"});if(!n.ok)throw new Error("Auth failed");const i=await n.json();return localStorage.setItem("access_token",i.access_token),localStorage.setItem("loyalty_points",i.loyalty_points),localStorage.setItem("loyalty_level_id",i.loyalty_level_id),i.access_token}const j={tg:B,ton:null,tonUI:M,wallet:null,config:{},async init(e={}){this.config=e,this.injectSVG(),this.injectStyles(),this.renderHTML(),this.initTelegram(),this.initAuthFromBack(),this.initAvatar(),this.initTon(),this.bindEvents()},injectSVG(){document.body.insertAdjacentHTML("beforeend",`
      <svg style="display:none">
        <symbol id="pm-qr" viewBox="0 0 24 24">
          <rect x="3" y="3" width="7" height="7" stroke="currentColor" fill="none" stroke-width="2"/>
          <rect x="14" y="3" width="7" height="7" stroke="currentColor" fill="none" stroke-width="2"/>
          <rect x="3" y="14" width="7" height="7" stroke="currentColor" fill="none" stroke-width="2"/>
        </symbol>

        <symbol id="pm-wallet" viewBox="0 0 24 24">
          <rect x="3" y="6" width="18" height="12" rx="2"
            stroke="currentColor" fill="none" stroke-width="2"/>
          <circle cx="16" cy="12" r="1.5" fill="currentColor"/>
        </symbol>
      </svg>
      `)},injectStyles(){const e=document.createElement("style");e.textContent=`
      .pm-container {
        position: fixed;
        top: calc(var(--tg-safe-area-inset-top) + 60px);
        right: 16px;
        z-index: 2147483647;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        font-family: system-ui;
      }

      .pm-btn {
        height: 36px;
        border-radius: 24px;
        background: #00535E;
        border: 1px;
        border-color: #FAAC6E;
        display: flex;
        align-items: center;
        cursor: pointer;
        overflow: hidden;
        padding-right: 0;
        transition: width .2s ease;
      }

      .pm-btn.active {
        padding-left: 12px;
      }

      .pm-label {
        white-space: nowrap;
        max-width: 0;
        opacity: 0;
        color: #FAAC6E;
        transition: max-width .2s ease;
      }

      .pm-btn.active .pm-label {
        max-width: 200px;
        opacity: 1;
      }

      .pm-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
      }

      .pm-dropdown {
        margin-top: 6px;
        display: flex;
        flex-direction: column;
        gap: 6px;
        opacity: 0;
        transform: translateY(-6px);
        pointer-events: none;
        transition: .2s ease;
      }

      .pm-container.active .pm-dropdown {
        opacity: 1;
        transform: none;
        pointer-events: auto;
      }

      .pm-item {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #2c2c2ea5;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
      }

      .pm-modal {
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,.6);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 999999;
      }

      .pm-modal svg {
        background: #fff;
        padding: 12px;
        border-radius: 12px;
      }
      /* === RESET interactive outlines === */
      .pm-btn,
      .pm-item {
        outline: none;
        border: none;
        box-shadow: none;
      }

      .pm-btn:focus,
      .pm-btn:focus-visible,
      .pm-item:focus,
      .pm-item:focus-visible {
        outline: none;
        box-shadow: none;
      }

      /* Mobile tap highlight */
      .pm-btn,
      .pm-item {
        -webkit-tap-highlight-color: transparent;
      }

      /* SVG inside buttons */
      .pm-btn svg,
      .pm-item svg {
        pointer-events: none;
      }

      /* Prevent ugly focus ring on click */
      :focus:not(:focus-visible) {
        outline: none;
      }        
    `,document.head.appendChild(e)},renderHTML(){document.body.insertAdjacentHTML("beforeend",`
      <div class="pm-container" id="pmContainer">
        <button class="pm-btn" id="pmBtn">
          <span class="pm-label">${this.tg?.initDataUnsafe?.user?.first_name}</span>
          <img class="pm-avatar" id="pmAvatar"/>
        </button>
        <div class="pm-dropdown">
          <div class="pm-item" id="pmQr">
            <svg width="20"><use href="#pm-qr"/></svg>
          </div>
          <div class="pm-item" id="pmWallet">
            <svg width="20"><use href="#pm-wallet"/></svg>
          </div>
        </div>
      </div>
      `)},updateProfileLabel(){const e=document.querySelector(".pm-label");e&&(this.wallet?(this.wallet.account.address,e.textContent=localStorage.getItem("loyalty_points")+" eBall "):e.textContent=this.tg?.initDataUnsafe?.user?.first_name||"Профиль")},initTelegram(){this.tg?.ready(),this.tg?.requestFullscreen(),this.tg?.lockOrientation(),this.tg?.expand(),this.tg?.SettingsButton.hide()},initAuthFromBack(){const e=N(this.tg?.initData);console.log("Auth data : ",e)},initAvatar(){document.getElementById("pmAvatar").src=localStorage.getItem("profile_avatar")||this.tg?.initDataUnsafe?.user?.photo_url||O},async initTon(){return this.ton?!0:this.config.tonManifestUrl?this.tonUI?(this.ton=new this.tonUI({manifestUrl:this.config.tonManifestUrl,language:P}),this.ton.onStatusChange(e=>{this.wallet=e,this.updateProfileLabel(),console.log("[TON] wallet:",e)}),!0):(console.error("[TON] TonConnectUI not loaded"),!1):(console.error("[TON] manifestUrl missing"),!1)},showWalletModal(){if(!this.wallet)return;const e=this.wallet.account.address,t=document.createElement("div");t.className="pm-modal",t.innerHTML=`
    <div style="
      background:#1c1c1e;
      color:#fff;
      padding:16px;
      border-radius:14px;
      width:280px;
      font-size:14px;
    ">
      <div style="margin-bottom:8px; opacity:.7">Подключённый кошелёк</div>

      <div style="
        font-family:monospace;
        word-break:break-all;
        background:#2c2c2e;
        padding:8px;
        border-radius:8px;
        margin-bottom:12px;
      ">
        ${e}
      </div>

      <button id="pmDisconnect" style="
        width:100%;
        padding:10px;
        margin-bottom:8px;
        border-radius:10px;
        border:none;
        background:#ff453a;
        color:#fff;
        cursor:pointer;
      ">
        Отключить
      </button>

      <button id="pmReconnect" style="
        width:100%;
        padding:10px;
        border-radius:10px;
        border:none;
        background:#0a84ff;
        color:#fff;
        cursor:pointer;
      ">
        Подключить другой
      </button>
    </div>
  `,t.onclick=n=>{n.target===t&&t.remove()},document.body.appendChild(t),t.querySelector("#pmDisconnect").onclick=async()=>{await this.ton.disconnect(),this.wallet=null,t.remove()},t.querySelector("#pmReconnect").onclick=async()=>{await this.ton.disconnect(),t.remove(),await this.ton.connectWallet()}},async showQR(){const e=this.wallet?this.wallet.account.address:`tg://user?id=${this.tg?.initDataUnsafe?.user?.id}`,t=await this.generateSVGQR(e),n=document.createElement("div");n.className="pm-modal",n.appendChild(t),n.onclick=()=>n.remove(),document.body.appendChild(n)},async generateSVGQR(e,t=220){const i=await(await _(()=>import("https://cdn.jsdelivr.net/npm/qrcode@1.5.4/+esm"),[])).toString(e,{type:"svg",width:t,margin:1}),o=document.createElement("div");return o.innerHTML=i,o.firstChild},bindEvents(){const e=document.getElementById("pmContainer"),t=document.getElementById("pmBtn");t.onclick=()=>{e.classList.toggle("active"),t.classList.toggle("active")},document.getElementById("pmWallet").onclick=async n=>{if(n.stopPropagation(),this.wallet)this.showWalletModal();else try{await this.ton.connectWallet()}catch(i){console.warn("[TON] connect canceled",i)}},document.getElementById("pmQr").onclick=n=>{n.stopPropagation(),this.showQR()}}};function U(){const e=document.getElementById("loader");e&&(e.style.display="flex",e.innerHTML=`
      <div style="display:flex;flex-direction:column;align-items:center;">
        <span class="loader"></span>
        <p style="margin-top:20px;color:var(--tg-theme-text-color,#e7f976ff);"></p>
      </div>
    `)}function $(){document.getElementById("loader")?.style.setProperty("display","none"),document.getElementById("content")?.style.setProperty("display","block")}(async function(){console.log("🚀 App init started"),U();try{await C(),console.log("Data Inited"),j.init({tonManifestUrl:"https://quantumforge.ton.run/tonconnect-manifest.json"}),console.log("Profile Inited"),document.getElementById("pmBtn"),document.getElementById("pmAvatar"),S(),T(),console.log("✅ App init finished")}catch(t){console.error("❌ Init error:",t)}finally{$()}})();
