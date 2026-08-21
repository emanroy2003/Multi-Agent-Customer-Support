import api from "./api";

export async function register(email, fullName, password) {
  const { data } = await api.post("/auth/register", {
    email,
    full_name: fullName,
    password,
  });
  return data;
}

export async function login(email, password) {
  const { data } = await api.post("/auth/login", { email, password });
  return data;
}

export async function getCurrentUser() {
  const { data } = await api.get("/auth/me");
  return data;
}
