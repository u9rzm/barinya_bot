async function loadMenu() {
  const topMenu = document.getElementById("top-menu");
  const menu = document.getElementById("menu");
  const menuBtn = document.getElementById("menu-btn");

  if (!topMenu || !menu || !menuBtn) return;

  let data = {};
  try {
    const response = await fetch("/static/data/menu.json");
    if (!response.ok) throw new Error(response.status);
    data = await response.json();
  } catch (err) {
    console.error("fetch error:", err);
    return;
  }

  topMenu.innerHTML = ""; // очистка меню

  Object.entries(data).forEach(([category, subs], idx) => {
    const catId = category.replace(/\s/g, "_");

    const catEl = document.createElement("div");
    catEl.className = "menu-category";

    // Добавляем картинки слева и справа
    const imgLeft = document.createElement("img");
    imgLeft.src = `/static/img/cat_left_${idx}.png`;
    imgLeft.alt = "left";

    const imgRight = document.createElement("img");
    imgRight.src = `/static/img/cat_right_${idx}.png`;
    imgRight.alt = "right";


    
    catEl.appendChild(imgLeft);
    catEl.appendChild(document.createTextNode(category));
    catEl.appendChild(imgRight);

    const subsEl = document.createElement("div");
    subsEl.className = "menu-subcategories";

    Object.keys(subs).forEach((sub, sidx) => {
      const subId = `${catId}_${sub.replace(/\s/g, "_")}`;
      const subEl = document.createElement("div");
      subEl.className = "menu-subcategory";
      subEl.textContent = sub;

      const subImg = document.createElement("img");
      subImg.src = `/static/img/sub_${idx}_${sidx}.png`;
      subImg.alt = "sub";

      subEl.appendChild(subImg);

      subEl.onclick = () => {
        document.getElementById(subId)?.scrollIntoView({ behavior: "smooth" });
        closeMenu();
      };

      subsEl.appendChild(subEl);
    });

    catEl.onclick = () => subsEl.classList.toggle("open");

    topMenu.appendChild(catEl);
    topMenu.appendChild(subsEl);
  });

  function openMenu() {
    topMenu.style.display = "block";
  }

  function closeMenu() {
    topMenu.style.display = "none";
  }

  menuBtn.onclick = () => {
    if (topMenu.style.display === "block") closeMenu();
    else openMenu();
  };

/* Основные секции */
menu.innerHTML = "";
Object.entries(data).forEach(([category, subs], idx) => {
  const catId = category.replace(/\s/g, "_");

  const section = document.createElement("section");
  section.id = catId;

  // Категория с картинками слева и справа
  const catWrapper = document.createElement("div");
  catWrapper.style.display = "flex";
  catWrapper.style.alignItems = "center";
  catWrapper.style.justifyContent = "space-between";
  catWrapper.style.marginBottom = "12px";

  const imgLeft = document.createElement("img");
  imgLeft.src = `/static/img/cat_left_${idx}.png`;
  imgLeft.alt = "left";
  imgLeft.style.height = "40px";

  const catTitle = document.createElement("h2");
  catTitle.textContent = category;
  catTitle.style.margin = "0 10px";
  catTitle.style.flexGrow = "1";
  catTitle.style.textAlign = "center";

  const imgRight = document.createElement("img");
  imgRight.src = `/static/img/cat_right_${idx}.png`;
  imgRight.alt = "right";
  imgRight.style.height = "40px";

  catWrapper.appendChild(imgLeft);
  catWrapper.appendChild(catTitle);
  catWrapper.appendChild(imgRight);
  section.appendChild(catWrapper);

  Object.entries(subs).forEach(([sub, items], sidx) => {
    const subId = `${catId}_${sub.replace(/\s/g, "_")}`;

    // Подкатегория
    const subTitle = document.createElement("h3");
    subTitle.id = subId;
    subTitle.textContent = sub;
    subTitle.style.position = "relative";
    subTitle.style.marginTop = "12px";

    // Картинка под подкатегорией
    const subImg = document.createElement("img");
    subImg.src = `/static/img/sub_${idx}_${sidx}.png`;
    subImg.alt = "sub";
    subTitle.style.position = "relative";
    subImg.style.display = "block";
    subImg.style.margin = "6px auto 12px auto";
    subImg.style.height = "50px";

    section.appendChild(subTitle);
    section.appendChild(subImg);

    items.forEach(i => {
      section.innerHTML += `
        <div class="item">
          <div class="item-info">
            <div class="item-name">${i.name}</div>
            ${i.description ? `<div class="item-description">${i.description}</div>` : ""}
          </div>
          <div class="item-price">${i.price} ₽</div>
        </div>`;
    });
  });

    menu.appendChild(section);
  });
}
