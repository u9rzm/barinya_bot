function normalizeData(data) {
  function walk(node) {
    if (node.items && !Array.isArray(node.items)) {
      node.items = Object.values(node.items);
    }
    Object.values(node).forEach(v => {
      if (typeof v === "object" && v !== null) {
        walk(v);
      }
    });
  }

  walk(data);
  return data;
}


export function loadContent() {
  const menu = document.getElementById("menu");
  if (!menu) return;

  const raw = localStorage.getItem("data");
  if (!raw) return;

  // const data = JSON.parse(raw);
  const data = normalizeData(JSON.parse(raw));
  menu.innerHTML = "";

  Object.entries(data).forEach(([category, subs], idx) => {
    const catId = category.replace(/\s/g, "_");

    const section = document.createElement("section");
    section.id = catId;

    // ===== CATEGORY HEADER =====
    const catWrapper = document.createElement("div");
    catWrapper.style.display = "flex";
    catWrapper.style.alignItems = "center";
    catWrapper.style.justifyContent = "space-between";
    catWrapper.style.marginBottom = "12px";

    const imgLeft = document.createElement("img");
    imgLeft.src = `/static/img/category.svg`;
    imgLeft.style.height = "40px";

    const title = document.createElement("h2");
    title.textContent = category;
    title.style.flexGrow = "1";
    title.style.textAlign = "center";

    const imgRight = document.createElement("img");
    imgRight.src = `/static/img/category.svg`;
    imgRight.style.height = "40px";

    catWrapper.append(imgLeft, title, imgRight);
    section.appendChild(catWrapper);

    // ===== SUBCATEGORIES =====
    Object.entries(subs).forEach(([subcategory, tree], sidx) => {
      const subId = `${catId}_${subcategory.replace(/\s/g, "_")}`;

      const subTitle = document.createElement("h3");
      subTitle.id = subId;
      subTitle.textContent = subcategory;

      const subImg = document.createElement("img");
      subImg.src = `/static/img/subcategory.svg`;
      subImg.style.display = "block";
      subImg.style.margin = "6px auto 12px";
      subImg.style.height = "30px";

      section.append(subTitle, subImg);

      renderTree(tree, section, 4);
    });

    menu.appendChild(section);
  });
}

/**
 * Рекурсивный рендер уровней sub_1 / sub_2 / ...
 */
function renderTree(node, container, level) {
  Object.entries(node).forEach(([key, value]) => {
    if (key === "items") {
      value.forEach(item => {
        container.innerHTML += `
          <div class="item">
            <div class="item-info">
              <div class="item-name">
                ${item.name}${item.weight ? ` / ${item.weight}` : ""}
              </div>
              ${item.description ? `<div class="item-description">${item.description}</div>` : ""}
            </div>
            <div class="item-price">${item.price} ₽</div>
          </div>
        `;
      });
      return;
    }

    const title = document.createElement(`h${level}`);
    title.textContent = key;
    container.appendChild(title);

    renderTree(value, container, Math.min(level + 1, 6));
  });
}
