MAX_NUMBER_OF_TAGS = 1000


class SearchMaterials:
    @staticmethod
    def tags(list1, list2):
        if list1 is None:
            list1 = []
        if list2 is None:
            list2 = []
        return (len(set(list1) & set(list2)) * MAX_NUMBER_OF_TAGS) - (len(list2) + len(list1))

    @staticmethod
    def validate_tags(
        input_tags: list[str], must_tags: list[str] = [], exclude_tags: list[str] = [], any_of_tags: list[str] = []
    ):
        # Check if all and_tags are in file_tags
        if input_tags is None:
            input_tags = []
        for item in must_tags:
            if item not in input_tags:
                return False

        # Check if any exclude_tags are in input_tags
        for item in exclude_tags:
            if item in input_tags:
                return False

        # Check if at least one of the or_tags is in input_tags
        if any_of_tags:
            return any(item in input_tags for item in any_of_tags)
        else:
            return True
