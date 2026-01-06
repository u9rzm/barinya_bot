export function loadTopMenu() {
  const topMenu = document.getElementById("top-menu");
  const menuBtn = document.getElementById("menu-btn");
  let lastScrollY = 0;

  if (!topMenu || !menuBtn) return;

  const raw = localStorage.getItem("data");
  if (!raw) return;

  const data = JSON.parse(raw);
  topMenu.innerHTML = "";

  let openedSubs = null;

  Object.entries(data).forEach(([category, subs]) => {
    const catId = category.replace(/\s/g, "_");

    const catEl = document.createElement("div");
    catEl.className = "menu-category";
    catEl.textContent = category;

    const subsEl = document.createElement("div");
    subsEl.className = "menu-subcategories";

    Object.keys(subs).forEach(subcategory => {
      const subId = `${catId}_${subcategory.replace(/\s/g, "_")}`;

      const subEl = document.createElement("div");
      subEl.className = "menu-subcategory";
      subEl.textContent = subcategory;

      subEl.onclick = e => {
        e.stopPropagation();

        document.getElementById(subId)
          ?.scrollIntoView({ behavior: "smooth" });

        closeMenu();
      };

      subsEl.appendChild(subEl);
    });

    catEl.onclick = e => {
      e.stopPropagation();

      if (openedSubs && openedSubs !== subsEl) {
        openedSubs.classList.remove("open");
      }

      subsEl.classList.toggle("open");
      openedSubs = subsEl.classList.contains("open") ? subsEl : null;
    };

    topMenu.append(catEl, subsEl);
  });

  function openMenu() {
    lastScrollY = window.scrollY;
    topMenu.style.display = "block";
    document.addEventListener("click", outsideClick);
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  function closeMenu() {
    topMenu.style.display = "none";
    document.removeEventListener("click", outsideClick);
    window.removeEventListener("scroll", onScroll);
  }

  function outsideClick(e) {
    if (!topMenu.contains(e.target) && e.target !== menuBtn) {
      closeMenu();
    }
  }

  function onScroll() {
    if (Math.abs(window.scrollY - lastScrollY) > 5) {
      closeMenu();
    }
  }

  menuBtn.onclick = e => {
    e.stopPropagation();
    topMenu.style.display === "block" ? closeMenu() : openMenu();
  };
}
