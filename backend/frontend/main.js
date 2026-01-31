/* ===============================
   CureVox – Production Frontend JS
   =============================== */

"use strict";

/* ---------- API BASE ---------- */
const API_BASE = (() => {
  if (location.hostname === "localhost" || location.hostname === "127.0.0.1") {
    return "http://localhost:5001";
  }
  return `${location.protocol}//${location.hostname}:5001`;
})();

/* ---------- AUTH TOKEN ---------- */
function saveToken(token) {
  localStorage.setItem("curevox_token", token);
}

function getToken() {
  return localStorage.getItem("curevox_token");
}

function clearToken() {
  localStorage.removeItem("curevox_token");
}

/* ---------- HTTP HELPERS ---------- */
async function apiGet(path) {
  const headers = {};
  const token = getToken();

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    headers
  });

  if (!response.ok) {
    throw new Error(`GET ${path} failed with ${response.status}`);
  }

  return response.json();
}

async function apiPost(path, payload = null, isForm = false) {
  const headers = {};
  const token = getToken();

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let body = null;

  if (payload) {
    if (isForm) {
      body = payload;
    } else {
      headers["Content-Type"] = "application/json";
      body = JSON.stringify(payload);
    }
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body
  });

  if (!response.ok) {
    throw new Error(`POST ${path} failed with ${response.status}`);
  }

  return response.json();
}

/* ---------- GLOBAL ERROR HANDLER ---------- */
window.addEventListener("unhandledrejection", event => {
  console.error("Unhandled API error:", event.reason);
});
