import { api } from "./api";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getWebdavApiWebdavGet: build.query<GetWebdavApiWebdavGetApiResponse, GetWebdavApiWebdavGetApiArg>({
      query: () => ({ url: `/api/webdav` }),
    }),
    updateWebdavApiWebdavPost: build.mutation<UpdateWebdavApiWebdavPostApiResponse, UpdateWebdavApiWebdavPostApiArg>({
      query: (queryArg) => ({
        url: `/api/webdav`,
        method: "POST",
        body: queryArg,
      }),
    }),
    deleteWebdavApiWebdavDelete: build.mutation<
      DeleteWebdavApiWebdavDeleteApiResponse,
      DeleteWebdavApiWebdavDeleteApiArg
    >({
      query: () => ({ url: `/api/webdav`, method: "DELETE" }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetWebdavApiWebdavGetApiResponse = /** status 200 Successful Response */ WebDavResponse;
export type GetWebdavApiWebdavGetApiArg = void;
export type UpdateWebdavApiWebdavPostApiResponse = /** status 200 Successful Response */ WebDavResponse;
export type UpdateWebdavApiWebdavPostApiArg = UpdateWebDav;
export type DeleteWebdavApiWebdavDeleteApiResponse = unknown;
export type DeleteWebdavApiWebdavDeleteApiArg = void;
export type WebDavResponse = {
  username: string;
  password: string;
  url: string;
};
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export type UpdateWebDav = {
  username: string;
  password: string;
  url: string;
};
export const {
  useGetWebdavApiWebdavGetQuery,
  useLazyGetWebdavApiWebdavGetQuery,
  useUpdateWebdavApiWebdavPostMutation,
  useDeleteWebdavApiWebdavDeleteMutation,
} = injectedRtkApi;
