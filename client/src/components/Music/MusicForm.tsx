import {
  Box,
  Button,
  Container,
  Divider,
  FileInput,
  Flex,
  Image,
  Loader,
  Stack,
  Switch,
  TextInput,
  Title,
} from "@mantine/core";
import { useDebouncedValue } from "@mantine/hooks";
import { showNotification } from "@mantine/notifications";
import { useCallback, useEffect, useMemo } from "react";
import { Controller, useForm, useWatch } from "react-hook-form";

import { useLazyArtworkQuery, useCreateJobMutation, useLazyGroupingQuery, useTagsMutation } from "../../api/music";
import { isBase64, isValidImage, isValidLink, resolveAlbumFromTitle } from "../../utils/helpers";
import { CreateMusicJob } from "../../api/generated/musicApi";

const MusicForm = () => {
  const { reset, handleSubmit, control, trigger, setValue } = useForm<MusicFormState>({
    reValidateMode: "onBlur",
  });
  const watchFields = useWatch({ control });

  const [debouncedArtworkUrl] = useDebouncedValue(watchFields.artworkUrl, 500);
  const [debouncedVideoUrl] = useDebouncedValue(watchFields.videoUrl, 500);

  const [createMusicJob, createJobStatus] = useCreateJobMutation();
  const [getArtwork, getArtworkStatus] = useLazyArtworkQuery();
  const [getTags, getTagsStatus] = useTagsMutation();
  const [getGrouping, getGroupingStatus] = useLazyGroupingQuery();

  const artworkLoading = useMemo(
    () => getArtworkStatus.isLoading || getArtworkStatus.isFetching,
    [getArtworkStatus.isFetching, getArtworkStatus.isLoading]
  );

  const groupingLoading = useMemo(
    () => getGroupingStatus.isLoading || getGroupingStatus.isFetching,
    [getGroupingStatus.isFetching, getGroupingStatus.isLoading]
  );

  const onSubmit = useCallback(
    async (data: MusicFormState) => {
      const successNotification = () =>
        showNotification({
          title: "Success",
          message: "Job Created Successfully",
          color: "green",
        });
      const errorNotification = () =>
        showNotification({
          title: "Error",
          message: "Job Failed to Start",
          color: "red",
        });

      const formData = new FormData();
      if (data.file) {
        formData.append("file", data.file);
      } else {
        formData.append("video_url", data.videoUrl);
      }
      if (data.resolvedArtworkUrl) {
        formData.append("artwork_url", data.resolvedArtworkUrl);
      }
      formData.append("title", data.title);
      formData.append("artist", data.artist);
      formData.append("album", data.album);
      if (data.grouping) {
        formData.append("grouping", data.grouping);
      }
      const status = await createMusicJob(formData as unknown as CreateMusicJob);
      if (!status.error) {
        reset();
        successNotification();
      } else {
        errorNotification();
      }
    },
    [createMusicJob, reset]
  );

  const resolveArtworkUrl = useCallback(
    async (artworkUrl: string) => {
      if (artworkUrl) {
        if (isBase64(artworkUrl) || isValidImage(artworkUrl)) {
          return setValue("resolvedArtworkUrl", artworkUrl);
        } else if (isValidLink(artworkUrl)) {
          const status = await getArtwork(artworkUrl);
          if (status.isSuccess) {
            const { resolvedArtworkUrl } = status.data;
            return setValue("resolvedArtworkUrl", resolvedArtworkUrl);
          }
        }
      }
      return setValue("resolvedArtworkUrl", "");
    },
    [getArtwork, setValue]
  );

  useEffect(() => {
    resolveArtworkUrl(debouncedArtworkUrl || "");
  }, [debouncedArtworkUrl, resolveArtworkUrl]);

  const getFileTags = useCallback(
    async (file: File) => {
      const status = await getTags({ file });
      if (!status.error) {
        const { title, artist, album, grouping, artworkUrl } = status.data;
        if (title) {
          setValue("title", title);
        }
        if (artist) {
          setValue("artist", artist);
        }
        if (album) {
          setValue("album", album);
        }
        if (grouping) {
          setValue("grouping", grouping);
        }
        if (artworkUrl) {
          setValue("artworkUrl", artworkUrl);
        }
        trigger();
      }
    },
    [getTags, setValue, trigger]
  );

  useEffect(() => {
    if (watchFields.file) {
      getFileTags(watchFields.file);
    }
  }, [getFileTags, watchFields.file]);

  useEffect(() => {
    if (watchFields.title) {
      setValue("album", resolveAlbumFromTitle(watchFields.title));
    }
  }, [setValue, watchFields.title]);

  const resolveGrouping = useCallback(
    async (videoUrl: string) => {
      if (videoUrl) {
        if (isValidLink(videoUrl)) {
          const status = await getGrouping(videoUrl);
          if (status.isSuccess) {
            const { grouping } = status.data;
            setValue("grouping", grouping);
          }
        }
      }
    },
    [getGrouping, setValue]
  );

  useEffect(() => {
    resolveGrouping(debouncedVideoUrl || "");
  }, [debouncedVideoUrl, resolveGrouping]);

  return (
    <Stack>
      <Title order={2}>Music Downloader / Converter</Title>
      <Divider />
      <Container fluid w={{ base: "100%", sm: 1500 }}>
        <Box component="form" onSubmit={handleSubmit(onSubmit)}>
          <Stack>
            <Flex align="center">
              <Controller
                name="videoUrl"
                control={control}
                defaultValue={""}
                rules={{
                  required: !watchFields.isFile,
                  validate: (v) => (!watchFields.isFile ? isValidLink(v) : true),
                }}
                render={({ field, fieldState }) => {
                  let error = "";
                  if (fieldState.error?.type === "validate") {
                    error = "Invalid Link";
                  } else if (fieldState.error?.type === "required") {
                    error = "Required";
                  }
                  return (
                    <TextInput
                      {...field}
                      w="100%"
                      error={error}
                      label="Video URL"
                      placeholder="Enter Video URL"
                      disabled={watchFields.isFile}
                      required={!watchFields.isFile}
                    />
                  );
                }}
              />
              <Controller
                name="isFile"
                control={control}
                defaultValue={false}
                render={({ field }) => <Switch {...field} value="" checked={field.value} />}
              />
              <Controller
                name="file"
                control={control}
                defaultValue={null}
                rules={{ required: watchFields.isFile }}
                render={({ field, fieldState }) => (
                  <FileInput
                    {...field}
                    w="100%"
                    error={fieldState.error?.type === "required" ? "Required" : ""}
                    label="Filename"
                    placeholder="Select File"
                    required={watchFields.isFile}
                    disabled={!watchFields.isFile}
                    accept="audio/mpeg,audio/wav"
                  />
                )}
              />
            </Flex>
            <Flex align="center">
              <Box w="100%">
                <Image
                  alt="blank"
                  src={
                    watchFields.resolvedArtworkUrl ||
                    "https://dripdrop-prod.nyc3.cdn.digitaloceanspaces.com/assets/blank_image.jpeg"
                  }
                />
              </Box>
              <Stack justify="center" gap="md" w="100%">
                <Controller
                  name="artworkUrl"
                  control={control}
                  defaultValue={""}
                  render={({ field, fieldState }) => (
                    <TextInput
                      {...field}
                      error={fieldState.error?.message}
                      label="Artwork URL"
                      placeholder="Enter Artwork URL"
                      disabled={getTagsStatus.isLoading}
                    />
                  )}
                />
                <Controller
                  name="resolvedArtworkUrl"
                  control={control}
                  defaultValue={""}
                  render={({ field, fieldState }) => (
                    <TextInput
                      {...field}
                      error={fieldState.error?.message}
                      label="Resolved Artwork URL"
                      disabled
                      rightSection={artworkLoading || getTagsStatus.isLoading ? <Loader size="xs" /> : null}
                    />
                  )}
                />
                <Button onClick={() => setValue("artworkUrl", "")}>Clear</Button>
              </Stack>
            </Flex>
            <Flex>
              <Controller
                name="title"
                control={control}
                defaultValue={""}
                rules={{ required: true }}
                render={({ field, fieldState }) => (
                  <TextInput
                    {...field}
                    w="100%"
                    error={fieldState.error?.type === "required" ? "Required" : ""}
                    label="Title"
                    placeholder="Enter Title"
                    withAsterisk
                    disabled={getTagsStatus.isLoading}
                    rightSection={getTagsStatus.isLoading ? <Loader size="xs" /> : null}
                  />
                )}
              />
              <Controller
                name="artist"
                control={control}
                defaultValue={""}
                rules={{ required: true }}
                render={({ field, fieldState }) => (
                  <TextInput
                    {...field}
                    w="100%"
                    error={fieldState.error?.type === "required" ? "Required" : ""}
                    label="Artist"
                    placeholder="Enter Artist"
                    withAsterisk
                    disabled={getTagsStatus.isLoading}
                    rightSection={getTagsStatus.isLoading ? <Loader size="xs" /> : null}
                  />
                )}
              />
              <Controller
                name="album"
                control={control}
                defaultValue={""}
                rules={{ required: true }}
                render={({ field, fieldState }) => (
                  <TextInput
                    {...field}
                    w="100%"
                    error={fieldState.error?.type === "required" ? "Required" : ""}
                    label="Album"
                    placeholder="Enter Album"
                    withAsterisk
                    disabled={getTagsStatus.isLoading}
                    rightSection={getTagsStatus.isLoading ? <Loader size="xs" /> : null}
                  />
                )}
              />
              <Controller
                name="grouping"
                control={control}
                defaultValue={""}
                render={({ field }) => (
                  <TextInput
                    {...field}
                    w="100%"
                    label="Grouping"
                    placeholder="Enter Grouping"
                    disabled={getTagsStatus.isLoading || groupingLoading}
                    rightSection={getTagsStatus.isLoading || groupingLoading ? <Loader size="xs" /> : null}
                  />
                )}
              />
            </Flex>
            <Flex justify="center">
              <Button
                disabled={artworkLoading || getTagsStatus.isLoading || groupingLoading}
                loading={createJobStatus.isLoading}
                type="submit"
              >
                Download / Convert
              </Button>
              <Button onClick={() => reset()}>Reset</Button>
            </Flex>
          </Stack>
        </Box>
      </Container>
    </Stack>
  );
};

export default MusicForm;
