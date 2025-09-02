const config = {
  schemaFile: "http://localhost:8000/api/openapi.json",
  apiFile: "./src/api/generated/api.ts",
  apiImport: "api",
  outputFiles: {
    "./src/api/generated/musicApi.ts": {
      filterEndpoints: [/music/i],
    },
    "./src/api/generated/authApi.ts": {
      filterEndpoints: [/auth/i],
    },
    "./src/api/generated/youtubeApi.ts": {
      filterEndpoints: [/youtube/i],
    },
    "./src/api/generated/adminApi.ts": {
      filterEndpoints: [/admin/i],
    },
    "./src/api/generated/webdavApi.ts": {
      filterEndpoints: [/webdav/i],
    },
  },
  exportName: "api",
  hooks: { queries: true, lazyQueries: true, mutations: true },
  tag: false,
  flattenArg: true,
  endpointOverrides: [
    {
      pattern: /.*/,
      parameterFilter: (_name, parameter) => parameter.in !== "header" && parameter.in !== "cookie",
    },
  ],
};

export default config;
