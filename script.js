async function predictLoan() {
  const fields = ["age","experience","income","family","ccavg","education",
                  "mortgage","securities","cd_account","online","creditcard"];

  // Bug fix: .value is always a string, check trim() not null
  for (const id of fields) {
    if (document.getElementById(id).value.trim() === "") {
      highlight(id);
      return;
    }
  }

  document.getElementById("btn-text").style.display  = "none";
  document.getElementById("btn-loader").style.display = "inline";
  document.querySelector(".predict-btn").disabled = true;

  const data = {};
  fields.forEach(id => data[id] = document.getElementById(id).value);

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    const result = await response.json();

    if (result.error) {
      showError(result.error);
    } else {
      window.open(result.redirect, "_blank");
    }
  } catch {
    showError("Error connecting to server. Please try again.");
  }

  document.getElementById("btn-text").style.display  = "inline";
  document.getElementById("btn-loader").style.display = "none";
  document.querySelector(".predict-btn").disabled = false;
}

function highlight(id) {
  const el = document.getElementById(id);
  el.style.borderColor = "#ef4444";
  el.style.boxShadow   = "0 0 0 3px rgba(239,68,68,0.3)";
  el.focus();
  setTimeout(() => { el.style.borderColor = ""; el.style.boxShadow = ""; }, 2000);
}

function showError(msg) {
  let el = document.getElementById("error-toast");
  if (!el) {
    el = document.createElement("div");
    el.id = "error-toast";
    el.style.cssText = "position:fixed;bottom:24px;left:50%;transform:translateX(-50%);"
      + "background:rgba(239,68,68,0.9);color:#fff;padding:14px 24px;border-radius:12px;"
      + "font-family:Poppins,sans-serif;font-size:13px;z-index:9999;animation:fadeInUp 0.4s ease;";
    document.body.appendChild(el);
  }
  el.textContent  = msg;
  el.style.display = "block";
  setTimeout(() => { el.style.display = "none"; }, 4000);
}
