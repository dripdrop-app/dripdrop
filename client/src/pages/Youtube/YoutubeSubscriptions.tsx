import { Center, Divider, Flex, Grid, Loader, Pagination, Stack, Title } from "@mantine/core";
import { useMemo } from "react";
import { Helmet } from "react-helmet-async";

import { useYoutubeSubscriptionsQuery } from "../../api/youtube";
import SubscriptionCard from "../../components/Youtube/SubscriptionCard";
import UpdateSubscriptionsModal from "../../components/Youtube/UpdateSubscriptionsModal";
import useSearchParams from "../../utils/useSearchParams";

const YoutubeSubscriptions = () => {
  const { params, setSearchParams } = useSearchParams({ perPage: 48, page: 1 });

  const subscriptionsStatus = useYoutubeSubscriptionsQuery(params);

  const { channels, totalPages } = useMemo(
    () => subscriptionsStatus.data ?? { channels: [], totalPages: 1 },
    [subscriptionsStatus.data]
  );

  return (
    <Stack>
      <Helmet>
        <title>Subscriptions</title>
      </Helmet>
      <Title order={2}>Subscriptions</Title>
      <Divider />
      <Stack pos="relative">
        {subscriptionsStatus.isLoading ? (
          <Center>
            <Loader />
          </Center>
        ) : (
          <>
            <Flex>
              <UpdateSubscriptionsModal />
            </Flex>
            <Grid type="container" breakpoints={{ xs: "400px", sm: "800px", md: "1000px", lg: "1200px", xl: "2000px" }}>
              {channels.map((subscription) => (
                <Grid.Col key={subscription.id} span={{ xs: 12, sm: 6, md: 4, lg: 3, xl: 2 }}>
                  <SubscriptionCard subscription={subscription} />
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
          </>
        )}
      </Stack>
    </Stack>
  );
};

export default YoutubeSubscriptions;
