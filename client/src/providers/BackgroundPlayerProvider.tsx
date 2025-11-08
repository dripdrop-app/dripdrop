import {
  createContext,
  MutableRefObject,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { skipToken } from "@reduxjs/toolkit/query";

import { GetYoutubeVideosApiYoutubeVideosListGetApiArg as YoutubeVideosParams } from "../api/generated/youtubeApi";
import { useFooter } from "./FooterProvider";
import { YoutubeVideoResponse as YoutubeVideo } from "../api/generated/youtubeApi";
import { useYoutubeVideosQuery } from "../api/youtube";
import ReactPlayer from "react-player";

interface BackgroundPlayerContextType {
  addVideoToQueue: ({ index, params }: { index: number; params: YoutubeVideosParams }) => void;
  advanceQueue: () => void;
  canAdvanceQueue: boolean;
  canRecedeQueue: boolean;
  currentVideo?: YoutubeVideo;
  recedeQueue: () => void;
  setShowPlayer: (show: boolean) => void;
  showPlayer: boolean;
  playerRef: MutableRefObject<ReactPlayer | null>;
}

const BackgroundPlayerContext = createContext<BackgroundPlayerContextType | undefined>(undefined);

export const BackgroundPlayerProvider = ({ children }: { children: ReactNode }) => {
  const { setDisplayFooter } = useFooter();

  const [currentVideoIndex, setCurrentVideoIndex] = useState(0);
  const [params, setParams] = useState<YoutubeVideosParams>();
  const [showPlayer, setShowPlayer] = useState(false);
  const playerRef = useRef<ReactPlayer | null>(null);

  const videosStatus = useYoutubeVideosQuery(params ?? skipToken);

  const addVideoToQueue = useCallback(({ index, params }: { index: number; params: YoutubeVideosParams }) => {
    setCurrentVideoIndex(index);
    setParams(params);
  }, []);

  const currentVideo = useMemo(
    () => videosStatus.currentData?.videos[currentVideoIndex],
    [currentVideoIndex, videosStatus.currentData?.videos]
  );

  const canAdvanceQueue = useMemo(() => {
    if (videosStatus.currentData && params) {
      return (
        currentVideoIndex + 1 < videosStatus.currentData?.videos.length ||
        params.page + 1 <= videosStatus.currentData.totalPages
      );
    }
    return false;
  }, [currentVideoIndex, params, videosStatus.currentData]);

  const advanceQueue = useCallback(() => {
    if (canAdvanceQueue && videosStatus.currentData && params) {
      if (currentVideoIndex + 1 < videosStatus.currentData?.videos.length) {
        setCurrentVideoIndex(currentVideoIndex + 1);
      } else if (params.page <= videosStatus.currentData.totalPages) {
        setParams({ ...params, page: params.page + 1 });
        setCurrentVideoIndex(0);
      }
    }
  }, [canAdvanceQueue, currentVideoIndex, params, videosStatus.currentData]);

  const canRecedeQueue = useMemo(() => {
    if (params) {
      return currentVideoIndex - 1 > 0 || params.page > 1;
    }
    return false;
  }, [currentVideoIndex, params]);

  const recedeQueue = useCallback(() => {
    if (canRecedeQueue && videosStatus.currentData && params) {
      if (currentVideoIndex - 1 > 0) {
        setCurrentVideoIndex(currentVideoIndex - 1);
      } else if (params.page > 1) {
        setParams({ ...params, page: params.page - 1 });
        setCurrentVideoIndex(params.perPage - 1);
      }
    }
  }, [canRecedeQueue, currentVideoIndex, params, videosStatus.currentData]);

  useEffect(() => {
    setDisplayFooter(showPlayer);
  }, [setDisplayFooter, showPlayer]);

  return (
    <BackgroundPlayerContext.Provider
      value={{
        addVideoToQueue,
        advanceQueue,
        canAdvanceQueue,
        canRecedeQueue,
        currentVideo,
        playerRef,
        recedeQueue,
        setShowPlayer,
        showPlayer,
      }}
    >
      {children}
    </BackgroundPlayerContext.Provider>
  );
};

export const useBackgroundPlayer = () => {
  const context = useContext(BackgroundPlayerContext);

  if (context === undefined) {
    throw new Error("useBackgroundPlayer must be used within a BackgroundPlayerProvider");
  }
  return context;
};
