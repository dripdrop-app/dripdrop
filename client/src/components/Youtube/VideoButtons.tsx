import { ActionIcon, Tooltip } from "@mantine/core";
import { FunctionComponent, useMemo } from "react";
import { MdAddToQueue, MdPlayArrow, MdRemoveFromQueue, MdThumbUp, MdVisibility } from "react-icons/md";

import { YoutubeVideoResponse as YoutubeVideo } from "../../api/generated/youtubeApi";
import {
  useAddYoutubeVideoLikeMutation,
  useAddYoutubeVideoQueueMutation,
  useDeleteYoutubeVideoLikeMutation,
  useDeleteYoutubeVideoQueueMutation,
} from "../../api/youtube";

interface VideoButtonsProps {
  video: YoutubeVideo;
}

export const VideoLikeButton: FunctionComponent<VideoButtonsProps> = ({ video }) => {
  const [likeVideo, likeVideoStatus] = useAddYoutubeVideoLikeMutation();
  const [unLikeVideo, unLikeVideoStatus] = useDeleteYoutubeVideoLikeMutation();

  const loading = useMemo(
    () => likeVideoStatus.isLoading || unLikeVideoStatus.isLoading,
    [likeVideoStatus.isLoading, unLikeVideoStatus.isLoading]
  );

  const likedDate = video.liked ? new Date(video.liked).toLocaleDateString() : "";

  return (
    <Tooltip label={video.liked ? `Liked on ${likedDate}` : "Like"}>
      <ActionIcon
        className="hover-brighten"
        variant="transparent"
        color="white"
        onClick={() => (video.liked ? unLikeVideo(video.id) : likeVideo(video.id))}
        loading={loading}
      >
        <MdThumbUp size={25} color={video.liked ? "green" : ""} />
      </ActionIcon>
    </Tooltip>
  );
};

export const VideoQueueButton: FunctionComponent<VideoButtonsProps> = ({ video }) => {
  const [queueVideo, queueVideoStatus] = useAddYoutubeVideoQueueMutation();
  const [unQueueVideo, unQueueVideoStatus] = useDeleteYoutubeVideoQueueMutation();

  const loading = useMemo(
    () => queueVideoStatus.isLoading || unQueueVideoStatus.isLoading,
    [queueVideoStatus.isLoading, unQueueVideoStatus.isLoading]
  );

  return (
    <Tooltip label={video.queued ? "Unqueue" : "Queue"}>
      <ActionIcon
        className="hover-brighten"
        variant="transparent"
        color="white"
        loading={loading}
        onClick={() => (video.queued ? unQueueVideo(video.id) : queueVideo(video.id))}
      >
        {video.queued ? <MdRemoveFromQueue size={25} color="red" /> : <MdAddToQueue size={25} />}
      </ActionIcon>
    </Tooltip>
  );
};

export const VideoWatchButton: FunctionComponent<VideoButtonsProps> = ({ video }) => {
  const watchedDate = video.watched ? new Date(video.watched).toLocaleDateString() : "";

  if (!video.watched) {
    return null;
  }

  return (
    <Tooltip label={`Watched on ${watchedDate}`}>
      <ActionIcon className="hover-brighten" variant="transparent" color="white">
        <MdVisibility size={25} />
      </ActionIcon>
    </Tooltip>
  );
};

interface VideoPlayInBackgroundButtonProps {
  onPlayVideoInBackground: () => void;
}

export const VideoPlayInBackgroundButton: FunctionComponent<VideoPlayInBackgroundButtonProps> = ({
  onPlayVideoInBackground,
}) => {
  return (
    <Tooltip label={`Play in Background`}>
      <ActionIcon
        className="hover-brighten"
        variant="transparent"
        color="white"
        onClick={() => onPlayVideoInBackground()}
      >
        <MdPlayArrow size={60} />
      </ActionIcon>
    </Tooltip>
  );
};
