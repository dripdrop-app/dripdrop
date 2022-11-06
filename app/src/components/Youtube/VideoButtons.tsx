import { useMemo, useState } from 'react';
import { CircularProgress, IconButton, Tooltip } from '@mui/material';
import { AddToQueue, RemoveFromQueue, ThumbUp, Visibility } from '@mui/icons-material';
import {
	useAddYoutubeVideoLikeMutation,
	useAddYoutubeVideoQueueMutation,
	useDeleteYoutubeVideoLikeMutation,
	useDeleteYoutubeVideoQueueMutation,
} from '../../api/youtube';

interface VideoButtonsProps {
	video: YoutubeVideo;
}

export const VideoLikeButton = (props: VideoButtonsProps) => {
	const { video } = props;

	const [likeVideo, likeVideoStatus] = useAddYoutubeVideoLikeMutation();
	const [unLikeVideo, unLikeVideoStatus] = useDeleteYoutubeVideoLikeMutation();

	const loading = useMemo(
		() => likeVideoStatus.isLoading || unLikeVideoStatus.isLoading,
		[likeVideoStatus.isLoading, unLikeVideoStatus.isLoading]
	);

	return useMemo(
		() => (
			<IconButton
				disabled={loading}
				onClick={() => (video.liked ? unLikeVideo(video.id) : likeVideo(video.id))}
				color={video.liked ? 'success' : 'default'}
			>
				<CircularProgress sx={{ display: loading ? 'block' : 'none' }} />
				<ThumbUp sx={{ display: !loading ? 'block' : 'none' }} />
			</IconButton>
		),
		[likeVideo, loading, unLikeVideo, video.id, video.liked]
	);
};

export const VideoQueueButton = (props: VideoButtonsProps) => {
	const { video } = props;

	const [queueVideo, queueVideoStatus] = useAddYoutubeVideoQueueMutation();
	const [unQueueVideo, unQueueVideoStatus] = useDeleteYoutubeVideoQueueMutation();

	const loading = useMemo(
		() => queueVideoStatus.isLoading || unQueueVideoStatus.isLoading,
		[queueVideoStatus.isLoading, unQueueVideoStatus.isLoading]
	);

	return useMemo(
		() => (
			<IconButton
				disabled={loading}
				onClick={() => (video.queued ? unQueueVideo(video.id) : queueVideo(video.id))}
				color={video.queued ? 'error' : 'inherit'}
			>
				<CircularProgress sx={{ display: loading ? 'block' : 'none' }} />
				<AddToQueue sx={{ display: video.queued && !loading ? 'none' : 'block' }} />
				<RemoveFromQueue color="error" sx={{ display: video.queued && !loading ? 'block' : 'none' }} />
			</IconButton>
		),
		[loading, queueVideo, unQueueVideo, video.id, video.queued]
	);
};

export const VideoWatchButton = (props: VideoButtonsProps) => {
	const { video } = props;
	const [open, setOpen] = useState(false);

	const watchedDate = video.watched ? new Date(video.watched).toLocaleDateString() : '';

	return useMemo(
		() => (
			<Tooltip
				open={open}
				onOpen={() => setOpen(true)}
				onClose={() => setOpen(false)}
				title={`Watched on ${watchedDate}`}
			>
				<IconButton onClick={() => setOpen(true)}>
					<Visibility sx={{ display: video.watched ? 'block' : 'none' }} />
				</IconButton>
			</Tooltip>
		),
		[open, video.watched, watchedDate]
	);
};
