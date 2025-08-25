import { ActionIcon, Avatar, Flex, Group, Slider, Space, Stack, Text } from "@mantine/core";
import { skipToken } from "@reduxjs/toolkit/query/react";
import { FunctionComponent, useEffect, useMemo, useRef, useState } from "react";
import { CgPlayTrackNext, CgPlayTrackPrev } from "react-icons/cg";
import { FaAngleDown, FaAngleUp, FaPause, FaPlay } from "react-icons/fa";

import { useDisclosure } from "@mantine/hooks";
import ReactPlayer from "react-player";
import { Link } from "react-router-dom";
import { useYoutubeVideosQuery } from "../../api/youtube";
import { VideoLikeButton, VideoQueueButton } from "./VideoButtons";
import VideoPlayer from "./VideoPlayer";
import { GetYoutubeVideosApiYoutubeVideosListGetApiArg as YoutubeVideosParams } from "../../api/generated/youtubeApi";

interface VideoAutoPlayerProps {
  initialParams: YoutubeVideosParams;
}

const VideoAutoPlayer: FunctionComponent<VideoAutoPlayerProps> = ({ initialParams }) => {
  const [currentParams, setCurrentParams] = useState<YoutubeVideosParams | undefined>();
  const [currentVideoIndex, setCurrentVideoIndex] = useState(0);
  const [videoProgress, setVideoProgress] = useState({
    duration: 0,
    played: 0,
  });

  const playerRef = useRef<ReactPlayer>(null);

  const [playing, { toggle: togglePlaying }] = useDisclosure(true);
  const [expand, { toggle: toggleExpand }] = useDisclosure(false);

  const videosStatus = useYoutubeVideosQuery(currentParams ?? skipToken, { skip: !currentParams });

  const currentVideo = useMemo(() => {
    const videos = videosStatus.data?.videos ?? [];
    if (videos.length === 0) {
      return null;
    }
    return videos[currentVideoIndex];
  }, [currentVideoIndex, videosStatus.data]);

  const channelLink = `/youtube/channel/${currentVideo?.channel.id}`;
  const videoLink = `/youtube/video/${currentVideo?.id}`;

  const convertToTimeString = (seconds: number) => {
    seconds = Math.round(seconds);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds < 10 ? `0${remainingSeconds}` : remainingSeconds}`;
  };

  useEffect(() => {
    if (!currentParams) {
      setCurrentParams(initialParams);
    }
  }, [currentParams, initialParams]);

  useEffect(() => {
    if (currentParams) {
      if (currentVideoIndex >= currentParams?.perPage) {
        setCurrentParams({ ...currentParams, page: currentParams.page + 1 });
        setCurrentVideoIndex(0);
      } else if (currentVideoIndex < 0 && currentParams?.page > 1) {
        setCurrentParams({ ...currentParams, page: currentParams.page - 1 });
        setCurrentVideoIndex(currentParams.perPage - 1);
      }
    }
  }, [currentParams, currentVideoIndex]);

  return (
    <Flex
      pos="sticky"
      bottom="0px"
      align="center"
      mb="-16px"
      mr="-16px"
      ml="-16px"
      mt="auto"
      bg="dark.7"
      style={{ zIndex: 99 }}
    >
      <Stack align="center" w="100%" gap={0}>
        <Slider
          display={!expand ? "block" : "none"}
          w="80%"
          py="lg"
          marks={[
            { value: 0, label: "0:00" },
            { value: 100, label: convertToTimeString(videoProgress.duration) },
          ]}
          label={convertToTimeString(videoProgress.played)}
          value={Math.floor((videoProgress.played / videoProgress.duration) * 100)}
          onChange={(value) => {
            console.log(value);
            if (playerRef.current) {
              playerRef.current.seekTo(value / 100, "fraction");
            }
          }}
        />
        <VideoPlayer
          ref={playerRef}
          video={currentVideo}
          playing={playing}
          height={expand ? `75vh` : "0px"}
          onDuration={(duration) => {
            setVideoProgress({ ...videoProgress, duration });
          }}
          onProgress={(state) => {
            setVideoProgress({ ...videoProgress, played: state.playedSeconds });
          }}
          onEnd={() => setCurrentVideoIndex(currentVideoIndex + 1)}
        />
        <Group p="sm" align="center">
          <Avatar size="md" src={currentVideo?.thumbnail} style={{ borderRadius: 10 }} />
          <Stack gap={0}>
            <Text
              component={Link}
              className="hover-underline"
              style={{
                fontSize: "0.9em",
              }}
              truncate="end"
              to={videoLink}
            >
              {currentVideo?.title}
            </Text>
            <Text
              component={Link}
              className="hover-underline"
              style={{
                fontSize: "0.75em",
              }}
              to={channelLink}
            >
              {currentVideo?.channel.title}
            </Text>
          </Stack>
          <Space w="lg" />
          <Group wrap="nowrap">
            {currentVideo && <VideoLikeButton video={currentVideo} />}
            {currentVideo && <VideoQueueButton video={currentVideo} />}
          </Group>
          <Space w="lg" />
          <Group wrap="nowrap">
            <ActionIcon
              className="hover-darken"
              variant="transparent"
              onClick={() => setCurrentVideoIndex(currentVideoIndex - 1)}
            >
              <CgPlayTrackPrev size={25} />
            </ActionIcon>
            <ActionIcon
              className="hover-darken"
              variant="transparent"
              style={{ ...(playing && { display: "none" }) }}
              onClick={togglePlaying}
            >
              <FaPlay />
            </ActionIcon>
            <ActionIcon
              className="hover-darken"
              variant="transparent"
              style={{ ...(!playing && { display: "none" }) }}
              onClick={togglePlaying}
            >
              <FaPause />
            </ActionIcon>
            <ActionIcon
              className="hover-darken"
              variant="transparent"
              onClick={() => setCurrentVideoIndex(currentVideoIndex + 1)}
            >
              <CgPlayTrackNext size={25} />
            </ActionIcon>
          </Group>
          <ActionIcon
            className="hover-darken"
            variant="transparent"
            style={{ ...(expand && { display: "none" }) }}
            onClick={toggleExpand}
          >
            <FaAngleUp />
          </ActionIcon>
          <ActionIcon
            className="hover-darken"
            variant="transparent"
            style={{ ...(!expand && { display: "none" }) }}
            onClick={toggleExpand}
          >
            <FaAngleDown />
          </ActionIcon>
        </Group>
      </Stack>
    </Flex>
  );
};

export default VideoAutoPlayer;
