type MusicFormState =
  | {
      isFile: true;
      videoUrl: string;
      file: File;
      artworkUrl: string;
      resolvedArtworkUrl: string;
      title: string;
      artist: string;
      album: string;
      grouping: string;
    }
  | {
      isFile: false;
      videoUrl: string;
      file: null;
      artworkUrl: string;
      resolvedArtworkUrl: string;
      title: string;
      artist: string;
      album: string;
      grouping: string;
    };
