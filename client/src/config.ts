const isProd = import.meta.env.PROD;
const webSocketProtocol = isProd ? "wss" : "ws";
const httpProtocol = isProd ? "https" : "http";
const serverDomain = isProd ? window.location.host : import.meta.env.VITE_SERVER_URL;

export const buildURL = (endpoint: string) => `${httpProtocol}://${serverDomain}/${endpoint}`;
export const buildWebsocketURL = (endpoint: string) => `${webSocketProtocol}://${serverDomain}/api/${endpoint}`;
