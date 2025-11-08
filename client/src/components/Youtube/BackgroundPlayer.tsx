import { ActionIcon, Avatar, Box, Card, CloseButton, Group, Overlay, Slider, Stack, Text } from "@mantine/core";
import { useEffect, useState } from "react";
import { CgPlayTrackNext, CgPlayTrackPrev } from "react-icons/cg";
import { FaAngleUp, FaPause, FaPlay } from "react-icons/fa";

import { useClickOutside, useDisclosure } from "@mantine/hooks";
import { Link } from "react-router-dom";
import { VideoLikeButton, VideoQueueButton } from "./VideoButtons";
import VideoPlayer from "./VideoPlayer";
import { createPortal } from "react-dom";
import { useFooter } from "../../providers/FooterProvider";
import { useOverlay } from "../../providers/OverlayProvider";
import { useBackgroundPlayer } from "../../providers/BackgroundPlayerProvider";
import { MdClose } from "react-icons/md";

const BackgroundPlayer = () => {
  const { currentVideo, advanceQueue, playerRef, recedeQueue, setShowPlayer } = useBackgroundPlayer();

  const [videoProgress, setVideoProgress] = useState({
    duration: 0,
    played: 0,
  });
  const [playing, setPlaying] = useState(true);

  const [expand, { toggle: toggleExpand }] = useDisclosure(false);
  const { footerRef } = useFooter();
  const { overlayRef } = useOverlay();
  const clickOutsideRef = useClickOutside(() => {
    if (expand) toggleExpand();
  });

  const channelLink = `/youtube/channel/${currentVideo?.channel.id}`;
  const videoLink = `/youtube/video/${currentVideo?.id}`;

  const convertToTimeString = (seconds: number) => {
    seconds = Math.round(seconds);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds < 10 ? `0${remainingSeconds}` : remainingSeconds}`;
  };

  useEffect(() => {
    setVideoProgress({ played: 0, duration: 0 });
  }, [currentVideo]);

  if (!footerRef.current || !overlayRef.current) {
    return null;
  }

  const VideoPlayerOverlayPortal = createPortal(
    <Overlay component={Box} display={expand ? "block" : "none"} fixed>
      <Card
        ref={clickOutsideRef}
        pos="absolute"
        top="5vh"
        right="10vw"
        w="80vw"
        padding="md"
        withBorder
        radius="md"
        shadow="md"
        display="flex"
      >
        <Card.Section inheritPadding py="xs">
          <Group justify="space-between" wrap="nowrap">
            <Group wrap="nowrap" style={{ overflowX: "hidden" }}>
              <Avatar size="md" src={currentVideo?.channel.thumbnail} style={{ borderRadius: 10 }} />
              <Text truncate="end">{currentVideo?.title}</Text>
            </Group>
            <CloseButton onClick={toggleExpand} />
          </Group>
        </Card.Section>
        <Card.Section h="80vh">
          <VideoPlayer
            ref={playerRef}
            video={currentVideo}
            playing={playing}
            onPlay={() => setPlaying(true)}
            onPause={() => setPlaying(false)}
            onDuration={(duration) => {
              setVideoProgress({ ...videoProgress, duration });
            }}
            onProgress={(state) => {
              setVideoProgress({ ...videoProgress, played: state.playedSeconds });
            }}
            onEnd={() => advanceQueue()}
          />
        </Card.Section>
      </Card>
    </Overlay>,
    overlayRef.current
  );

  return createPortal(
    <Stack align="center" w="100%" gap={7} pos="relative">
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
          if (playerRef.current) {
            playerRef.current.seekTo(value / 100, "fraction");
          }
        }}
      />
      {VideoPlayerOverlayPortal}
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
            onClick={() => {
              if (videoProgress.played < 5) {
                recedeQueue();
              } else {
                playerRef.current?.seekTo(0);
              }
            }}
          >
            <CgPlayTrackPrev size={25} />
          </ActionIcon>
          <ActionIcon className="hover-darken" variant="transparent" onClick={() => setPlaying(!playing)}>
            {playing ? <FaPause /> : <FaPlay />}
          </ActionIcon>
          <ActionIcon className="hover-darken" variant="transparent" onClick={advanceQueue}>
            <CgPlayTrackNext size={25} />
          </ActionIcon>
          <ActionIcon className="hover-darken" variant="transparent" onClick={toggleExpand}>
            <FaAngleUp />
          </ActionIcon>
          <ActionIcon className="hover-darken" variant="transparent" onClick={() => setShowPlayer(false)}>
            <MdClose />
          </ActionIcon>
        </Group>
      </Group>
    </Stack>,
    footerRef.current
  );
};

export default BackgroundPlayer;
