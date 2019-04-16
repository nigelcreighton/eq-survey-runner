from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict

from structlog import get_logger

logger = get_logger()


@dataclass
class Answer:
    answer_id: str
    value: str
    list_item_id: str = field(default=None)

    @classmethod
    def from_dict(cls, answer_dict: Dict) -> Answer:
        return cls(answer_id=answer_dict['answer_id'],
               value=answer_dict['value'],
               list_item_id=answer_dict.get('list_item_id'))

    def to_dict(self) -> Dict:
        return asdict(self)

    def matches(self, answer: Answer):
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
