import { api } from "./api";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getYoutubeSubscriptionsApiYoutubeSubscriptionsListGet: build.query<
      GetYoutubeSubscriptionsApiYoutubeSubscriptionsListGetApiResponse,
      GetYoutubeSubscriptionsApiYoutubeSubscriptionsListGetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/youtube/subscriptions/list`,
        params: {
          page: queryArg.page,
          per_page: queryArg.perPage,
        },
      }),
    }),
    addUserSubscriptionApiYoutubeSubscriptionsUserPut: build.mutation<
      AddUserSubscriptionApiYoutubeSubscriptionsUserPutApiResponse,
      AddUserSubscriptionApiYoutubeSubscriptionsUserPutApiArg
    >({
      query: (queryArg) => ({
        url: `/api/youtube/subscriptions/user`,
        method: "PUT",
        params: {
          channel_id: queryArg,
        },
      }),
    }),
    deleteUserSubscriptionApiYoutubeSubscriptionsUserDelete: build.mutation<
      DeleteUserSubscriptionApiYoutubeSubscriptionsUserDeleteApiResponse,
      DeleteUserSubscriptionApiYoutubeSubscriptionsUserDeleteApiArg
    >({
      query: (queryArg) => ({
        url: `/api/youtube/subscriptions/user`,
        method: "DELETE",
        params: {
          channel_id: queryArg,
        },
      }),
    }),
    getUserYoutubeChannelApiYoutubeChannelsUserGet: build.query<
      GetUserYoutubeChannelApiYoutubeChannelsUserGetApiResponse,
      GetUserYoutubeChannelApiYoutubeChannelsUserGetApiArg
    >({
      query: () => ({ url: `/api/youtube/channels/user` }),
    }),
    updateUserYoutubeChannelApiYoutubeChannelsUserPost: build.mutation<
      UpdateUserYoutubeChannelApiYoutubeChannelsUserPostApiResponse,
      UpdateUserYoutubeChannelApiYoutubeChannelsUserPostApiArg
    >({
      query: (queryArg) => ({ url: `/api/youtube/channels/user`, method: "POST", body: queryArg }),
    }),
    getYoutubeChannelApiYoutubeChannelsChannelIdGet: build.query<
      GetYoutubeChannelApiYoutubeChannelsChannelIdGetApiResponse,
      GetYoutubeChannelApiYoutubeChannelsChannelIdGetApiArg
    >({
      query: (queryArg) => ({ url: `/api/youtube/channels/${queryArg}` }),
    }),
    getYoutubeVideoCategoriesApiYoutubeVideosCategoriesGet: build.query<
      GetYoutubeVideoCategoriesApiYoutubeVideosCategoriesGetApiResponse,
      GetYoutubeVideoCategoriesApiYoutubeVideosCategoriesGetApiArg
    >({
      query: () => ({ url: `/api/youtube/videos/categories` }),
    }),
    getYoutubeVideosApiYoutubeVideosListGet: build.query<
      GetYoutubeVideosApiYoutubeVideosListGetApiResponse,
      GetYoutubeVideosApiYoutubeVideosListGetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/youtube/videos/list`,
        params: {
          page: queryArg.page,
          per_page: queryArg.perPage,
          video_categories: queryArg.videoCategories,
          channel_id: queryArg.channelId,
          liked_only: queryArg.likedOnly,
          queued_only: queryArg.queuedOnly,
        },
      }),
    }),
    getYoutubeVideoApiYoutubeVideosVideoIdGet: build.query<
      GetYoutubeVideoApiYoutubeVideosVideoIdGetApiResponse,
      GetYoutubeVideoApiYoutubeVideosVideoIdGetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/youtube/videos/${queryArg.videoId}`,
        params: {
          related_videos_length: queryArg.relatedVideosLength,
        },
      }),
    }),
    addYoutubeVideoWatchApiYoutubeVideosVideoIdWatchPut: build.mutation<
      AddYoutubeVideoWatchApiYoutubeVideosVideoIdWatchPutApiResponse,
      AddYoutubeVideoWatchApiYoutubeVideosVideoIdWatchPutApiArg
    >({
      query: (queryArg) => ({ url: `/api/youtube/videos/${queryArg}/watch`, method: "PUT" }),
    }),
    addYoutubeVideoLikeApiYoutubeVideosVideoIdLikePut: build.mutation<
      AddYoutubeVideoLikeApiYoutubeVideosVideoIdLikePutApiResponse,
      AddYoutubeVideoLikeApiYoutubeVideosVideoIdLikePutApiArg
    >({
      query: (queryArg) => ({ url: `/api/youtube/videos/${queryArg}/like`, method: "PUT" }),
    }),
    deleteYoutubeVideoLikeApiYoutubeVideosVideoIdLikeDelete: build.mutation<
      DeleteYoutubeVideoLikeApiYoutubeVideosVideoIdLikeDeleteApiResponse,
      DeleteYoutubeVideoLikeApiYoutubeVideosVideoIdLikeDeleteApiArg
    >({
      query: (queryArg) => ({ url: `/api/youtube/videos/${queryArg}/like`, method: "DELETE" }),
    }),
    addYoutubeVideoQueueApiYoutubeVideosVideoIdQueuePut: build.mutation<
      AddYoutubeVideoQueueApiYoutubeVideosVideoIdQueuePutApiResponse,
      AddYoutubeVideoQueueApiYoutubeVideosVideoIdQueuePutApiArg
    >({
      query: (queryArg) => ({ url: `/api/youtube/videos/${queryArg}/queue`, method: "PUT" }),
    }),
    deleteYoutubeVideoQueueApiYoutubeVideosVideoIdQueueDelete: build.mutation<
      DeleteYoutubeVideoQueueApiYoutubeVideosVideoIdQueueDeleteApiResponse,
      DeleteYoutubeVideoQueueApiYoutubeVideosVideoIdQueueDeleteApiArg
    >({
      query: (queryArg) => ({ url: `/api/youtube/videos/${queryArg}/queue`, method: "DELETE" }),
    }),
    runUpdateSubscriptionsApiAdminYoutubeUpdateSubscriptionsGet: build.query<
      RunUpdateSubscriptionsApiAdminYoutubeUpdateSubscriptionsGetApiResponse,
      RunUpdateSubscriptionsApiAdminYoutubeUpdateSubscriptionsGetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/admin/youtube/update_subscriptions`,
        params: {
          email: queryArg,
        },
      }),
    }),
    runUpdateChannelVideosApiAdminYoutubeUpdateChannelVideosGet: build.query<
      RunUpdateChannelVideosApiAdminYoutubeUpdateChannelVideosGetApiResponse,
      RunUpdateChannelVideosApiAdminYoutubeUpdateChannelVideosGetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/admin/youtube/update_channel_videos`,
        params: {
          channel_id: queryArg.channelId,
          date_after: queryArg.dateAfter,
        },
      }),
    }),
    runUpdateVideoCategoriesApiAdminYoutubeUpdateVideoCategoriesGet: build.query<
      RunUpdateVideoCategoriesApiAdminYoutubeUpdateVideoCategoriesGetApiResponse,
      RunUpdateVideoCategoriesApiAdminYoutubeUpdateVideoCategoriesGetApiArg
    >({
      query: () => ({ url: `/api/admin/youtube/update_video_categories` }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetYoutubeSubscriptionsApiYoutubeSubscriptionsListGetApiResponse =
  /** status 200 Successful Response */ YoutubeSubscriptionsResponse;
export type GetYoutubeSubscriptionsApiYoutubeSubscriptionsListGetApiArg = {
  page: number;
  perPage: number;
};
export type AddUserSubscriptionApiYoutubeSubscriptionsUserPutApiResponse =
  /** status 200 Successful Response */ YoutubeChannelResponse;
export type AddUserSubscriptionApiYoutubeSubscriptionsUserPutApiArg = string;
export type DeleteUserSubscriptionApiYoutubeSubscriptionsUserDeleteApiResponse =
  /** status 200 Successful Response */ any;
export type DeleteUserSubscriptionApiYoutubeSubscriptionsUserDeleteApiArg = string;
export type GetUserYoutubeChannelApiYoutubeChannelsUserGetApiResponse =
  /** status 200 Successful Response */ YoutubeUserChannelResponse;
export type GetUserYoutubeChannelApiYoutubeChannelsUserGetApiArg = void;
export type UpdateUserYoutubeChannelApiYoutubeChannelsUserPostApiResponse = /** status 200 Successful Response */ any;
export type UpdateUserYoutubeChannelApiYoutubeChannelsUserPostApiArg =
  BodyUpdateUserYoutubeChannelApiYoutubeChannelsUserPost;
export type GetYoutubeChannelApiYoutubeChannelsChannelIdGetApiResponse =
  /** status 200 Successful Response */ YoutubeChannelResponse;
export type GetYoutubeChannelApiYoutubeChannelsChannelIdGetApiArg = string;
export type GetYoutubeVideoCategoriesApiYoutubeVideosCategoriesGetApiResponse =
  /** status 200 Successful Response */ YoutubeVideoCategoriesResponse;
export type GetYoutubeVideoCategoriesApiYoutubeVideosCategoriesGetApiArg = void;
export type GetYoutubeVideosApiYoutubeVideosListGetApiResponse =
  /** status 200 Successful Response */ YoutubeVideosResponse;
export type GetYoutubeVideosApiYoutubeVideosListGetApiArg = {
  page: number;
  perPage: number;
  videoCategories?: number[] | null;
  channelId?: string | null;
  likedOnly?: boolean | null;
  queuedOnly?: boolean | null;
};
export type GetYoutubeVideoApiYoutubeVideosVideoIdGetApiResponse =
  /** status 200 Successful Response */ YoutubeVideoDetailResponse;
export type GetYoutubeVideoApiYoutubeVideosVideoIdGetApiArg = {
  videoId: string;
  relatedVideosLength?: number;
};
export type AddYoutubeVideoWatchApiYoutubeVideosVideoIdWatchPutApiResponse = /** status 200 Successful Response */ any;
export type AddYoutubeVideoWatchApiYoutubeVideosVideoIdWatchPutApiArg = string;
export type AddYoutubeVideoLikeApiYoutubeVideosVideoIdLikePutApiResponse = /** status 200 Successful Response */ any;
export type AddYoutubeVideoLikeApiYoutubeVideosVideoIdLikePutApiArg = string;
export type DeleteYoutubeVideoLikeApiYoutubeVideosVideoIdLikeDeleteApiResponse =
  /** status 200 Successful Response */ any;
export type DeleteYoutubeVideoLikeApiYoutubeVideosVideoIdLikeDeleteApiArg = string;
export type AddYoutubeVideoQueueApiYoutubeVideosVideoIdQueuePutApiResponse = /** status 200 Successful Response */ any;
export type AddYoutubeVideoQueueApiYoutubeVideosVideoIdQueuePutApiArg = string;
export type DeleteYoutubeVideoQueueApiYoutubeVideosVideoIdQueueDeleteApiResponse =
  /** status 200 Successful Response */ any;
export type DeleteYoutubeVideoQueueApiYoutubeVideosVideoIdQueueDeleteApiArg = string;
export type RunUpdateSubscriptionsApiAdminYoutubeUpdateSubscriptionsGetApiResponse =
  /** status 200 Successful Response */ any;
export type RunUpdateSubscriptionsApiAdminYoutubeUpdateSubscriptionsGetApiArg = string | undefined;
export type RunUpdateChannelVideosApiAdminYoutubeUpdateChannelVideosGetApiResponse =
  /** status 200 Successful Response */ any;
export type RunUpdateChannelVideosApiAdminYoutubeUpdateChannelVideosGetApiArg = {
  channelId?: string;
  /** date string with format YYYYMMDD */
  dateAfter?: string;
};
export type RunUpdateVideoCategoriesApiAdminYoutubeUpdateVideoCategoriesGetApiResponse =
  /** status 200 Successful Response */ any;
export type RunUpdateVideoCategoriesApiAdminYoutubeUpdateVideoCategoriesGetApiArg = void;
export type YoutubeChannelResponse = {
  id: string;
  title: string;
  thumbnail?: string | null;
  subscribed: boolean;
  updating: boolean;
};
export type YoutubeSubscriptionsResponse = {
  channels: YoutubeChannelResponse[];
  totalPages: number;
};
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export type YoutubeUserChannelResponse = {
  id: string;
};
export type BodyUpdateUserYoutubeChannelApiYoutubeChannelsUserPost = {
  channel_id: string;
};
export type YoutubeVideoCategoryResponse = {
  id: number;
  name: string;
};
export type YoutubeVideoCategoriesResponse = {
  categories: YoutubeVideoCategoryResponse[];
};
export type YoutubeVideoChannelResponse = {
  id: string;
  title: string;
  thumbnail: string;
};
export type YoutubeVideoResponse = {
  id: string;
  title: string;
  thumbnail: string;
  category: YoutubeVideoCategoryResponse;
  publishedAt: string;
  description?: string | null;
  channel: YoutubeVideoChannelResponse;
  liked?: string | null;
  queued?: string | null;
  watched?: string | null;
};
export type YoutubeVideosResponse = {
  videos: YoutubeVideoResponse[];
  totalPages: number;
};
export type YoutubeVideoDetailResponse = {
  id: string;
  title: string;
  thumbnail: string;
  category: YoutubeVideoCategoryResponse;
  publishedAt: string;
  description?: string | null;
  channel: YoutubeVideoChannelResponse;
  liked?: string | null;
  queued?: string | null;
  watched?: string | null;
  relatedVideos?: YoutubeVideoResponse[];
};
export const {
  useGetYoutubeSubscriptionsApiYoutubeSubscriptionsListGetQuery,
  useLazyGetYoutubeSubscriptionsApiYoutubeSubscriptionsListGetQuery,
  useAddUserSubscriptionApiYoutubeSubscriptionsUserPutMutation,
  useDeleteUserSubscriptionApiYoutubeSubscriptionsUserDeleteMutation,
  useGetUserYoutubeChannelApiYoutubeChannelsUserGetQuery,
  useLazyGetUserYoutubeChannelApiYoutubeChannelsUserGetQuery,
  useUpdateUserYoutubeChannelApiYoutubeChannelsUserPostMutation,
  useGetYoutubeChannelApiYoutubeChannelsChannelIdGetQuery,
  useLazyGetYoutubeChannelApiYoutubeChannelsChannelIdGetQuery,
  useGetYoutubeVideoCategoriesApiYoutubeVideosCategoriesGetQuery,
  useLazyGetYoutubeVideoCategoriesApiYoutubeVideosCategoriesGetQuery,
  useGetYoutubeVideosApiYoutubeVideosListGetQuery,
  useLazyGetYoutubeVideosApiYoutubeVideosListGetQuery,
  useGetYoutubeVideoApiYoutubeVideosVideoIdGetQuery,
  useLazyGetYoutubeVideoApiYoutubeVideosVideoIdGetQuery,
  useAddYoutubeVideoWatchApiYoutubeVideosVideoIdWatchPutMutation,
  useAddYoutubeVideoLikeApiYoutubeVideosVideoIdLikePutMutation,
  useDeleteYoutubeVideoLikeApiYoutubeVideosVideoIdLikeDeleteMutation,
  useAddYoutubeVideoQueueApiYoutubeVideosVideoIdQueuePutMutation,
  useDeleteYoutubeVideoQueueApiYoutubeVideosVideoIdQueueDeleteMutation,
  useRunUpdateSubscriptionsApiAdminYoutubeUpdateSubscriptionsGetQuery,
  useLazyRunUpdateSubscriptionsApiAdminYoutubeUpdateSubscriptionsGetQuery,
  useRunUpdateChannelVideosApiAdminYoutubeUpdateChannelVideosGetQuery,
  useLazyRunUpdateChannelVideosApiAdminYoutubeUpdateChannelVideosGetQuery,
  useRunUpdateVideoCategoriesApiAdminYoutubeUpdateVideoCategoriesGetQuery,
  useLazyRunUpdateVideoCategoriesApiAdminYoutubeUpdateVideoCategoriesGetQuery,
} = injectedRtkApi;
