import { Avatar, Box, Card, Flex, Image, Overlay, Stack, Text, Tooltip } from "@mantine/core";
import { useHover, useOs } from "@mantine/hooks";
import { FunctionComponent } from "react";
import { Link } from "react-router-dom";

import { YoutubeVideoResponse as YoutubeVideo } from "../../api/generated/youtubeApi";
import { VideoPlayInBackgroundButton, VideoQueueButton, VideoWatchButton } from "./VideoButtons";
import VideoCategoryIcon from "./VideoCategoryIcon";

interface VideoCardProps {
  video: YoutubeVideo;
  onPlayVideoInBackground?: () => void;
}

const VideoCard: FunctionComponent<VideoCardProps> = ({ video, onPlayVideoInBackground }) => {
  const { hovered, ref } = useHover();
  const os = useOs();

  const isMobile = os === "android" || os === "ios";

  const hideOverlay = !isMobile && !hovered && !video.queued && !video.watched;

  const hideQueueButton = !isMobile && !hovered && !video.queued;

  const publishedAt = new Date(video.publishedAt).toLocaleDateString();
  const channelLink = `/youtube/channel/${video.channel.id}`;
  const videoLink = `/youtube/video/${video.id}`;

  return (
    <Box>
      <Card>
        <Card.Section ref={ref} pos="relative">
          <Image src={video.thumbnail} alt="thumbnail" />
          <Overlay
            style={{ ...(hideOverlay && { display: "none" }) }}
            opacity={0.5}
            color="black"
            zIndex={1}
            component={Link}
            to={videoLink}
          />
          <Flex
            pos="absolute"
            right="5%"
            top="5%"
            style={{
              ...(hideQueueButton && { display: "none" }),
              zIndex: 2,
            }}
          >
            <VideoQueueButton video={video} />
          </Flex>
          <Flex pos="absolute" left="5%" top="5%" style={{ zIndex: 2 }}>
            <VideoWatchButton video={video} />
          </Flex>
          <Tooltip label={video.category.name}>
            <Flex
              style={(theme) => ({
                zIndex: 2,
                borderRadius: theme.spacing.xs,
              })}
              pos="absolute"
              right="5%"
              bottom="5%"
              bg="dark.7"
              p="xs"
            >
              <VideoCategoryIcon categoryId={video.category.id} color="white" />
            </Flex>
          </Tooltip>
          {onPlayVideoInBackground && (
            <Flex pos="absolute" left="45%" top="45%" style={{ zIndex: 2 }}>
              <VideoPlayInBackgroundButton onPlayVideoInBackground={onPlayVideoInBackground} />
            </Flex>
          )}
        </Card.Section>
        <Stack py={10}>
          <Stack className="hover-underline">
            <Text component={Link} to={videoLink}>
              {video.title}
            </Text>
          </Stack>
          <Flex justify="space-between">
            <Text
              variant="link"
              c="dimmed"
              component={Link}
              to={channelLink}
              className="hover-underline"
              style={{ overflow: "hidden" }}
            >
              <Flex>
                <Avatar size="sm" src={video.channel.thumbnail} style={{ borderRadius: 10 }} />
                <Text style={{ overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis" }}>
                  {video.channel.title}
                </Text>
              </Flex>
            </Text>
            <Text ta="right" style={{ flex: 1 }} c="dimmed">
              {publishedAt}
            </Text>
          </Flex>
        </Stack>
      </Card>
    </Box>
  );
};

export default VideoCard;
