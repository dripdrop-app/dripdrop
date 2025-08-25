import { Stack } from "@mantine/core";
import { Helmet } from "react-helmet-async";

import MusicForm from "../../components/Music/MusicForm";
import MusicJobList from "../../components/Music/MusicJobList";

const MusicDownloader = () => {
  return (
    <Stack gap={10}>
      <Helmet>
        <title>Music Downloader</title>
      </Helmet>
      <MusicForm />
      <MusicJobList />
    </Stack>
  );
};

export default MusicDownloader;
