async function loadMenu(token) {
  const headers = token ? { Authorization: "Bearer " + token } : {};
  
  const data = await fetch("/api/menu", { headers })
    .then(r => r.json())
    .catch(() => ({})); // Если ошибка - пустое меню

  const menu = document.getElementById("menu");
  const side = document.getElementById("side-menu");

  Object.entries(data).forEach(([category, subs]) => {
    const catId = category.replace(/\s/g, "_");

    // Создаем элемент категории с обработчиком клика
    const categoryElement = document.createElement("div");
    categoryElement.className = "category";
    categoryElement.textContent = category;
    categoryElement.onclick = () => {
      document.getElementById(catId).scrollIntoView({ behavior: 'smooth' });
      side.classList.add("hidden"); // Закрываем меню после клика
    };
    side.appendChild(categoryElement);

    const section = document.createElement("section");
    section.id = catId;
    section.innerHTML = `<h2>${category}</h2>`;

    Object.entries(subs).forEach(([sub, items]) => {
      section.innerHTML += `<h3>${sub}</h3>`;
      items.forEach(i => {
        section.innerHTML += `
          <div class="item">
            <div class="item-info">
              <div class="item-name">${i.name}</div>
              ${i.description ? `<div class="item-description">${i.description}</div>` : ''}
            </div>
            <div class="item-price">${i.price} ₽</div>
          </div>`;
      });
    });

    menu.appendChild(section);
  });

  // Добавляем обработчик для кнопки меню
  document.getElementById("menu-btn").onclick = () => {
    side.classList.toggle("hidden");
  };
}
