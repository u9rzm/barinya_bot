export function loadFooterMenu() {
  const raw = localStorage.getItem("data");
  if (!raw) return;

  const data = JSON.parse(raw);

  const footerMenu = document.getElementById("footer-menu");
  const catWrap = document.getElementById("footer-categories");
  const subWrap = document.getElementById("footer-subcategories");

  if (!footerMenu || !catWrap || !subWrap) return;

  catWrap.innerHTML = "";
  subWrap.innerHTML = "";

  let lastScrollY = window.scrollY;
  let visible = false;
  let showTimeout = null;

  // ---------- build categories ----------
  Object.entries(data).forEach(([category, subs], index) => {
    const catId = category.replace(/\s/g, "_");

    const catEl = document.createElement("div");
    catEl.className = "footer-category";

    // === ICON ===
    const icon = document.createElement("div");
    icon.className = "icon-mask";
    const iconUrl = `../img/icons/icon_${catId}_bk.svg`;
    icon.style.setProperty("--icon-mask", `url("${iconUrl}")`);
    console.log(iconUrl);
    catEl.appendChild(icon);

/* заглушка, если иконки временно нет */
// catEl.textContent = category[0];


    // === icon stub ===
    // catEl.innerHTML = "🔲";

    catEl.onclick = e => {
      e.stopPropagation();
      const OFFSET = 180;
      const categoryId = `${category}`.replace(/\s/g, "_");

      // 1. скроллимся сразу
      const target = document.getElementById(categoryId);
        if (!target) return;

        const y =
          target.getBoundingClientRect().top +
          window.pageYOffset -
          OFFSET;

        window.scrollTo({
          top: y,
          behavior: "smooth",
        });

      // 2. сохраняем активную категорию
      localStorage.setItem("activeCategory", category);

      // 3. рендерим подкатегории в header
      // renderHeaderSubcategories(category, subs);
    };


    catWrap.appendChild(catEl);

    // staggered animation
    setTimeout(() => catEl.classList.add("show"), index * 120);
  });

  // ---------- subcategories ----------
  function renderSubcategories(category, subs) {
    subWrap.innerHTML = "";

  Object.keys(subs).forEach(sub => {
    const subEl = document.createElement("div");
    subEl.className = "footer-subcategory";
    subEl.textContent = sub;

    subEl.onclick = () => {
      const id = `${category}_${sub}`.replace(/\s/g, "_");
      document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
    };

    subWrap.appendChild(subEl);

      // low-level categories
      if (typeof low === "object" && !Array.isArray(low)) {
        Object.keys(low)
          .filter(key => key !== "items")
          .forEach(lowSub => {
            const lowEl = document.createElement("div");
            lowEl.className = "footer-subcategory";
            lowEl.textContent = lowSub;

        lowEl.onclick = () => {
          const id = `${category}_${sub}_${lowSub}`.replace(/\s/g, "_");
          document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
      };

      subWrap.appendChild(lowEl);
    });
}

    });
  }

  // ---------- visibility ----------
  function showMenu() {
    if (visible) return;
    visible = true;
    footerMenu.style.pointerEvents = "auto";

    [...catWrap.children].forEach((el, i) => {
      setTimeout(() => el.classList.add("show"), i * 120);
    });
  }

  function hideMenu() {
    if (!visible) return;
    visible = false;
    footerMenu.style.pointerEvents = "none";

    [...catWrap.children].forEach(el => {
      el.classList.remove("show");
    });

    subWrap.innerHTML = "";
  }

  // ---------- scroll logic ----------
  window.addEventListener("scroll", () => {
    const currentY = window.scrollY;

    if (currentY > lastScrollY + 7) {
      hideMenu();
    } else if (currentY < lastScrollY - 7) {
      showMenu();
    }

    lastScrollY = currentY;
    clearTimeout(showTimeout);
  });

  // ---------- idle show ----------
  showTimeout = setTimeout(showMenu, 3000);
}
