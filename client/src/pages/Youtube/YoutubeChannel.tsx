import { Avatar, Box, Button, Center, Divider, Flex, Group, Loader, Stack, Title } from "@mantine/core";
import { useMemo } from "react";
import { Helmet } from "react-helmet-async";
import { useParams } from "react-router-dom";

import { useListenYoutubeChannelsQuery, useYoutubeChannelQuery } from "../../api/youtube";
import { SubscribeButton } from "../../components/Youtube/ChannelButtons";
import VideosView from "../../components/Youtube/VideosView";
import { useFooter } from "../../providers/FooterProvider";

const YoutubeChannel = () => {
  const { id } = useParams();
  const channelStatus = useYoutubeChannelQuery(id || "", { skip: !id });
  const { displayFooter, setDisplayFooter } = useFooter();

  const channel = useMemo(() => channelStatus.data, [channelStatus.data]);

  useListenYoutubeChannelsQuery();

  if (channelStatus.isLoading) {
    return (
      <Center>
        <Loader />
      </Center>
    );
  } else if (!channel) {
    return <Center>Channel could not be loaded</Center>;
  }

  return (
    <Stack h="100%">
      <Helmet>
        <title>{channel?.title}</title>
      </Helmet>
      <Group justify="space-between">
        <Group align="center">
          <Avatar src={channel?.thumbnail} style={{ borderRadius: 10 }} />
          <Title order={2}>{channel?.title}</Title>
          <SubscribeButton channelTitle={channel?.title} channelId={channel?.id} subscribed={channel?.subscribed} />
        </Group>
        <Button onClick={() => setDisplayFooter(!displayFooter)}>
          {displayFooter ? "Stop AutoPlay" : "Enable AutoPlay"}
        </Button>
      </Group>
      <Divider />
      <Box style={{ display: channel?.updating ? "contents" : "none" }}>
        <Center>
          <Flex align="center">
            <Loader />
            Retrieving latest videos...
          </Flex>
        </Center>
      </Box>
      <VideosView channelId={channel.id} enableAutoPlay={displayFooter} />
    </Stack>
  );
};

export default YoutubeChannel;
