import { api } from "./generated/youtubeApi";
import { Tags } from "./tags";
import { transformErrorResponse } from "./utils";

import { buildWebsocketURL } from "../config";

const enhancedApi = api
  .enhanceEndpoints({
    addTagTypes: [
      Tags.YOUTUBE_CHANNEL,
      Tags.YOUTUBE_CHANNEL_VIDEOS,
      Tags.YOUTUBE_LIKE_VIDEOS,
      Tags.YOUTUBE_QUEUE_VIDEOS,
      Tags.YOUTUBE_SUBSCRIPTION,
      Tags.YOUTUBE_USER_CHANNEL,
      Tags.YOUTUBE_VIDEO,
      Tags.YOUTUBE_VIDEO_CATEGORY,
    ],
    endpoints: {
      getYoutubeVideoCategoriesApiYoutubeVideosCategoriesGet: {
        providesTags: (result) => {
          if (result) {
            return result.categories.map((category) => ({ type: Tags.YOUTUBE_VIDEO_CATEGORY, id: category.id }));
          }
          return [];
        },
      },
      getYoutubeVideoApiYoutubeVideosVideoIdGet: {
        providesTags: (result) => {
          if (result) {
            const tags = [{ type: Tags.YOUTUBE_VIDEO, id: result.id }];
            if (result.relatedVideos) {
              tags.push(...result.relatedVideos.map((video) => ({ type: Tags.YOUTUBE_VIDEO, id: video.id })));
            }
            return tags;
          }
          return [];
        },
      },
      getYoutubeVideosApiYoutubeVideosListGet: {
        providesTags: (result, _, args) => {
          const tags = [];
          if (result) {
            tags.push(...result.videos.map((video) => ({ type: Tags.YOUTUBE_VIDEO, id: video.id })));
          }
          if (args.likedOnly) {
            tags.push(Tags.YOUTUBE_LIKE_VIDEOS);
          } else if (args.queuedOnly) {
            tags.push(Tags.YOUTUBE_QUEUE_VIDEOS);
          }
          if (args.channelId) {
            tags.push({ type: Tags.YOUTUBE_CHANNEL_VIDEOS, id: args.channelId });
          }
          return tags;
        },
      },
      getYoutubeSubscriptionsApiYoutubeSubscriptionsListGet: {
        providesTags: (result) => {
          if (result) {
            return result.channels.map((channel) => ({
              type: Tags.YOUTUBE_CHANNEL,
              id: channel.id,
            }));
          }
          return [];
        },
      },
      addUserSubscriptionApiYoutubeSubscriptionsUserPut: {
        invalidatesTags: (result) => {
          if (result) {
            return [Tags.YOUTUBE_CHANNEL, { type: Tags.YOUTUBE_CHANNEL, id: result.id }];
          }
          return [];
        },
      },
      deleteUserSubscriptionApiYoutubeSubscriptionsUserDelete: {
        invalidatesTags: (_, error, channelId) => {
          if (!error) {
            return [
              { type: Tags.YOUTUBE_SUBSCRIPTION, id: channelId },
              { type: Tags.YOUTUBE_CHANNEL, id: channelId },
            ];
          }
          return [];
        },
      },
      addYoutubeVideoLikeApiYoutubeVideosVideoIdLikePut: {
        invalidatesTags: (_, error, videoId) => {
          if (!error) {
            return [{ type: Tags.YOUTUBE_VIDEO, id: videoId }, Tags.YOUTUBE_LIKE_VIDEOS];
          }
          return [];
        },
      },
      deleteYoutubeVideoLikeApiYoutubeVideosVideoIdLikeDelete: {
        invalidatesTags: (_, error, videoId) => {
          if (!error) {
            return [{ type: Tags.YOUTUBE_VIDEO, id: videoId }];
          }
          return [];
        },
      },
      addYoutubeVideoQueueApiYoutubeVideosVideoIdQueuePut: {
        invalidatesTags: (_, error, videoId) => {
          if (!error) {
            return [{ type: Tags.YOUTUBE_VIDEO, id: videoId }, Tags.YOUTUBE_QUEUE_VIDEOS];
          }
          return [];
        },
      },
      deleteYoutubeVideoQueueApiYoutubeVideosVideoIdQueueDelete: {
        invalidatesTags: (_, error, videoId) => {
          if (!error) {
            return [{ type: Tags.YOUTUBE_VIDEO, id: videoId }];
          }
          return [];
        },
      },
      addYoutubeVideoWatchApiYoutubeVideosVideoIdWatchPut: {
        invalidatesTags: (_, error, videoId) => {
          if (!error) {
            return [{ type: Tags.YOUTUBE_VIDEO, id: videoId }];
          }
          return [];
        },
      },
      getYoutubeChannelApiYoutubeChannelsChannelIdGet: {
        providesTags: (result) => (result ? [{ type: Tags.YOUTUBE_CHANNEL, id: result.id }] : []),
      },
      getUserYoutubeChannelApiYoutubeChannelsUserGet: {
        providesTags: () => [Tags.YOUTUBE_USER_CHANNEL],
      },
      updateUserYoutubeChannelApiYoutubeChannelsUserPost: {
        invalidatesTags: (_, error) => {
          if (!error) {
            return [Tags.YOUTUBE_USER_CHANNEL];
          }
          return [];
        },
        transformErrorResponse,
      },
    },
  })
  .injectEndpoints({
    endpoints: (build) => ({
      listenYoutubeChannels: build.query<null, void>({
        queryFn: () => ({ data: null }),
        onCacheEntryAdded: async (_, { cacheDataLoaded, cacheEntryRemoved, dispatch }) => {
          const url = buildWebsocketURL("youtube/channel/listen");
          const ws = new WebSocket(url);
          try {
            await cacheDataLoaded;
            ws.onmessage = (event) => {
              const json = JSON.parse(event.data);
              const status = json.status;
              if (status === "PING") {
                return;
              }
              const id = json.id;
              const updating = json.updating;
              dispatch(enhancedApi.util.invalidateTags([{ type: Tags.YOUTUBE_CHANNEL, id }]));
              if (!updating) {
                dispatch(enhancedApi.util.invalidateTags([{ type: Tags.YOUTUBE_CHANNEL_VIDEOS, id }]));
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
  useGetYoutubeVideoCategoriesApiYoutubeVideosCategoriesGetQuery: useYoutubeVideoCategoriesQuery,
  useGetYoutubeVideoApiYoutubeVideosVideoIdGetQuery: useYoutubeVideoQuery,
  useGetYoutubeVideosApiYoutubeVideosListGetQuery: useYoutubeVideosQuery,
  useGetYoutubeSubscriptionsApiYoutubeSubscriptionsListGetQuery: useYoutubeSubscriptionsQuery,
  useAddYoutubeVideoLikeApiYoutubeVideosVideoIdLikePutMutation: useAddYoutubeVideoLikeMutation,
  useDeleteYoutubeVideoLikeApiYoutubeVideosVideoIdLikeDeleteMutation: useDeleteYoutubeVideoLikeMutation,
  useAddYoutubeVideoQueueApiYoutubeVideosVideoIdQueuePutMutation: useAddYoutubeVideoQueueMutation,
  useDeleteYoutubeVideoQueueApiYoutubeVideosVideoIdQueueDeleteMutation: useDeleteYoutubeVideoQueueMutation,
  useGetYoutubeChannelApiYoutubeChannelsChannelIdGetQuery: useYoutubeChannelQuery,
  useListenYoutubeChannelsQuery,
  useAddYoutubeVideoWatchApiYoutubeVideosVideoIdWatchPutMutation: useAddYoutubeVideoWatchMutation,
  useUpdateUserYoutubeChannelApiYoutubeChannelsUserPostMutation: useUpdateUserYoutubeChannelMutation,
  useGetUserYoutubeChannelApiYoutubeChannelsUserGetQuery: useUserYoutubeChannelQuery,
  useAddUserSubscriptionApiYoutubeSubscriptionsUserPutMutation: useAddYoutubeSubscriptionMutation,
  useDeleteUserSubscriptionApiYoutubeSubscriptionsUserDeleteMutation: useRemoveSubscriptionMutation,
} = enhancedApi;
