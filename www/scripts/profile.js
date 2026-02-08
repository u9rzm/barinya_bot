// profile-menu.js

/* ================== EXTERNAL DEPENDENCIES ================== */

// Telegram
const TG = window.Telegram?.WebApp || null;

// TON
const TonConnectUIClass =
  window.TON_CONNECT_UI?.TonConnectUI || null;

// TON Core (для address utils, если понадобится)




/* ================== CONSTANTS ================== */

const DEFAULT_AVATAR = 'https://via.placeholder.com/64';
const UI_LANG = 'ru';


// AUTH
async function auth(tg_init_data) {
  console.log("🔐 Auth started");

  const stored = localStorage.getItem("access_token");
  if (stored) {
    const check = await fetch("./api/auth/user/check", {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${stored}`,
      },
    });

    if (check.ok) {
      return stored;
    }
    // ❌ токен невалиден
    localStorage.removeItem("access_token");
  }

  if (!tg_init_data) {
    throw new Error("initData is empty");
  }
  console.log(tg_init_data);
  const res = await fetch(`./api/auth/user`,
   {
    method: "GET",
    headers: { "Authorization": `TMA ${tg_init_data}` },
    cache: "no-store"
  });

  if (!res.ok) {
    throw new Error("Auth failed");
  }
  console.log(res);

  const data = res.ok ? await res.json() : null;
  localStorage.setItem("access_token", data.user.access_token);
  localStorage.setItem("loyalty_points", data.user.loyalty_points);
  localStorage.setItem("loyalty_level_id", data.user.loyalty_level_id);
  return data.access_token;
}

/* ================== HELPERS ================== */

function shortenAddress(addr) {
  return addr.slice(0, 4) + '…' + addr.slice(-4);
}

export const ProfileMenu = {
  // external
  tg: TG,
  ton: null,
  tonUI: TonConnectUIClass,
  // state
  wallet: null,
  config: {},
  async init(config = {}) {
    this.config = config;
    this.injectSVG();
    this.injectStyles();
    this.renderHTML();
    this.initTelegram();
    this.initAuthFromBack();
    this.initAvatar();
    this.initTon();
    this.bindEvents();
  },

  /* ---------- SVG ICONS ---------- */
  injectSVG() {
    document.body.insertAdjacentHTML(
      'beforeend',
      `
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
      `
    );
  },

  /* ---------- STYLES ---------- */
  injectStyles() {
    const style = document.createElement('style');
    style.textContent = `
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
    `;
    document.head.appendChild(style);
  },

  /* ---------- HTML ---------- */
  renderHTML() {
    document.body.insertAdjacentHTML(
      'beforeend',
      `
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
      `
    );
  },
  /* ---------- updateProfileLabel ---------- */
  updateProfileLabel() {
    const label = document.querySelector('.pm-label');
    if (!label) return;

    if (this.wallet) {
      const addr = this.wallet.account.address;
      label.textContent = this.tg?.initDataUnsafe?.user?.first_name || 'Профиль';
      // label.textContent = shortenAddress(addr); // 0-4 + … + -4
    } else {
      label.textContent =
        this.tg?.initDataUnsafe?.user?.first_name || 'Профиль';
    }
  },

/* ---------- TELEGRAM ---------- */
initTelegram() {
  this.tg?.ready();
  this.tg?.requestFullscreen();
  this.tg?.lockOrientation();
  this.tg?.expand()
  this.tg?.SettingsButton.hide()
},

initAuthFromBack(){
  const auth_token = auth(this.tg?.initData);
  console.log("Auth data : ", auth_token)
},

initAvatar() {
  document.getElementById('pmAvatar').src =
    localStorage.getItem('profile_avatar') ||
    this.tg?.initDataUnsafe?.user?.photo_url ||
    DEFAULT_AVATAR;
},

/* ---------- TON ---------- */
  async initTon() {
    if (this.ton) return true;

    if (!this.config.tonManifestUrl) {
      console.error('[TON] manifestUrl missing');
      return false;
    }

    if (!this.tonUI) {
      console.error('[TON] TonConnectUI not loaded');
      return false;
    }

    this.ton = new this.tonUI({
      manifestUrl: this.config.tonManifestUrl,
      language: UI_LANG
    });

    this.ton.onStatusChange(wallet => {
      const previousWallet = this.wallet;
      this.wallet = wallet;
      this.updateProfileLabel();
      console.log('[TON] wallet:', wallet);
      
      // Отправляем запрос при подключении кошелька
      if (wallet) {
        this.handleWalletConnection(wallet);
      }
      
      // Отправляем запрос при отключении кошелька
      if (!wallet && previousWallet) {
        this.handleWalletDisconnection(previousWallet);
      }
    });

  return true;
},

/* ---------- WALLET CONNECTION HANDLER ---------- */
async handleWalletConnection(wallet) {
  try {
    const address = wallet.account.address;
    const token = localStorage.getItem("access_token");
    
    if (!token) {
      console.warn('[WALLET] No access token found');
      return;
    }
    console.log('[WALLET] Sending connection request for address:', address);
    
    const response = await fetch(`./api/wallet/connect?address=${encodeURIComponent(address)}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.ok) {
      const data = await response.json();
      console.log('[WALLET] Connection successful:', data);
      
      // Обновляем данные пользователя если они пришли в ответе
      if (data.loyalty_points) {
        localStorage.setItem("loyalty_points", data.loyalty_points);
      }
      if (data.loyalty_level_id) {
        localStorage.setItem("loyalty_level_id", data.loyalty_level_id);
      }
      
      // Обновляем отображение профиля
      this.updateProfileLabel();
    } else {
      console.error('[WALLET] Connection request failed:', response.status, response.statusText);
    }
  } catch (error) {
    console.error('[WALLET] Error during connection request:', error);
  }
},

/* ---------- WALLET DISCONNECTION HANDLER ---------- */
async handleWalletDisconnection(previousWallet) {
  try {
    const address = previousWallet.account.address;
    const token = localStorage.getItem("access_token");
    
    if (!token) {
      console.warn('[WALLET] No access token found');
      return;
    }

    console.log('[WALLET] Sending disconnection request for address:', address);
    
    const response = await fetch(`./api/wallet/disconnect?`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.ok) {
      const data = await response.json();
      console.log('[WALLET] Disconnection successful:', data);
      
      // Обновляем данные пользователя если они пришли в ответе
      if (data.loyalty_points) {
        localStorage.setItem("loyalty_points", data.loyalty_points);
      }
      if (data.loyalty_level_id) {
        localStorage.setItem("loyalty_level_id", data.loyalty_level_id);
      }
      
      // Обновляем отображение профиля
      this.updateProfileLabel();
    } else {
      console.error('[WALLET] Disconnection request failed:', response.status, response.statusText);
    }
  } catch (error) {
    console.error('[WALLET] Error during disconnection request:', error);
  }
},

showWalletModal() {
  if (!this.wallet) return;
  const address = this.wallet.account.address;
  const modal = document.createElement('div');
  modal.className = 'pm-modal';

  modal.innerHTML = `
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
        ${address}
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
  `;

  modal.onclick = e => {
    if (e.target === modal) modal.remove();
  };

  document.body.appendChild(modal);

  // handlers
  modal.querySelector('#pmDisconnect').onclick = async () => {
    await this.ton.disconnect();
    this.wallet = null;
    modal.remove();
  };

  modal.querySelector('#pmReconnect').onclick = async () => {
    await this.ton.disconnect();
    modal.remove();
    await this.ton.connectWallet();
  };
},
  /* ---------- QR ---------- */
  async showQR() {
    const text = this.wallet
      ? this.wallet.account.address
      : `tg://user?id=${this.tg?.initDataUnsafe?.user?.id}`;

    const qr = await this.generateSVGQR(text);

    const modal = document.createElement('div');
    modal.className = 'pm-modal';
    modal.appendChild(qr);
    modal.onclick = () => modal.remove();
    document.body.appendChild(modal);
  },

  async generateSVGQR(text, size = 220) {
    const QR = await import('https://cdn.jsdelivr.net/npm/qrcode@1.5.4/+esm');
    const svgText = await QR.toString(text, {
      type: 'svg',
      width: size,
      margin: 1
    });

    const wrapper = document.createElement('div');
    wrapper.innerHTML = svgText;
    return wrapper.firstChild;
  },

  /* ---------- EVENTS ---------- */
  bindEvents() {
    const c = document.getElementById('pmContainer');
    const b = document.getElementById('pmBtn');

    b.onclick = () => {
      c.classList.toggle('active');
      b.classList.toggle('active');
    };

    document.getElementById('pmWallet').onclick = async e => {
      e.stopPropagation();
      // await this.initTon();

      if (this.wallet) {
        this.showWalletModal();
      } else {
        try {
          await this.ton.connectWallet();
        } catch (e) {
          console.warn('[TON] connect canceled', e);
        }
      }
    };

    document.getElementById('pmQr').onclick = e => {
      e.stopPropagation();
      this.showQR();
    };
  }
};
