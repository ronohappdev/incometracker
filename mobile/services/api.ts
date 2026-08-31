import * as SecureStore from "expo-secure-store";
import { Platform } from "react-native";

const API_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000";

// Storage adapter: Use SecureStore on native, localStorage on web
const storage = {
  async getItem(key: string) {
    if (Platform.OS === "web") {
      return typeof window !== "undefined" ? window.localStorage.getItem(key) : null;
    }
    return SecureStore.getItemAsync(key);
  },
  async setItem(key: string, value: string) {
    if (Platform.OS === "web") {
      if (typeof window !== "undefined") window.localStorage.setItem(key, value);
    } else {
      await SecureStore.setItemAsync(key, value);
    }
  },
};

async function request(path: string, options: RequestInit = {}) {
  const token = await storage.getItem("access_token");
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Unable to reach the service" }));
    throw new Error(errorData.detail || "Request failed");
  }
  return response.status === 204 ? undefined : response.json();
}

export const api = {
  login: (email: string, password: string) =>
    request("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  register: (email: string, password: string) =>
    request("/auth/register", { method: "POST", body: JSON.stringify({ email, password }) }),
  me: () => request("/users/me"),
  dashboard: () => request("/dashboard"),
  income: () => request("/income"),
  addIncome: (payload: unknown) => request("/income", { method: "POST", body: JSON.stringify(payload) }),
  updateBenchmark: (payload: unknown) =>
    request("/benchmark", { method: "PATCH", body: JSON.stringify(payload) }),
  analyticsMonthly: (params?: { start?: string; end?: string }) => {
    const qs = params ? `?${new URLSearchParams(Object.fromEntries(Object.entries(params).filter(([k, v]) => v != null)))}` : "";
    return request(`/analytics/monthly${qs}`);
  },
  analyticsYearly: (params?: { start?: string; end?: string }) => {
    const qs = params ? `?${new URLSearchParams(Object.fromEntries(Object.entries(params).filter(([k, v]) => v != null)))}` : "";
    return request(`/analytics/yearly${qs}`);
  },
};
