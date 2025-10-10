import logging
import random

import db.session
from db.language import Language
from db.hashtag import Hashtag

from utils.search_materials import SearchMaterials
from utils.log_wrapper import log_inputs

logger = logging.getLogger(__name__)


class HashtagFactory:
    def __init__(self) -> None:
        self._db_session = db.session.make()

    @log_inputs
    def select(
        self,
        number: int,
        language: Language = None,
        must_tags: list[str] = [],
        exclude_tags: list[str] = [],
        any_of_tags: list[str] = [],
    ):
        number = max(1, number)
        if language == None:
            language = self._db_session.query(Language).filter(Language.name == "English").all()[0]
        hashtags = self._db_session.query(Hashtag).filter(Hashtag.language_id == language.id).all()

        temp = []
        for hashtag in hashtags:
            if SearchMaterials.validate_tags(hashtag.keywords, must_tags, exclude_tags, any_of_tags):
                temp.append(hashtag)

        if not temp:
            logger.warning("failed to find any hashtag")
            return []
        
        if len(temp) < number:
            logger.warning(f"failed to find enough hashtags")

        good_tags = must_tags + any_of_tags

        max_element = max(temp, key=lambda x: SearchMaterials.tags(x.keywords, good_tags))
        max_value = SearchMaterials.tags(max_element.keywords, good_tags)
        filtered_objects = filter(lambda x: (SearchMaterials.tags(x.keywords, good_tags) == max_value), temp)
        obj_list = list(filtered_objects)

        random.shuffle(obj_list)
        # # output = sorted(temp,key=lambda x: SearchMaterials.tags(x.keywords, good_tags),reverse=True)
        return obj_list[0:number]


if __name__ == "__main__":
    a = HashtagFactory()
    t = a.select(5, any_of_tags=["cargo"])
    t = []
    print(t[:5])
