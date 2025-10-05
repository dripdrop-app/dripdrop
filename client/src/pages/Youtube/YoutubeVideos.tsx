import { Button, Divider, Group, Stack, Title } from "@mantine/core";
import { Helmet } from "react-helmet-async";

import VideosView from "../../components/Youtube/VideosView";
import { useFooter } from "../../providers/FooterProvider";

const YoutubeVideos = () => {
  const { displayFooter, setDisplayFooter } = useFooter();

  return (
    <Stack>
      <Helmet>
        <title>Videos</title>
      </Helmet>
      <Group justify="space-between">
        <Title order={2}>Videos</Title>
        <Button onClick={() => setDisplayFooter(!displayFooter)}>
          {displayFooter ? "Stop AutoPlay" : "Enable AutoPlay"}
        </Button>
      </Group>
      <Divider />
      <VideosView enableAutoPlay={displayFooter} />
    </Stack>
  );
};

export default YoutubeVideos;
