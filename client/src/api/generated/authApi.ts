import { api } from "./api";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    checkSessionApiAuthSessionGet: build.query<
      CheckSessionApiAuthSessionGetApiResponse,
      CheckSessionApiAuthSessionGetApiArg
    >({
      query: () => ({ url: `/api/auth/session` }),
    }),
    loginApiAuthLoginPost: build.mutation<LoginApiAuthLoginPostApiResponse, LoginApiAuthLoginPostApiArg>({
      query: (queryArg) => ({ url: `/api/auth/login`, method: "POST", body: queryArg }),
    }),
    logoutApiAuthLogoutDelete: build.mutation<LogoutApiAuthLogoutDeleteApiResponse, LogoutApiAuthLogoutDeleteApiArg>({
      query: () => ({ url: `/api/auth/logout`, method: "DELETE" }),
    }),
    createAccountApiAuthCreatePost: build.mutation<
      CreateAccountApiAuthCreatePostApiResponse,
      CreateAccountApiAuthCreatePostApiArg
    >({
      query: (queryArg) => ({ url: `/api/auth/create`, method: "POST", body: queryArg }),
    }),
    verifyEmailApiAuthVerifyGet: build.query<VerifyEmailApiAuthVerifyGetApiResponse, VerifyEmailApiAuthVerifyGetApiArg>(
      {
        query: (queryArg) => ({
          url: `/api/auth/verify`,
          params: {
            token: queryArg,
          },
        }),
      }
    ),
    sendResetEmailApiAuthSendresetPost: build.mutation<
      SendResetEmailApiAuthSendresetPostApiResponse,
      SendResetEmailApiAuthSendresetPostApiArg
    >({
      query: (queryArg) => ({ url: `/api/auth/sendreset`, method: "POST", body: queryArg }),
    }),
    resetPasswordApiAuthResetPost: build.mutation<
      ResetPasswordApiAuthResetPostApiResponse,
      ResetPasswordApiAuthResetPostApiArg
    >({
      query: (queryArg) => ({ url: `/api/auth/reset`, method: "POST", body: queryArg }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type CheckSessionApiAuthSessionGetApiResponse = /** status 200 Successful Response */ UserResponse;
export type CheckSessionApiAuthSessionGetApiArg = void;
export type LoginApiAuthLoginPostApiResponse = /** status 200 Successful Response */ AuthenticatedResponse;
export type LoginApiAuthLoginPostApiArg = LoginUser;
export type LogoutApiAuthLogoutDeleteApiResponse = unknown;
export type LogoutApiAuthLogoutDeleteApiArg = void;
export type CreateAccountApiAuthCreatePostApiResponse = unknown;
export type CreateAccountApiAuthCreatePostApiArg = CreateUser;
export type VerifyEmailApiAuthVerifyGetApiResponse = unknown;
export type VerifyEmailApiAuthVerifyGetApiArg = string;
export type SendResetEmailApiAuthSendresetPostApiResponse = unknown;
export type SendResetEmailApiAuthSendresetPostApiArg = SendResetPassword;
export type ResetPasswordApiAuthResetPostApiResponse = unknown;
export type ResetPasswordApiAuthResetPostApiArg = PasswordReset;
export type UserResponse = {
  email: string;
  admin: boolean;
};
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export type AuthenticatedResponse = {
  accessToken: string;
  tokenType: string;
  user: UserResponse;
};
export type LoginUser = {
  email: string;
  password: string;
};
export type CreateUser = {
  email: string;
  password: string;
};
export type SendResetPassword = {
  email: string;
};
export type PasswordReset = {
  token: string;
  password: string;
};
export const {
  useCheckSessionApiAuthSessionGetQuery,
  useLazyCheckSessionApiAuthSessionGetQuery,
  useLoginApiAuthLoginPostMutation,
  useLogoutApiAuthLogoutDeleteMutation,
  useCreateAccountApiAuthCreatePostMutation,
  useVerifyEmailApiAuthVerifyGetQuery,
  useLazyVerifyEmailApiAuthVerifyGetQuery,
  useSendResetEmailApiAuthSendresetPostMutation,
  useResetPasswordApiAuthResetPostMutation,
} = injectedRtkApi;
