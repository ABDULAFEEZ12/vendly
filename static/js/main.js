// main.js - Vendly frontend utilities

const API_BASE = '';
let currentUser = null;

// Token management
function getToken() {
  return localStorage.getItem('vendly_token');
}
function setToken(token) {
  localStorage.setItem('vendly_token', token);
}
function clearToken() {
  localStorage.removeItem('vendly_token');
  currentUser = null;
}

// Axios instance
const api = axios.create({
  baseURL: API_BASE,
});
api.interceptors.request.use(config => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auth UI update
async function fetchUser() {
  try {
    const res = await api.get('/api/auth/me');
    currentUser = res.data.user;
    updateNav();
  } catch(e) {
    currentUser = null;
    updateNav();
  }
}

function updateNav() {
  const authLinks = document.getElementById('auth-links');
  if (!authLinks) return;
  if (currentUser) {
    authLinks.innerHTML = `
      <a href="/dashboard">Dashboard</a>
      <a href="/chat">Chat</a>
      <a href="/saved">Saved</a>
      <a href="#" onclick="logout()">Logout</a>
    `;
  } else {
    authLinks.innerHTML = `
      <a href="/login">Login</a>
      <a href="/register">Register</a>
    `;
  }
}

function logout() {
  clearToken();
  window.location.href = '/login';
}

// Cloudinary unsigned upload helper
async function uploadToCloudinary(file) {
  const cloudName = document.body.dataset.cloudName || 'your-cloud-name';
  const uploadPreset = document.body.dataset.uploadPreset || 'vendly-unsigned';
  const formData = new FormData();
  formData.append('file', file);
  formData.append('upload_preset', uploadPreset);
  const res = await fetch(`https://api.cloudinary.com/v1_1/${cloudName}/image/upload`, {
    method: 'POST',
    body: formData
  });
  const data = await res.json();
  return data.secure_url;
}

// On page load
document.addEventListener('DOMContentLoaded', fetchUser);