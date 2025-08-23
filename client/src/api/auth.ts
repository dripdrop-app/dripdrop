import { api } from "./generated/authApi";
import { Tags, tags } from "./tags";
import { transformErrorResponse } from "./utils";

const enhancedApi = api.enhanceEndpoints({
  addTagTypes: [Tags.USER],
  endpoints: {
    checkSessionApiAuthSessionGet: {
      providesTags: [Tags.USER],
    },
    createAccountApiAuthCreatePost: {
      invalidatesTags: (result) => (result ? tags : []),
      transformErrorResponse,
    },
    loginApiAuthLoginPost: {
      invalidatesTags: (result) => (result ? tags : []),
      transformErrorResponse,
    },
    logoutApiAuthLogoutDelete: {
      invalidatesTags: (_, error) => (!error ? tags : []),
    },
    sendResetEmailApiAuthSendresetPost: {
      transformErrorResponse,
    },
    resetPasswordApiAuthResetPost: {
      transformErrorResponse,
    },
    verifyEmailApiAuthVerifyGet: {
      transformErrorResponse,
    },
  },
});

export default enhancedApi;
export const {
  useCheckSessionApiAuthSessionGetQuery: useCheckSessionQuery,
  useCreateAccountApiAuthCreatePostMutation: useCreateMutation,
  useLoginApiAuthLoginPostMutation: useLoginMutation,
  useLogoutApiAuthLogoutDeleteMutation: useLogoutMutation,
  useSendResetEmailApiAuthSendresetPostMutation: useSendResetEmailMutation,
  useVerifyEmailApiAuthVerifyGetQuery: useVerifyAccountQuery,
  useResetPasswordApiAuthResetPostMutation: useResetPasswordMutation,
} = enhancedApi;
