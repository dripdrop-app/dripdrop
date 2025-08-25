import { Center, Checkbox, Grid, Group, Loader, MultiSelect, Pagination, Stack } from "@mantine/core";
import { FunctionComponent, useMemo } from "react";

import { useYoutubeVideoCategoriesQuery, useYoutubeVideosQuery } from "../../api/youtube";
import useSearchParams from "../../utils/useSearchParams";
import VideoAutoPlayer from "./VideoAutoPlayer";
import YoutubeVideoCard from "./VideoCard";

interface VideosViewProps {
  channelId?: string;
  enableAutoPlay?: boolean;
}

const VideosView: FunctionComponent<VideosViewProps> = ({ channelId, enableAutoPlay }) => {
  const { params, setSearchParams } = useSearchParams<{
    perPage: number;
    page: number;
    videoCategories: string[];
    likedOnly: boolean;
    queuedOnly: boolean;
  }>({
    perPage: 48,
    page: 1,
    videoCategories: [],
    likedOnly: false,
    queuedOnly: false,
  });

  const videosStatus = useYoutubeVideosQuery({
    ...params,
    videoCategories: params.videoCategories.map((id) => parseInt(id)),
    channelId,
  });
  const videoCategoriesStatus = useYoutubeVideoCategoriesQuery();

  const categories = useMemo(
    () => (videoCategoriesStatus.data ? videoCategoriesStatus.data.categories : []),
    [videoCategoriesStatus.data]
  );
  const { videos, totalPages } = useMemo(() => videosStatus.data ?? { videos: [], totalPages: 1 }, [videosStatus.data]);

  return (
    <Stack h="100%">
      <Group>
        <Checkbox
          label="Show Liked Only"
          checked={params.likedOnly}
          onChange={(e) => setSearchParams({ likedOnly: e.target.checked, page: 1 })}
        />
        <Checkbox
          label="Show Queued Only"
          checked={params.queuedOnly}
          onChange={(e) => setSearchParams({ queuedOnly: e.target.checked, page: 1 })}
        />
      </Group>
      <MultiSelect
        style={{ ...(!videoCategoriesStatus.data && { display: "none" }) }}
        label="Categories"
        placeholder="Select Categories"
        data={categories.map((category) => ({
          value: category.id.toString(),
          label: category.name,
        }))}
        value={params.videoCategories}
        onChange={(newCategories) => setSearchParams({ videoCategories: newCategories, page: 1 })}
      />
      <Center style={{ ...(!videosStatus.isFetching && videosStatus.currentData && { display: "none" }) }}>
        <Loader />
      </Center>
      <Stack style={{ ...(!videosStatus.data && { display: "none" }) }}>
        <Grid type="container" breakpoints={{ xs: "400px", sm: "800px", md: "1000px", lg: "1200px", xl: "2000px" }}>
          {videos.map((video) => (
            <Grid.Col key={video.id} span={{ xs: 12, sm: 6, md: 4, lg: 3, xl: 2 }}>
              <YoutubeVideoCard video={video} />
            </Grid.Col>
          ))}
        </Grid>
        <Center>
          <Pagination
            total={totalPages}
            value={params.page}
            onChange={(newPage) => setSearchParams({ page: newPage })}
          />
        </Center>
      </Stack>
      {enableAutoPlay && (
        <VideoAutoPlayer
          initialParams={{
            ...params,
            videoCategories: params.videoCategories.map((id) => parseInt(id)),
            channelId,
          }}
        />
      )}
    </Stack>
  );
};

export default VideosView;
