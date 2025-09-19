import axios from "axios";

const BASE = import.meta.env.VITE_API || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: BASE,
});

function getAccess()  { return localStorage.getItem("access") || ""; }
function getRefresh() { return localStorage.getItem("refresh") || ""; }
function setAccess(t) { if (t) localStorage.setItem("access", t); }
function setRefresh(t){ if (t) localStorage.setItem("refresh", t); }
export function clearAuth() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
}

api.interceptors.request.use((cfg) => {
  const token = getAccess();
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

let refreshing = false;
let pending = [];
api.interceptors.response.use(
  r => r,
  async (err) => {
    const status = err?.response?.status;
    const original = err.config || {};
    if (status === 401 && !original._retry) {
      const refresh = getRefresh();
      if (!refresh) { clearAuth(); return Promise.reject(err); }

      original._retry = true;

      if (refreshing) {
        return new Promise((resolve, reject) => {
          pending.push({ resolve, reject });
        }).then((newAccess) => {
          original.headers.Authorization = `Bearer ${newAccess}`;
          return api(original);
        });
      }

      refreshing = true;
      try {
        const r = await axios.post(`${BASE}/accounts/refresh/`, { refresh });
        const newAccess = r.data?.access;
        if (!newAccess) throw new Error("no access");
        setAccess(newAccess);
        pending.forEach(p => p.resolve(newAccess));
        pending = [];
        original.headers.Authorization = `Bearer ${newAccess}`;
        return api(original);
      } catch (e) {
        clearAuth();
        pending.forEach(p => p.reject(e));
        pending = [];
        return Promise.reject(e);
      } finally {
        refreshing = false;
      }
    }
    return Promise.reject(err);
  }
);

export async function login(username, password) {
  const r = await api.post("/accounts/login/", { username, password });
  const { access, refresh } = r.data;
  setAccess(access); setRefresh(refresh);
  return r.data;
}

export async function register(username, email, password) {
  return api.post("/accounts/register/", { username, email, password });
}

export default api;
