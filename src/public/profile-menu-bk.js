// profile-menu.js
export const ProfileMenu = {
  tg: null,
  ton: null,
  wallet: null,
  config: {},

  async init(config = {}) {
    this.config = config;
    this.tg = window.Telegram?.WebApp;
    console.log('[ProfileMenu] init');

    this.injectSVG();
    this.injectStyles();
    this.renderHTML();
    this.initTelegram();
    this.initAvatar();
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
        top: 12px;
        right: 12px;
        z-index: 2147483647;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        font-family: system-ui;
      }

      .pm-btn {
        height: 36px;
        border-radius: 24px;
        background: #1c1c1e73;
        border: none;
        display: flex;
        align-items: center;
        cursor: pointer;
        overflow: hidden;
        padding-right: 0;
        transition: width .25s ease;
      }

      .pm-btn.active {
        padding-left: 12px;
      }

      .pm-label {
        white-space: nowrap;
        max-width: 0;
        opacity: 0;
        color: #fff;
        transition: max-width .25s ease, opacity .2s ease;
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

  /* ---------- TELEGRAM ---------- */
  initTelegram() {
    this.tg?.ready();
  },

  initAvatar() {
    document.getElementById('pmAvatar').src =
      localStorage.getItem('profile_avatar') ||
      this.tg?.initDataUnsafe?.user?.photo_url ||
      'https://via.placeholder.com/64';
  },
  /* ---------- TON ---------- */
async initTon() {
  if (this.ton) return true;

  if (!this.config.tonManifestUrl) {
    console.error('[TON] manifestUrl missing');
    return false;
  }

  if (!window.TON_CONNECT_UI) {
    console.error('[TON] TON_CONNECT_UI not loaded');
    return false;
  }

  const TonConnectUI = window.TON_CONNECT_UI.TonConnectUI;

  this.ton = new TonConnectUI({
    manifestUrl: this.config.tonManifestUrl,
    language: 'ru'
  });

  this.ton.onStatusChange(wallet => {
    this.wallet = wallet;
    const label = document.querySelector('.pm-label');
    if (!label) return;
    if (wallet) {
      const addr = wallet.account.address.toString({bounceable: false});
      label.textContent =
        addr.slice(0, 4) + '…' + addr.slice(-4);
    } else {
      label.textContent = this.tg?.initDataUnsafe?.user?.first_name || 'Профиль';
    }
    console.log('[TON] wallet:', wallet);
  });

  return true;
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
      ? this.wallet.account.addressFriendly
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
      await this.initTon();

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