import { Center, Divider, Grid, Loader, Pagination, Stack, Title } from "@mantine/core";
import { useMemo, useState } from "react";

import { useListenMusicJobsQuery, useMusicJobsQuery } from "../../api/music";
import { GetJobsApiMusicJobsListGetApiArg } from "../../api/generated/musicApi";
import MusicJobCard from "./MusicJobCard";

const MusicJobList = () => {
  const [args, setArgs] = useState<GetJobsApiMusicJobsListGetApiArg>({
    page: 1,
    perPage: 5,
  });

  const musicJobsStatus = useMusicJobsQuery(args);
  useListenMusicJobsQuery();

  const { jobs, totalPages } = useMemo(() => {
    if (musicJobsStatus.isSuccess && musicJobsStatus.currentData) {
      return musicJobsStatus.currentData;
    } else if (musicJobsStatus.data) {
      return musicJobsStatus.data;
    }
    return { jobs: [], totalPages: 1 };
  }, [musicJobsStatus.currentData, musicJobsStatus.data, musicJobsStatus.isSuccess]);

  return (
    <Stack>
      <Title order={3}>Jobs</Title>
      <Divider />
      <Center style={{ ...(!musicJobsStatus.isLoading && { display: "none" }) }}>
        <Loader />
      </Center>
      <Stack style={{ ...(musicJobsStatus.isLoading && { display: "none" }) }}>
        <Center style={{ ...(jobs.length !== 0 && { display: "none" }) }}>No Music Jobs</Center>
        <Stack>
          <Grid
            justify="center"
            type="container"
            breakpoints={{ xs: "400px", sm: "800px", md: "1000px", lg: "1200px", xl: "2000px" }}
          >
            {jobs.map((musicJob) => (
              <Grid.Col key={musicJob.id} span={{ xs: 12, sm: 6, md: 4, lg: 3, xl: 2 }}>
                <MusicJobCard {...musicJob} />
              </Grid.Col>
            ))}
          </Grid>
          <Center>
            <Pagination
              value={args.page}
              total={totalPages}
              onChange={(newPage) => setArgs((prevState) => ({ ...prevState, page: newPage }))}
            />
          </Center>
        </Stack>
      </Stack>
    </Stack>
  );
};

export default MusicJobList;
