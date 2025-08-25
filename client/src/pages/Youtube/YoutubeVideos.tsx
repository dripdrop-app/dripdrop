import { Button, Divider, Group, Stack, Title } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { Helmet } from "react-helmet-async";

import VideosView from "../../components/Youtube/VideosView";

const YoutubeVideos = () => {
  const [enableAutoPlay, { toggle }] = useDisclosure(false);

  return (
    <Stack>
      <Helmet>
        <title>Videos</title>
      </Helmet>
      <Group justify="space-between">
        <Title order={2}>Videos</Title>
        <Button onClick={toggle}>{enableAutoPlay ? "Stop AutoPlay" : "Enable AutoPlay"}</Button>
      </Group>
      <Divider />
      <VideosView enableAutoPlay={enableAutoPlay} />
    </Stack>
  );
};

export default YoutubeVideos;
