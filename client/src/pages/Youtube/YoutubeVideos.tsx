import { Divider, Group, Stack, Title } from "@mantine/core";
import { Helmet } from "react-helmet-async";

import VideosView from "../../components/Youtube/VideosView";

const YoutubeVideos = () => {
  return (
    <Stack>
      <Helmet>
        <title>Videos</title>
      </Helmet>
      <Group justify="space-between">
        <Title order={2}>Videos</Title>
      </Group>
      <Divider />
      <VideosView />
    </Stack>
  );
};

export default YoutubeVideos;
