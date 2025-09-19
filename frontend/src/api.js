import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API || "http://localhost:8000/api/v1",
  withCredentials: false,
});

function getTokens() {
  const access = localStorage.getItem("access");
  const refresh = localStorage.getItem("refresh");
  return { access, refresh };
}
function setTokens({ access, refresh }) {
  if (access) localStorage.setItem("access", access);
  if (refresh) localStorage.setItem("refresh", refresh);
}
function clearTokens() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
}

api.interceptors.request.use((config) => {
  const { access } = getTokens();
  if (access) config.headers.Authorization = `Bearer ${access}`;
  return config;
});

let isRefreshing = false;
let queue = [];

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config || {};
    const status = error?.response?.status;

    if (status === 401 && !original._retry) {
      const { refresh } = getTokens();
      if (!refresh) {
        clearTokens();
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          queue.push({ resolve, reject });
        })
          .then((token) => {
            original.headers.Authorization = `Bearer ${token}`;
            return api(original);
          })
          .catch((err) => Promise.reject(err));
      }

      original._retry = true;
      isRefreshing = true;
      try {
        const r = await axios.post(
          (import.meta.env.VITE_API || "http://localhost:8000/api/v1") + "/auth/refresh/",
          { refresh }
        );
        const newAccess = r.data.access || r.data.access_token;
        if (!newAccess) throw new Error("No access token in refresh response");
        setTokens({ access: newAccess });
        queue.forEach(({ resolve }) => resolve(newAccess));
        queue = [];
        original.headers.Authorization = `Bearer ${newAccess}`;
        return api(original);
      } catch (e) {
        clearTokens();
        queue.forEach(({ reject }) => reject(e));
        queue = [];
        return Promise.reject(e);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
export { setTokens, clearTokens, getTokens };
