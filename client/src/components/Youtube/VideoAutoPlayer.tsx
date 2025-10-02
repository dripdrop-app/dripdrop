import {
  ActionIcon,
  Avatar,
  Box,
  Center,
  Divider,
  Group,
  Indicator,
  Modal,
  Pagination,
  Slider,
  Stack,
  Text,
  Title,
} from "@mantine/core";
import { skipToken } from "@reduxjs/toolkit/query/react";
import { Fragment, FunctionComponent, useEffect, useMemo, useRef, useState } from "react";
import { CgPlayTrackNext, CgPlayTrackPrev } from "react-icons/cg";
import { FaAngleUp, FaPause, FaPlay } from "react-icons/fa";

import { useDisclosure } from "@mantine/hooks";
import ReactPlayer from "react-player";
import { Link } from "react-router-dom";
import { useYoutubeVideosQuery } from "../../api/youtube";
import { VideoLikeButton, VideoQueueButton } from "./VideoButtons";
import VideoPlayer from "./VideoPlayer";
import { GetYoutubeVideosApiYoutubeVideosListGetApiArg as YoutubeVideosParams } from "../../api/generated/youtubeApi";
import { createPortal } from "react-dom";
import { useFooter } from "../../providers/FooterProvider";

interface VideoAutoPlayerProps {
  initialParams: YoutubeVideosParams;
}

interface VideoAutoPlayerQueueProps {
  initialParams: YoutubeVideosParams;
  currentVideoId?: string;
  onClick: (params: YoutubeVideosParams, videoIndex: number) => void;
}

const VideoAutoPlayerQueue: FunctionComponent<VideoAutoPlayerQueueProps> = ({
  initialParams,
  onClick,
  currentVideoId,
}) => {
  const [currentParams, setCurrentParams] = useState<YoutubeVideosParams>(initialParams);

  const videosStatus = useYoutubeVideosQuery(currentParams);

  const totalPages = useMemo(() => videosStatus.data?.totalPages ?? 1, [videosStatus.data]);
  const videos = useMemo(() => videosStatus.data?.videos ?? [], [videosStatus.data]);

  return (
    <Stack h="100%">
      <Title order={4}>Queue</Title>
      <Box style={{ overflowX: "hidden", overflowY: "auto" }}>
        {videos.map((video, i) => {
          return (
            <Fragment key={video.id}>
              <Box className="hover-brighten" style={{ cursor: "pointer" }} onClick={() => onClick(currentParams, i)}>
                <Group gap="sm" p="xs" wrap="nowrap">
                  <Indicator processing size={16} disabled={video.id !== currentVideoId}>
                    <Avatar size="md" src={video.thumbnail} style={{ borderRadius: 10 }} />
                  </Indicator>
                  <Stack gap={0} style={{ overflowX: "hidden" }}>
                    <Text truncate="end">{video.title}</Text>
                    <Text c="dimmed" truncate="end">
                      {video.channel.title}
                    </Text>
                  </Stack>
                </Group>
              </Box>
              <Divider />
            </Fragment>
          );
        })}
      </Box>
      <Center>
        <Pagination
          total={totalPages}
          value={currentParams?.page}
          onChange={(newPage) => setCurrentParams({ ...currentParams, page: newPage })}
        />
      </Center>
    </Stack>
  );
};

