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

  const data = normalizeData(JSON.parse(raw));
  menu.innerHTML = "";

  Object.entries(data).forEach(([category, subs]) => {
    const catId = category.replace(/\s/g, "_");

    const section = document.createElement("section");
    section.id = catId;

    // ===== CATEGORY HEADER =====
    const catWrapper = document.createElement("div");
    catWrapper.className = "category-header";

    const imgCatLeft = document.createElement("div");
    imgCatLeft.className = "imgCat";
    imgCatLeft.style.setProperty(
      "--imgCat",
      `url("/static/img/category.svg")`
    );

    const title = document.createElement("h2");
    title.textContent = category;

    const imgCatRight = document.createElement("div");
    imgCatRight.className = "imgCat";
    imgCatRight.style.setProperty(
      "--imgCat",
      `url("/static/img/category.svg")`
    );

    

    catWrapper.append(imgCatLeft, title, imgCatRight);
    section.appendChild(catWrapper);

    // ===== SUBCATEGORIES =====
    Object.entries(subs).forEach(([subcategory, tree]) => {
      const subId = `${catId}_${subcategory.replace(/\s/g, "_")}`;

      const subTitle = document.createElement("h3");
      subTitle.id = subId;
      subTitle.textContent = subcategory;


      const subImgcenter = document.createElement("div");
      subImgcenter.className = "subImg";
      subImgcenter.style.setProperty(
        "--subImg",
        `url("/static/img/subcategory.svg")`
      );

      section.append(subTitle, subImgcenter);
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
