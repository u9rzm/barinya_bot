document.getElementById("profile-form").onsubmit = async e => {
  e.preventDefault();

  const token = localStorage.getItem("access_token");
  const data = Object.fromEntries(new FormData(e.target));

  await fetch("/api/profile", {
    method: "POST",
    headers: {
      "Authorization": "Bearer " + token,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  });

  alert("Сохранено");
};
