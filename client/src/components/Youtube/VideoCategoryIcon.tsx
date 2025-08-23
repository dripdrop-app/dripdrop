import { FunctionComponent } from "react";
import { IconBaseProps } from "react-icons";
import { BsFilm, BsMusicNoteBeamed, BsNewspaper, BsPersonVideo } from "react-icons/bs";
import { CgScreen } from "react-icons/cg";
import { FaBlog, FaDog, FaDragon, FaGlobe, FaHammer } from "react-icons/fa";
import { GiClassicalKnowledge, GiDramaMasks, GiFilmProjector } from "react-icons/gi";
import {
  MdAnimation,
  MdAttractions,
  MdDirectionsCar,
  MdFamilyRestroom,
  MdLocalMovies,
  MdMovie,
  MdMovieCreation,
  MdOutlineComputer,
  MdSchool,
  MdSports,
  MdSportsEsports,
  MdTheaterComedy,
  MdTravelExplore,
  MdVolunteerActivism,
} from "react-icons/md";
import { RiCompassDiscoverFill, RiVideoFill } from "react-icons/ri";
import { TbPumpkinScary } from "react-icons/tb";

const VideoCategories = {
  FILM_AND_ANIMATION: 1,
  AUTOS_AND_VEHICLES: 2,
  MUSIC: 10,
  PETS_AND_ANIMALS: 15,
  SPORTS: 17,
  SHORT_MOVIES: 18,
  TRAVEL_AND_EVENTS: 19,
  GAMING: 20,
  VIDEOBLOGGING: 21,
  PEOPLE_AND_BLOGS: 22,
  COMEDY: 23,
  ENTERTAINMENT: 24,
  NEWS_AND_POLITICS: 25,
  HOWTO_AND_STYLE: 26,
  EDUCATION: 27,
  SCIENCE_AND_TECHNOLOGY: 28,
  NONPROFITS_AND_ACTIVISM: 29,
  MOVIES: 30,
  ANIME_ANIMATION: 31,
  ACTION_ADVENTURE: 32,
  CLASSICS: 33,
  DOCUMENTARY: 35,
  DRAMA: 36,
  FAMILY: 37,
  FOREIGN: 38,
  HORROR: 39,
  SCIFI_FANTASY: 38,
  THRILLER: 41,
  SHORTS: 42,
  SHOWS: 43,
  TRAILERS: 44,
};

const VideoCategoryIconMap = {
  [VideoCategories.FILM_AND_ANIMATION]: BsFilm,
  [VideoCategories.AUTOS_AND_VEHICLES]: MdDirectionsCar,
  [VideoCategories.MUSIC]: BsMusicNoteBeamed,
  [VideoCategories.PETS_AND_ANIMALS]: FaDog,
  [VideoCategories.SPORTS]: MdSports,
  [VideoCategories.SHORT_MOVIES]: MdMovie,
  [VideoCategories.TRAVEL_AND_EVENTS]: MdTravelExplore,
  [VideoCategories.GAMING]: MdSportsEsports,
  [VideoCategories.VIDEOBLOGGING]: BsPersonVideo,
  [VideoCategories.PEOPLE_AND_BLOGS]: FaBlog,
  [VideoCategories.COMEDY]: MdTheaterComedy,
  [VideoCategories.ENTERTAINMENT]: MdAttractions,
  [VideoCategories.NEWS_AND_POLITICS]: BsNewspaper,
  [VideoCategories.HOWTO_AND_STYLE]: FaHammer,
  [VideoCategories.EDUCATION]: MdSchool,
  [VideoCategories.SCIENCE_AND_TECHNOLOGY]: MdOutlineComputer,
  [VideoCategories.NONPROFITS_AND_ACTIVISM]: MdVolunteerActivism,
  [VideoCategories.MOVIES]: MdLocalMovies,
  [VideoCategories.ANIME_ANIMATION]: MdAnimation,
  [VideoCategories.ACTION_ADVENTURE]: RiCompassDiscoverFill,
  [VideoCategories.CLASSICS]: GiClassicalKnowledge,
  [VideoCategories.DOCUMENTARY]: GiFilmProjector,
  [VideoCategories.DRAMA]: GiDramaMasks,
  [VideoCategories.FAMILY]: MdFamilyRestroom,
  [VideoCategories.FOREIGN]: FaGlobe,
  [VideoCategories.HORROR]: TbPumpkinScary,
  [VideoCategories.SCIFI_FANTASY]: FaDragon,
  [VideoCategories.THRILLER]: null,
  [VideoCategories.SHORTS]: RiVideoFill,
  [VideoCategories.SHOWS]: CgScreen,
  [VideoCategories.TRAILERS]: MdMovieCreation,
};

interface VideoCategoryIconProps extends IconBaseProps {
  categoryId: number;
}

const VideoCategoryIcon: FunctionComponent<VideoCategoryIconProps> = ({ categoryId, ...iconProps }) => {
  const Icon = VideoCategoryIconMap[categoryId];

  if (Icon) {
    return <Icon {...iconProps} />;
  }
  return null;
};

export default VideoCategoryIcon;
