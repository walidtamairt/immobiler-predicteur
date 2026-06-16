import axios from "axios";

function resolveApiBaseUrl() {
  const configuredUrl = import.meta.env.VITE_API_URL?.trim();
  if (configuredUrl) {
    return configuredUrl;
  }

  if (typeof window === "undefined") {
    return "http://localhost:8000";
  }

  const { hostname, port } = window.location;
  const isLocalFrontendDevServer =
    hostname === "localhost" &&
    (port === "5173" || port === "4173");

  return isLocalFrontendDevServer ? "http://localhost:8000" : "";
}

const API_URL = resolveApiBaseUrl();
const API_KEY = import.meta.env.VITE_API_KEY?.trim();

const http = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
    ...(API_KEY ? { "X-API-Key": API_KEY } : {}),
  },
});

function buildQueryString(filters = {}) {
  const query = new URLSearchParams();
  if (filters.neighborhood) query.set("neighborhood", filters.neighborhood);
  if (filters.houseStyle) query.set("house_style", filters.houseStyle);
  if (filters.overallQual) query.set("overall_qual", filters.overallQual);
  if (filters.bedroomAbvGr) query.set("bedroom_abv_gr", filters.bedroomAbvGr);
  if (filters.fullBath) query.set("full_bath", filters.fullBath);
  if (filters.saleMonth) query.set("sale_month", filters.saleMonth);
  if (filters.propertyAgeMin) query.set("property_age_min", filters.propertyAgeMin);
  if (filters.propertyAgeMax) query.set("property_age_max", filters.propertyAgeMax);
  const suffix = query.toString();
  return suffix ? `?${suffix}` : "";
}

async function get(path) {
  const response = await http.get(path);
  return response.data;
}

async function post(path, payload) {
  const response = await http.post(path, payload);
  return response.data;
}

export function getErrorMessage(error, fallbackMessage = "Impossible de recuperer les donnees.") {
  if (error?.response?.status === 401) {
    return "Acces refuse. Configurez VITE_API_KEY pour appeler les routes protegees.";
  }

  if (error?.message) {
    return error.message;
  }

  return fallbackMessage;
}

export async function getMarketDashboard(filters = {}) {
  return get(`/api/market-dashboard${buildQueryString(filters)}`);
}

export async function getMarketFilters() {
  return get("/api/filters");
}

export async function predictProperty(payload) {
  return post("/api/predict", payload);
}

export async function getPredictionHistory() {
  return get("/api/prediction-history");
}

export async function getLatestModelMetrics() {
  return get("/api/model-metrics/latest");
}

export async function getModelMetricsHistory() {
  return get("/api/model-metrics/history");
}

export async function sendChatMessage(messages) {
  return post("/api/chat", { messages });
}
