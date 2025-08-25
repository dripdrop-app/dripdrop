export const resolveAlbumFromTitle = (title: string) => {
  let album = "";

  if (!title) {
    return album;
  }

  const openPar = title.indexOf("(");
  const closePar = title.indexOf(")");
  const specialTitle = (openPar !== -1 || closePar !== -1) && openPar < closePar;

  const songTitle = specialTitle ? title.substring(0, openPar).trim() : title.trim();
  album = songTitle;
  const songTitleWords = songTitle.split(" ");

  if (songTitleWords.length > 2) {
    album = songTitleWords.map((word) => word.charAt(0)).join("");
  }
  if (specialTitle) {
    const specialWords = title.substring(openPar + 1, closePar).split(" ");
    album = `${album} - ${specialWords[specialWords.length - 1]}`;
  } else {
    album = album ? `${album} - Single` : "";
  }
  return album;
};

export const isBase64 = (url: string) => RegExp(/^data:(image\/.+)?;base64/).test(url);

export const isValidLink = (url: string) => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const isValidImage = (url: string) => {
  const isLink = isValidLink(url);
  return isLink && RegExp(/\.(jpg|jpeg|png)$/).test(url);
};

export const generateTime = (seconds: number) => {
  const formattedMinutes = Math.floor(seconds / 60)
    .toString()
    .padStart(1, "0");
  const formattedSeconds = Math.floor(seconds % 60)
    .toString()
    .padStart(2, "0");
  return `${formattedMinutes} : ${formattedSeconds}`;
};
