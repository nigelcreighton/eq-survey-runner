from __future__ import annotations
from typing import List

from jinja2 import escape
from structlog import get_logger

from app.data_model.answer import Answer
from app.libs.utils import make_hash

logger = get_logger()


class AnswerStore:
    """
    An object that stores and updates a collection of answers, ready for serialisation
    via the Questionnaire Store.

    Internally stores answers in the form:

    {
        (<answer_id>, <list_item_id>): {
            Answer
        }
    }
    """

    def __init__(self, existing_answers=None):
        """ Instantiate an answer_store.
        Args:
            existing_answers: If a list of answer dictionaries is provided, this will be used to initialise the store.

        """
        if isinstance(existing_answers, list):
            self.answer_map = self._build_map(existing_answers or [])
        else:
            self.answer_map = existing_answers or {}

    def __iter__(self):
        return iter(self.answer_map.values())

    def __len__(self):
        return len(self.answer_map)

    def __eq__(self, other):
        return self.answer_map == other.answer_map

    def __getitem__(self, key):
        return self.answer_map[key]

    @staticmethod
    def _build_map(answers):
        """ Builds the answer_store's data structure from a list of Answer dictionaries"""
        answer_map = {}

        for answer in answers:
            list_item_id = answer.get('list_item_id')
            answer_map[answer['answer_id'], list_item_id] = answer

        return answer_map

    @staticmethod
    def _validate(answer):
        if not isinstance(answer, Answer):
            raise TypeError('Method only supports Answer argument type')

    def copy(self) -> AnswerStore:
        """
        Create a new instance of answer_store with the same values.
        """
        return self.__class__(self.answer_map.copy())

    def add_or_update(self, answer: Answer):
        """
        Add a new answer into the answer store, or update if it exists.
        """
        self._validate(answer)

        self.answer_map[(answer.answer_id, answer.list_item_id)] = vars(answer).copy()

    def values(self) -> List[str]:
        """
        Return a flat list of all answer values in the answer store.
        """
        return [answer['value'] for answer in self]

    def escaped(self) -> AnswerStore:
        """
        Escape all answer values and return a new AnswerStore instance.

        Returns:
            A new AnswerStore object with escaped answers for chaining
        """
        escaped = []
        for answer in self:
            answer = answer.copy()
            if isinstance(answer['value'], str):
                answer['value'] = escape(answer['value'])
            escaped.append(answer)
        return self.__class__(existing_answers=escaped)

    def get_answer(self, answer_id: str, list_item_id: str = None) -> Answer:
        """ Get a single answer from the store

        Args:
            answer_id: The answer id to find
            list_item_id: If not provided (None), will only match an answer with no list_item_id

        Returns:
            A single Answer or None if it doesn't exist
        """
        return self.answer_map.get((answer_id, list_item_id))

    def get_answers_by_answer_id(self, answer_ids: List[str], list_item_id: str = None) -> List[Answer]:
        """ Get multiple answers from the store using the answer_id

        Args:
            answer_ids: list of answer ids to find
            list_item_id: list item id to match
                          If not provided (None), will only match an answer with no list_item_id

        Returns:
            A list of Answer objects
        """
        output = []
        for answer_id in answer_ids:
            answer = self.answer_map.get((answer_id, list_item_id))
            if answer:
                output.append(answer)

        return output

    def clear(self):
        """
        Clears answers *in place*
        """
        self.answer_map.clear()

    def remove_answer(self, answer_id: str, list_item_id: str = None):
        """
        Removes answer *in place* from the answer store.
        """

        if self.answer_map.get((answer_id, list_item_id)):
            del self.answer_map[(answer_id, list_item_id)]

    def remove_all_answers_for_list_item_id(self, list_item_id: str):
        """Remove all answers associated with a particular list_item_id
        This method iterates through the entire list of answers. Not efficient.
        """
        trimmed_answers = self.answer_map.copy()

        for answer in self:
            if answer['list_item_id'] == list_item_id:
                del trimmed_answers[(answer['answer_id'], answer['list_item_id'])]

        self.answer_map = trimmed_answers

    def get_hash(self):
        """
        Gets unique hash from answers contained within this AnswerStore

        :return: Return a unique hash value
        """

        return make_hash(self.answer_map)
