import { Anchor, Button, Card, Flex, Image, Stack, Table } from "@mantine/core";
import { FunctionComponent } from "react";
import { MdDelete, MdDownload, MdError } from "react-icons/md";

import { useDeleteJobMutation } from "../../api/music";
import { MusicJobResponse as MusicJob } from "../../api/generated/musicApi";

const MusicJobCard: FunctionComponent<MusicJob> = (props) => {
  // const createdAt = new Date(props.createdAt).toLocaleDateString();

  const [removeMusicJob, removeMusicJobStatus] = useDeleteJobMutation();

  const downloadFile = async () => {
    if (props.downloadUrl && props.downloadFilename) {
      const response = await fetch(props.downloadUrl, { mode: "no-cors" });
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = props.downloadFilename.substring(props.downloadFilename.lastIndexOf("/") + 1);
      a.click();
    }
  };

  return (
    <Card>
      <Card.Section>
        <Image
          src={props.artworkUrl || "https://ewr1.vultrobjects.com/dripdrop-prod/assets/blank_image.jpeg"}
          alt="Artwork"
          height={150}
        />
      </Card.Section>
      <Stack>
        <Table variant="vertical" withColumnBorders withRowBorders>
          <Table.Tbody>
            <Table.Tr>
              <Table.Th>Video URL</Table.Th>
              <Table.Td>
                {props.videoUrl ? (
                  <Anchor href={props.videoUrl} target="_blank" rel="noopener noreferrer">
                    {props.videoUrl}
                  </Anchor>
                ) : (
                  props.videoUrl
                )}
              </Table.Td>
            </Table.Tr>
            <Table.Tr>
              <Table.Th>Filename</Table.Th>
              <Table.Td>
                {props.filenameUrl ? (
                  <Anchor href={props.filenameUrl} target="_blank" rel="noopener noreferrer">
                    {props.originalFilename}
                  </Anchor>
                ) : (
                  props.originalFilename
                )}
              </Table.Td>
            </Table.Tr>
            <Table.Tr>
              <Table.Th>Artwork URL</Table.Th>
              <Table.Td>
                {props.artworkUrl ? (
                  <Anchor href={props.artworkUrl} target="_blank" rel="noopener noreferrer">
                    {props.artworkUrl}
                  </Anchor>
                ) : (
                  props.artworkUrl
                )}
              </Table.Td>
            </Table.Tr>
            <Table.Tr>
              <Table.Th>Title</Table.Th>
              <Table.Td>{props.title}</Table.Td>
            </Table.Tr>
            <Table.Tr>
              <Table.Th>Artist</Table.Th>
              <Table.Td>{props.artist}</Table.Td>
            </Table.Tr>
            <Table.Tr>
              <Table.Th>Album</Table.Th>
              <Table.Td>{props.album}</Table.Td>
            </Table.Tr>
            <Table.Tr>
              <Table.Th>Grouping</Table.Th>
              <Table.Td>{props.grouping}</Table.Td>
            </Table.Tr>
            {/* <Table.Tr>
              <Table.Th>Created At</Table.Th>
              <Table.Td>{createdAt}</Table.Td>
            </Table.Tr> */}
          </Table.Tbody>
        </Table>
        <Flex justify="center">
          <Button display={!props.completed && !props.failed ? "initial" : "none"} loading>
            Loading
          </Button>
          <Button display={props.failed ? "initial" : "none"} color="red" leftSection={<MdError />}>
            Failed
          </Button>
          <Button
            display={props.completed ? "initial" : "none"}
            color="green"
            leftSection={<MdDownload />}
            onClick={downloadFile}
          >
            Download
          </Button>
          <Button
            color="red"
            leftSection={<MdDelete />}
            loading={removeMusicJobStatus.isLoading}
            onClick={() => removeMusicJob(props.id)}
          >
            Delete
          </Button>
        </Flex>
      </Stack>
    </Card>
  );
};

export default MusicJobCard;
