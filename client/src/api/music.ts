import { api } from "./generated/musicApi";
import { Tags } from "./tags";

import { buildWebsocketURL } from "../config";

const enhancedApi = api
  .enhanceEndpoints({
    addTagTypes: [Tags.MUSIC_GROUPING, Tags.MUSIC_ARTWORK, Tags.MUSIC_TAGS, Tags.MUSIC_JOB, Tags.MUSIC_DOWNLOAD],
    endpoints: {
      getGroupingApiMusicGroupingGet: {
        providesTags: [Tags.MUSIC_GROUPING],
      },
      getArtworkApiMusicArtworkGet: {
        providesTags: [Tags.MUSIC_ARTWORK],
      },
      getTagsApiMusicTagsPost: {
        invalidatesTags: [Tags.MUSIC_TAGS],
      },
      getJobsApiMusicJobsListGet: {
        providesTags: (result) => {
          if (result) {
            const { jobs } = result;
            if (jobs.length > 0) {
              return jobs.map((job) => ({ type: Tags.MUSIC_JOB, id: job.id }));
            }
          }
          return [Tags.MUSIC_JOB];
        },
      },
      deleteJobApiMusicJobsJobIdDeleteDelete: {
        invalidatesTags: (_, error, jobId) => {
          if (!error) {
            return [{ type: Tags.MUSIC_JOB, id: jobId }];
          }
          return [];
        },
      },
    },
  })
  .injectEndpoints({
    endpoints: (build) => ({
      listenMusicJobs: build.query<null, void>({
        queryFn: () => ({ data: null }),
        onCacheEntryAdded: async (_, { cacheDataLoaded, cacheEntryRemoved, dispatch }) => {
          const url = buildWebsocketURL("music/jobs/listen");
          const ws = new WebSocket(url);
          try {
            await cacheDataLoaded;
            ws.onmessage = (event) => {
              const json = JSON.parse(event.data);
              const status = json.status;
              if (status === "PING") {
                return;
              } else if (status === "STARTED") {
                dispatch(enhancedApi.util.invalidateTags([Tags.MUSIC_JOB]));
              } else if (status === "COMPLETED") {
                dispatch(enhancedApi.util.invalidateTags([{ type: Tags.MUSIC_JOB, id: json.id }]));
              }
            };
          } catch (e) {
            console.error(e);
          }
          await cacheEntryRemoved;
          ws.close();
        },
      }),
    }),
  });

export default enhancedApi;
export const {
  useLazyGetArtworkApiMusicArtworkGetQuery: useLazyArtworkQuery,
  useLazyGetGroupingApiMusicGroupingGetQuery: useLazyGroupingQuery,
  useGetTagsApiMusicTagsPostMutation: useTagsMutation,
  useCreateJobApiMusicJobsCreatePostMutation: useCreateJobMutation,
  useGetJobsApiMusicJobsListGetQuery: useMusicJobsQuery,
  useListenMusicJobsQuery,
  useDeleteJobApiMusicJobsJobIdDeleteDeleteMutation: useDeleteJobMutation,
} = enhancedApi;
