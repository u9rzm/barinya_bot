(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const n of document.querySelectorAll('link[rel="modulepreload"]'))s(n);new MutationObserver(n=>{for(const i of n)if(i.type==="childList")for(const a of i.addedNodes)a.tagName==="LINK"&&a.rel==="modulepreload"&&s(a)}).observe(document,{childList:!0,subtree:!0});function o(n){const i={};return n.integrity&&(i.integrity=n.integrity),n.referrerPolicy&&(i.referrerPolicy=n.referrerPolicy),n.crossOrigin==="use-credentials"?i.credentials="include":n.crossOrigin==="anonymous"?i.credentials="omit":i.credentials="same-origin",i}function s(n){if(n.ep)return;n.ep=!0;const i=o(n);fetch(n.href,i)}})();async function L(){localStorage.removeItem("data");try{const e=await fetch("./data/menu.json");if(!e.ok)throw new Error(e.status);const t=await e.json();return localStorage.setItem("data",JSON.stringify(t)),t}catch(e){return console.error("fetch error:",e),null}}function k(e){function t(o){o.items&&!Array.isArray(o.items)&&(o.items=Object.values(o.items)),Object.values(o).forEach(s=>{typeof s=="object"&&s!==null&&t(s)})}return t(e),e}function C(){const e=document.getElementById("menu");if(!e)return;const t=localStorage.getItem("data");if(!t)return;const o=k(JSON.parse(t));e.innerHTML="",e.addEventListener("click",s=>{const n=s.target.closest(".item-name");if(!n||!e.contains(n))return;const i=n.closest(".item");e.querySelectorAll(".item.open").forEach(a=>{a!==i&&a.classList.remove("open")}),i.classList.toggle("open")}),Object.entries(o).forEach(([s,n])=>{const i=s.replace(/\s/g,"_"),a=document.createElement("section");a.id=i;const l=document.createElement("div");l.className="category-header";const c=document.createElement("div");c.className="imgCat",c.style.setProperty("--imgCat",'url("../img/category.svg")');const f=document.createElement("h2");f.textContent=s;const r=document.createElement("div");r.className="imgCat",r.style.setProperty("--imgCat",'url("../img/category.svg")'),l.append(c,f,r),a.appendChild(l),Object.entries(n).forEach(([u,p])=>{const d=document.createElement("h3");d.textContent=u;const m=document.createElement("div");m.className="subImg",m.style.setProperty("--subImg",'url("../img/subcategory.svg")'),a.append(d,m),w(p,a,4)}),e.appendChild(a)})}function w(e,t,o){Object.entries(e).forEach(([s,n])=>{if(s==="items"){n.forEach(a=>{t.insertAdjacentHTML("beforeend",`
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
          `)});return}const i=document.createElement(`h${o}`);i.textContent=s,t.appendChild(i),w(n,t,Math.min(o+1,6))})}function I(){const e=localStorage.getItem("data");if(!e)return;const t=JSON.parse(e),o=document.getElementById("footer-menu"),s=document.getElementById("footer-categories"),n=document.getElementById("footer-subcategories");if(!o||!s||!n)return;s.innerHTML="",n.innerHTML="";let i=window.scrollY,a=!1,l=null;Object.entries(t).forEach(([r,u],p)=>{const d=r.replace(/\s/g,"_"),m=document.createElement("div");m.className="footer-category";const h=document.createElement("div");h.className="icon-mask";const g=`../img/icons/icon_${d}_bk.svg`;h.style.setProperty("--icon-mask",`url("${g}")`),console.log(g),m.appendChild(h),m.onclick=b=>{b.stopPropagation();const E=180,x=`${r}`.replace(/\s/g,"_"),y=document.getElementById(x);if(!y)return;const T=y.getBoundingClientRect().top+window.pageYOffset-E;window.scrollTo({top:T,behavior:"smooth"}),localStorage.setItem("activeCategory",r)},s.appendChild(m),setTimeout(()=>m.classList.add("show"),p*120)});function c(){a||(a=!0,o.style.pointerEvents="auto",[...s.children].forEach((r,u)=>{setTimeout(()=>r.classList.add("show"),u*120)}))}function f(){a&&(a=!1,o.style.pointerEvents="none",[...s.children].forEach(r=>{r.classList.remove("show")}),n.innerHTML="")}window.addEventListener("scroll",()=>{const r=window.scrollY;r>i+7?f():r<i-7&&c(),i=r,clearTimeout(l)}),l=setTimeout(c,3e3)}const _="modulepreload",A=function(e){return"/"+e},v={},S=function(t,o,s){let n=Promise.resolve();if(o&&o.length>0){let f=function(r){return Promise.all(r.map(u=>Promise.resolve(u).then(p=>({status:"fulfilled",value:p}),p=>({status:"rejected",reason:p}))))};var a=f;document.getElementsByTagName("link");const l=document.querySelector("meta[property=csp-nonce]"),c=l?.nonce||l?.getAttribute("nonce");n=f(o.map(r=>{if(r=A(r),r in v)return;v[r]=!0;const u=r.endsWith(".css"),p=u?'[rel="stylesheet"]':"";if(document.querySelector(`link[href="${r}"]${p}`))return;const d=document.createElement("link");if(d.rel=u?"stylesheet":_,u||(d.as="script"),d.crossOrigin="",d.href=r,c&&d.setAttribute("nonce",c),document.head.appendChild(d),u)return new Promise((m,h)=>{d.addEventListener("load",m),d.addEventListener("error",()=>h(new Error(`Unable to preload CSS for ${r}`)))})}))}function i(l){const c=new Event("vite:preloadError",{cancelable:!0});if(c.payload=l,window.dispatchEvent(c),!c.defaultPrevented)throw l}return n.then(l=>{for(const c of l||[])c.status==="rejected"&&i(c.reason);return t().catch(i)})},B=window.Telegram?.WebApp||null,P=window.TON_CONNECT_UI?.TonConnectUI||null,M="https://via.placeholder.com/64",N="ru";async function j(e){console.log("🔐 Auth started");const t=localStorage.getItem("access_token");if(t){if((await fetch("./api/auth/user/check",{method:"GET",headers:{Authorization:`Bearer ${t}`}})).ok)return t;localStorage.removeItem("access_token")}if(!e)throw new Error("initData is empty");console.log(e);const o=await fetch("./api/auth/user",{method:"GET",headers:{Authorization:`TMA ${e}`},cache:"no-store"});if(!o.ok)throw new Error("Auth failed");console.log(o);const s=o.ok?await o.json():null;return localStorage.setItem("access_token",s.user.access_token),localStorage.setItem("loyalty_points",s.user.loyalty_points),localStorage.setItem("loyalty_level_id",s.user.loyalty_level_id),s.access_token}const O={tg:B,ton:null,tonUI:P,wallet:null,config:{},async init(e={}){this.config=e,this.injectSVG(),this.injectStyles(),this.renderHTML(),this.initTelegram(),this.initAuthFromBack(),this.initAvatar(),this.initTon(),this.bindEvents()},injectSVG(){document.body.insertAdjacentHTML("beforeend",`
      <svg style="display:none">
        <symbol id="pm-qr" viewBox="0 0 24 24">
          <rect x="3" y="3" width="7" height="7" stroke="currentColor" fill="none" stroke-width="2"/>
          <rect x="14" y="3" width="7" height="7" stroke="currentColor" fill="none" stroke-width="2"/>
          <rect x="3" y="14" width="7" height="7" stroke="currentColor" fill="none" stroke-width="2"/>
          <rect x="14" y="14" width="7" height="7" stroke="currentColor" fill="none" stroke-width="2"/>
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
      `)},updateProfileLabel(){const e=document.querySelector(".pm-label");e&&(this.wallet?(this.wallet.account.address,e.textContent=this.tg?.initDataUnsafe?.user?.first_name||"Профиль"):e.textContent=this.tg?.initDataUnsafe?.user?.first_name||"Профиль")},initTelegram(){this.tg?.ready(),this.tg?.requestFullscreen(),this.tg?.lockOrientation(),this.tg?.expand(),this.tg?.SettingsButton.hide()},initAuthFromBack(){const e=j(this.tg?.initData);console.log("Auth data : ",e)},initAvatar(){document.getElementById("pmAvatar").src=localStorage.getItem("profile_avatar")||this.tg?.initDataUnsafe?.user?.photo_url||M},async initTon(){return this.ton?!0:this.config.tonManifestUrl?this.tonUI?(this.ton=new this.tonUI({manifestUrl:this.config.tonManifestUrl,language:N}),this.ton.onStatusChange(e=>{const t=this.wallet;this.wallet=e,this.updateProfileLabel(),console.log("[TON] wallet:",e),e&&this.handleWalletConnection(e),!e&&t&&this.handleWalletDisconnection(t)}),!0):(console.error("[TON] TonConnectUI not loaded"),!1):(console.error("[TON] manifestUrl missing"),!1)},async handleWalletConnection(e){try{const t=e.account.address,o=localStorage.getItem("access_token");if(!o){console.warn("[WALLET] No access token found");return}console.log("[WALLET] Sending connection request for address:",t);const s=await fetch(`./api/wallet/connect?address=${encodeURIComponent(t)}`,{method:"GET",headers:{Authorization:`Bearer ${o}`,"Content-Type":"application/json"}});if(s.ok){const n=await s.json();console.log("[WALLET] Connection successful:",n),n.loyalty_points&&localStorage.setItem("loyalty_points",n.loyalty_points),n.loyalty_level_id&&localStorage.setItem("loyalty_level_id",n.loyalty_level_id),this.updateProfileLabel()}else console.error("[WALLET] Connection request failed:",s.status,s.statusText)}catch(t){console.error("[WALLET] Error during connection request:",t)}},async handleWalletDisconnection(e){try{const t=e.account.address,o=localStorage.getItem("access_token");if(!o){console.warn("[WALLET] No access token found");return}console.log("[WALLET] Sending disconnection request for address:",t);const s=await fetch("./api/wallet/disconnect?",{method:"GET",headers:{Authorization:`Bearer ${o}`,"Content-Type":"application/json"}});if(s.ok){const n=await s.json();console.log("[WALLET] Disconnection successful:",n),n.loyalty_points&&localStorage.setItem("loyalty_points",n.loyalty_points),n.loyalty_level_id&&localStorage.setItem("loyalty_level_id",n.loyalty_level_id),this.updateProfileLabel()}else console.error("[WALLET] Disconnection request failed:",s.status,s.statusText)}catch(t){console.error("[WALLET] Error during disconnection request:",t)}},showWalletModal(){if(!this.wallet)return;const e=this.wallet.account.address,t=document.createElement("div");t.className="pm-modal",t.innerHTML=`
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
  `,t.onclick=o=>{o.target===t&&t.remove()},document.body.appendChild(t),t.querySelector("#pmDisconnect").onclick=async()=>{await this.ton.disconnect(),this.wallet=null,t.remove()},t.querySelector("#pmReconnect").onclick=async()=>{await this.ton.disconnect(),t.remove(),await this.ton.connectWallet()}},async showQR(){const e=this.wallet?this.wallet.account.address:`tg://user?id=${this.tg?.initDataUnsafe?.user?.id}`,t=await this.generateSVGQR(e),o=document.createElement("div");o.className="pm-modal",o.appendChild(t),o.onclick=()=>o.remove(),document.body.appendChild(o)},async generateSVGQR(e,t=220){const s=await(await S(()=>import("https://cdn.jsdelivr.net/npm/qrcode@1.5.4/+esm"),[])).toString(e,{type:"svg",width:t,margin:1}),n=document.createElement("div");return n.innerHTML=s,n.firstChild},bindEvents(){const e=document.getElementById("pmContainer"),t=document.getElementById("pmBtn");t.onclick=()=>{e.classList.toggle("active"),t.classList.toggle("active")},document.getElementById("pmWallet").onclick=async o=>{if(o.stopPropagation(),this.wallet)this.showWalletModal();else try{await this.ton.connectWallet()}catch(s){console.warn("[TON] connect canceled",s)}},document.getElementById("pmQr").onclick=o=>{o.stopPropagation(),this.showQR()}}};function W(){const e=document.getElementById("loader");e&&(e.style.display="flex",e.innerHTML=`
      <div style="display:flex;flex-direction:column;align-items:center;">
        <span class="loader"></span>
        <p style="margin-top:20px;color:var(--tg-theme-text-color,#e7f976ff);"></p>
      </div>
    `)}function U(){document.getElementById("loader")?.style.setProperty("display","none"),document.getElementById("content")?.style.setProperty("display","block")}(async function(){console.log("🚀 App init started"),W();try{await L(),console.log("Data Inited"),O.init({tonManifestUrl:"https://quantumforge.ton.run/tonconnect-manifest.json"}),console.log("Profile Inited"),document.getElementById("pmBtn"),document.getElementById("pmAvatar"),I(),C(),console.log("✅ App init finished")}catch(t){console.error("❌ Init error:",t)}finally{U()}})();
