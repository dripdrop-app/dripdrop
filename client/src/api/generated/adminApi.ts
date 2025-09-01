import { api } from "./api";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    runCronJobsApiAdminCronRunGet: build.query<
      RunCronJobsApiAdminCronRunGetApiResponse,
      RunCronJobsApiAdminCronRunGetApiArg
    >({
      query: () => ({ url: `/api/admin/cron/run` }),
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
export type RunCronJobsApiAdminCronRunGetApiResponse = /** status 200 Successful Response */ any;
export type RunCronJobsApiAdminCronRunGetApiArg = void;
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
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export const {
  useRunCronJobsApiAdminCronRunGetQuery,
  useLazyRunCronJobsApiAdminCronRunGetQuery,
  useRunUpdateSubscriptionsApiAdminYoutubeUpdateSubscriptionsGetQuery,
  useLazyRunUpdateSubscriptionsApiAdminYoutubeUpdateSubscriptionsGetQuery,
  useRunUpdateChannelVideosApiAdminYoutubeUpdateChannelVideosGetQuery,
  useLazyRunUpdateChannelVideosApiAdminYoutubeUpdateChannelVideosGetQuery,
  useRunUpdateVideoCategoriesApiAdminYoutubeUpdateVideoCategoriesGetQuery,
  useLazyRunUpdateVideoCategoriesApiAdminYoutubeUpdateVideoCategoriesGetQuery,
} = injectedRtkApi;