const VideoAutoPlayer: FunctionComponent<VideoAutoPlayerProps> = ({ initialParams }) => {
  const [currentParams, setCurrentParams] = useState<YoutubeVideosParams | undefined>();
  const [currentVideoIndex, setCurrentVideoIndex] = useState(0);
  const [videoProgress, setVideoProgress] = useState({
    duration: 0,
    played: 0,
  });
  const [playing, setPlaying] = useState(true);
  const hiddenPlayerRef = useRef<ReactPlayer | null>(null);
  const modalPlayerRef = useRef<ReactPlayer | null>(null);

  const [expand, { toggle: toggleExpand }] = useDisclosure(false);
  const { footerRef } = useFooter();

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

  if (!footerRef.current) {
    return null;
  }

  return createPortal(
    <Stack align="center" w="100%" gap={7}>
      <Slider
        w={{ base: "90%", md: "95%" }}
        py="lg"
        marks={[
          { value: 0, label: "0:00" },
          { value: 100, label: convertToTimeString(videoProgress.duration) },
        ]}
        label={convertToTimeString(videoProgress.played)}
        labelAlwaysOn={true}
        value={Math.floor((videoProgress.played / videoProgress.duration) * 100)}
        onChange={(value) => {
          if (hiddenPlayerRef.current) {
            hiddenPlayerRef.current.seekTo(value / 100, "fraction");
          }
        }}
      />
      {!expand && (
        <VideoPlayer
          style={{ display: "none" }}
          ref={hiddenPlayerRef}
          video={currentVideo}
          playing={playing}
          onReady={() => {
            if (videoProgress.played) {
              hiddenPlayerRef.current?.seekTo(videoProgress.played, "seconds");
            }
          }}
          onDuration={(duration) => {
            setVideoProgress({ ...videoProgress, duration });
          }}
          onProgress={(state) => {
            setVideoProgress({ ...videoProgress, played: state.playedSeconds });
          }}
          onEnd={() => setCurrentVideoIndex(currentVideoIndex + 1)}
        />
      )}
      <Modal opened={expand} onClose={toggleExpand} size="lg" title={currentVideo?.title}>
        <Stack>
          <VideoPlayer
            ref={modalPlayerRef}
            video={currentVideo}
            playing={playing}
            height="47vh"
            onPause={() => {
              setPlaying(false);
            }}
            onPlay={() => {
              setPlaying(true);
            }}
            onReady={() => {
              if (videoProgress.played) {
                modalPlayerRef.current?.seekTo(videoProgress.played, "seconds");
              }
            }}
            onDuration={(duration) => {
              setVideoProgress({ ...videoProgress, duration });
            }}
            onProgress={(state) => {
              setVideoProgress({ ...videoProgress, played: state.playedSeconds });
            }}
            onEnd={() => setCurrentVideoIndex(currentVideoIndex + 1)}
          />
          <Box h="30vh">
            {currentParams && (
              <VideoAutoPlayerQueue
                initialParams={currentParams}
                onClick={(newParams, newVideoIndex) => {
                  setCurrentParams(newParams);
                  setCurrentVideoIndex(newVideoIndex);
                  setVideoProgress({ duration: 0, played: 0 });
                  hiddenPlayerRef.current?.seekTo(0, "seconds");
                  modalPlayerRef.current?.seekTo(0, "seconds");
                }}
                currentVideoId={currentVideo?.id}
              />
            )}
          </Box>
        </Stack>
      </Modal>
      <Group w={{ base: "90%", md: "95%" }} gap="xl" justify="center" wrap="nowrap" style={{ overflowX: "hidden" }}>
        <Group wrap="nowrap" style={{ overflowX: "hidden" }}>
          <Avatar size="md" src={currentVideo?.thumbnail} style={{ borderRadius: 10 }} />
          <Stack gap={0} style={{ overflowX: "hidden" }}>
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
              truncate="end"
              to={channelLink}
            >
              {currentVideo?.channel.title}
            </Text>
          </Stack>
        </Group>
        <Group wrap="nowrap" visibleFrom="sm">
          {currentVideo && <VideoLikeButton video={currentVideo} />}
          {currentVideo && <VideoQueueButton video={currentVideo} />}
        </Group>
        <Group wrap="nowrap">
          <ActionIcon
            className="hover-darken"
            variant="transparent"
            onClick={() => setCurrentVideoIndex(currentVideoIndex - 1)}
          >
            <CgPlayTrackPrev size={25} />
          </ActionIcon>
          <ActionIcon className="hover-darken" variant="transparent" onClick={() => setPlaying(!playing)}>
            {playing ? <FaPause /> : <FaPlay />}
          </ActionIcon>
          <ActionIcon
            className="hover-darken"
            variant="transparent"
            onClick={() => setCurrentVideoIndex(currentVideoIndex + 1)}
          >
            <CgPlayTrackNext size={25} />
          </ActionIcon>
          <ActionIcon className="hover-darken" variant="transparent" onClick={toggleExpand}>
            <FaAngleUp />
          </ActionIcon>
        </Group>
      </Group>
    </Stack>,
    footerRef.current
  );
};

export default VideoAutoPlayer;
