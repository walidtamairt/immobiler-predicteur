function create(config = {}) {
  const baseURL = config.baseURL || "";
  const defaultHeaders = config.headers || {};

  async function request(method, path, payload) {
    const response = await fetch(`${baseURL}${path}`, {
      method,
      headers: defaultHeaders,
      body: payload ? JSON.stringify(payload) : undefined,
    });

    if (!response.ok) {
      const error = new Error(`Request failed with status ${response.status}`);
      error.response = { status: response.status };
      throw error;
    }

    return { data: await response.json() };
  }

  return {
    get(path) {
      return request("GET", path);
    },
    post(path, payload) {
      return request("POST", path, payload);
    },
  };
}

export default { create };
