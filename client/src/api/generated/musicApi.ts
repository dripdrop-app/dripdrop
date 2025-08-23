import { api } from "./api";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    createJobApiMusicJobsCreatePost: build.mutation<
      CreateJobApiMusicJobsCreatePostApiResponse,
      CreateJobApiMusicJobsCreatePostApiArg
    >({
      query: (queryArg) => ({ url: `/api/music/jobs/create`, method: "POST", body: queryArg }),
    }),
    deleteJobApiMusicJobsJobIdDeleteDelete: build.mutation<
      DeleteJobApiMusicJobsJobIdDeleteDeleteApiResponse,
      DeleteJobApiMusicJobsJobIdDeleteDeleteApiArg
    >({
      query: (queryArg) => ({ url: `/api/music/jobs/${queryArg}/delete`, method: "DELETE" }),
    }),
    downloadJobApiMusicJobsJobIdDownloadGet: build.query<
      DownloadJobApiMusicJobsJobIdDownloadGetApiResponse,
      DownloadJobApiMusicJobsJobIdDownloadGetApiArg
    >({
      query: (queryArg) => ({ url: `/api/music/jobs/${queryArg}/download` }),
    }),
    getJobsApiMusicJobsListGet: build.query<GetJobsApiMusicJobsListGetApiResponse, GetJobsApiMusicJobsListGetApiArg>({
      query: (queryArg) => ({
        url: `/api/music/jobs/list`,
        params: {
          page: queryArg.page,
          per_page: queryArg.perPage,
        },
      }),
    }),
    getGroupingApiMusicGroupingGet: build.query<
      GetGroupingApiMusicGroupingGetApiResponse,
      GetGroupingApiMusicGroupingGetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/music/grouping`,
        params: {
          video_url: queryArg,
        },
      }),
    }),
    getArtworkApiMusicArtworkGet: build.query<
      GetArtworkApiMusicArtworkGetApiResponse,
      GetArtworkApiMusicArtworkGetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/music/artwork`,
        params: {
          artwork_url: queryArg,
        },
      }),
    }),
    getTagsApiMusicTagsPost: build.mutation<GetTagsApiMusicTagsPostApiResponse, GetTagsApiMusicTagsPostApiArg>({
      query: (queryArg) => ({ url: `/api/music/tags`, method: "POST", body: queryArg }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type CreateJobApiMusicJobsCreatePostApiResponse = /** status 201 Successful Response */ any;
export type CreateJobApiMusicJobsCreatePostApiArg = CreateMusicJob;
export type DeleteJobApiMusicJobsJobIdDeleteDeleteApiResponse = /** status 200 Successful Response */ any;
export type DeleteJobApiMusicJobsJobIdDeleteDeleteApiArg = string;
export type DownloadJobApiMusicJobsJobIdDownloadGetApiResponse = /** status 200 Successful Response */ any;
export type DownloadJobApiMusicJobsJobIdDownloadGetApiArg = string;
export type GetJobsApiMusicJobsListGetApiResponse = /** status 200 Successful Response */ MusicJobListResponse;
export type GetJobsApiMusicJobsListGetApiArg = {
  page: number;
  perPage: number;
};
export type GetGroupingApiMusicGroupingGetApiResponse = /** status 200 Successful Response */ GroupingResponse;
export type GetGroupingApiMusicGroupingGetApiArg = string;
export type GetArtworkApiMusicArtworkGetApiResponse = /** status 200 Successful Response */ ResolvedArtworkResponse;
export type GetArtworkApiMusicArtworkGetApiArg = string;
export type GetTagsApiMusicTagsPostApiResponse = /** status 200 Successful Response */ TagsResponse;
export type GetTagsApiMusicTagsPostApiArg = BodyGetTagsApiMusicTagsPost;
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export type CreateMusicJob = {
  file?: Blob | null;
  video_url?: string | null;
  artwork_url?: string | null;
  title: string;
  artist: string;
  album: string;
  grouping?: string | null;
};
export type MusicJobResponse = {
  id: string;
  userEmail: string;
  title: string;
  artist: string;
  album: string;
  grouping?: string | null;
  artworkUrl?: string | null;
  artworkFilename?: string | null;
  originalFilename?: string | null;
  filenameUrl?: string | null;
  videoUrl?: string | null;
  downloadFilename?: string | null;
  downloadUrl?: string | null;
  completed?: string | null;
  failed?: string | null;
};
export type MusicJobListResponse = {
  jobs: MusicJobResponse[];
  totalPages: number;
};
export type GroupingResponse = {
  grouping: string;
};
export type ResolvedArtworkResponse = {
  resolvedArtworkUrl: string;
};
export type TagsResponse = {
  title?: string | null;
  artist?: string | null;
  album?: string | null;
  grouping?: string | null;
  artworkUrl?: string | null;
};
export type BodyGetTagsApiMusicTagsPost = {
  file: Blob;
};
export const {
  useCreateJobApiMusicJobsCreatePostMutation,
  useDeleteJobApiMusicJobsJobIdDeleteDeleteMutation,
  useDownloadJobApiMusicJobsJobIdDownloadGetQuery,
  useLazyDownloadJobApiMusicJobsJobIdDownloadGetQuery,
  useGetJobsApiMusicJobsListGetQuery,
  useLazyGetJobsApiMusicJobsListGetQuery,
  useGetGroupingApiMusicGroupingGetQuery,
  useLazyGetGroupingApiMusicGroupingGetQuery,
  useGetArtworkApiMusicArtworkGetQuery,
  useLazyGetArtworkApiMusicArtworkGetQuery,
  useGetTagsApiMusicTagsPostMutation,
} = injectedRtkApi;
