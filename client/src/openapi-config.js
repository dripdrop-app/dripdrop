const config = {
  schemaFile: "http://localhost:8000/api/openapi.json",
  apiFile: "./api/generated/api.ts",
  apiImport: "api",
  outputFiles: {
    "./api/generated/musicApi.ts": {
      filterEndpoints: [/music/i],
    },
    "./api/generated/authApi.ts": {
      filterEndpoints: [/auth/i],
    },
    "./api/generated/youtubeApi.ts": {
      filterEndpoints: [/youtube/i],
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
