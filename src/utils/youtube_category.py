from enum import Enum


class YTCategory(Enum):
    FILM_AND_ANIMATION = 1
    AUTOS_AND_VEHICLES = 2
    MUSIC = 10
    PETS_AND_ANIMALS = 15
    SPORTS = 17
    SHORT_MOVIES = 18
    TRAVEL_AND_EVENTS = 19
    GAMING = 20
    VIDEOBLOGGING = 21
    PEOPLE_AND_BLOGS = 22
    COMEDY = 23
    ENTERTAINMENT = 24
    NEWS_AND_POLITICS = 25
    HOWTO_AND_STYLE = 26
    EDUCATION = 27
    SCIENCE_AND_TECHNOLOGY = 28
    NONPROFITS_AND_ACTIVISM = 29
    MOVIES = 30
    ANIME_ACTION = 31
    CLASSICS = 33
    DOCUMENTARY = 35
    DRAMA = 36
    FAMILY = 37
    FOREIGN = 38
    HORROR = 39
    SCI_FI_FANTASY = 40
    THRILLER = 41
    SHORTS = 42
    SHOWS = 43
    TRAILERS = 44


class YoutubeCategory:
    @staticmethod
    def guess_category(tags: list[str] = []):
        return YTCategory.ENTERTAINMENT.value
