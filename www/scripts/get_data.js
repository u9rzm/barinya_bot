// get_data.js
export async function getData() {
  localStorage.removeItem("data"); // толька для разработки, потом убрать
  try {
    const response = await fetch("./data/menu.json");
    if (!response.ok) throw new Error(response.status);

    const data = await response.json();
    localStorage.setItem("data", JSON.stringify(data));
    return data;
  } catch (err) {
    console.error("fetch error:", err);
    return null;
  }
}
 