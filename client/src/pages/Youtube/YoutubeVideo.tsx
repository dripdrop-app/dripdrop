import { AspectRatio, Center, Divider, Grid, Loader, Stack, Title } from "@mantine/core";
import { useEffect, useMemo } from "react";
import { Helmet } from "react-helmet-async";
import { useParams } from "react-router-dom";

import { useYoutubeVideoQuery } from "../../api/youtube";
import VideoCard from "../../components/Youtube/VideoCard";
import VideoInformation from "../../components/Youtube/VideoInformation";
import VideoPlayer from "../../components/Youtube/VideoPlayer";
import { useBackgroundPlayer } from "../../providers/BackgroundPlayerProvider";

const YoutubeVideo = () => {
  const { id } = useParams();
  const videoStatus = useYoutubeVideoQuery({ videoId: id || "", relatedVideosLength: 4 }, { skip: !id });
  const { playerRef } = useBackgroundPlayer();

  const { relatedVideos, video } = useMemo(
    () =>
      videoStatus.data
        ? { relatedVideos: videoStatus.data.relatedVideos, video: videoStatus.data }
        : { video: null, relatedVideos: null },
    [videoStatus.data]
  );

  // TODO: Figure out how to test pause i =n sentry

  return (
    <Stack p="md">
      {videoStatus.isLoading ? (
        <Center>
          <Loader />
        </Center>
      ) : video ? (
        <>
          <Helmet>
            <title>{video.title}</title>
          </Helmet>
          <AspectRatio ratio={18 / 8}>
            <VideoPlayer video={video} playing={true} />
          </AspectRatio>
          <VideoInformation video={video} />
          <Divider />
          <Title order={3}>Related Videos</Title>
          <Grid
            justify="center"
            type="container"
            breakpoints={{ xs: "400px", sm: "800px", md: "1000px", lg: "1200px", xl: "2000px" }}
          >
            {relatedVideos?.map((video) => (
              <Grid.Col key={video.id} span={{ xs: 12, sm: 6, md: 4, lg: 3, xl: 2 }}>
                <VideoCard video={video} />
              </Grid.Col>
            ))}
          </Grid>
        </>
      ) : (
        <Center>Video could not be loaded</Center>
      )}
    </Stack>
  );
};

export default YoutubeVideo;
