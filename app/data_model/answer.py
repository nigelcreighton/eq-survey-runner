from structlog import get_logger

logger = get_logger()


class Answer:
    def __init__(self, answer_id, value, list_item_id=None):
        if answer_id is None or value is None:
            raise ValueError("Both 'answer_id' and 'value' must be set for Answer")

        self.answer_id = answer_id
        self.value = value
        self.list_item_id = list_item_id

    def copy(self):
        return Answer(self.answer_id, self.value, self.list_item_id)

    @staticmethod
    def from_dict(input: dict):
        return Answer(
            input.get('answer_id'),
            input.get('value'),
            input.get('list_item_id'),
        )

    def matches(self, answer):
        """
        Check to see if two answers match.

        :param answer: An answer to compare
        :return: True if both answers match, otherwise False.
        """
        return self.answer_id == answer.answer_id and self.list_item_id == answer.list_item_id

    def matches_dict(self, answer_dict):
        """
        Check to see if a dict describes an answer the same as this object.

        :param answer_dict: A dictionary representation of the answer.
        :return: True if both answers match, otherwise False.
        """

        return self.matches(Answer.from_dict(answer_dict))
