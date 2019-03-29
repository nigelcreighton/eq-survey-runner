from structlog import get_logger

logger = get_logger()


class Answer:
    def __init__(self, answer_id, value, list_item_id=None):
        if answer_id is None or value is None:
            raise ValueError("Both 'answer_id' and 'value' must be set for Answer")

        self.answer_id = answer_id
        self.value = value
        self.list_item_id = list_item_id

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

        return self.matches(Answer(
            answer_dict.get('answer_id'),
            answer_dict.get('value'),
            answer_dict.get('list_item_id'),
        ))
