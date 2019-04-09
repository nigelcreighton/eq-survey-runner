from __future__ import annotations
from typing import List
import itertools
from collections import defaultdict
from jinja2 import escape
from structlog import get_logger
import simplejson as json

from app.data_model.answer import Answer

logger = get_logger()

class AnswerUnion:
    """ Representation of answers relating to a single answer_id.
    Either:
        - Represents a single answer
        - Represents multiple answers with the same answer id

    Multiple answers are stored as a map keyed on the list_item_id

    Assumes that an answer id will never have a list_item_id if it is not in a repeat
    i.e. You should never add a single answer, and then another answer with a list_item_id
    Assumes list_item_ids are unique per answer_id

    """

    def __init__(self):
        self._answers = None
        self._answer = None

    def __iter__(self):
        if self._answers:
            return iter(self._answers.values())
        elif self._answer:
            return iter((self._answer,))
        else:
            raise StopIteration

    def __len__(self):
        if self._answer:
            return 1
        else:
            return len(self._answers)

    def add_answer(self, answer: dict):
        if answer['list_item_id']:
            if not self._answers:
                self._answers = {}
            self._answers[answer['list_item_id']] = answer
        else:
            self._answer = answer

    def get_answer(self, list_item_id: str=None):
        """
        Returns an answer.
        If no list_item_id is provided then this is assumed to be a non-repeating answer
        """
        if list_item_id:
            return self._answers.get(list_item_id)
        else:
            return self._answer

    def get_all_answers(self) -> List[dict]:
        if self._answer:
            return [self._answer]
        else:
            return self._answers

    def get_values(self):
        if self._answer:
            return self._answer['value'],
        else:
            return (answer['value'] for answer in self._answers.values())

class AnswerStoreMap(defaultdict):
    def __iter__(self):
        return itertools.chain.from_iterable(union.get_all_answers() for union in self.values())

class AnswerStore:
    """
    An object that stores and updates a collection of answers, ready for serialisation
    via the Questionnaire Store.
    """

    def __init__(self, existing_answers=None):
        """ Instantiate an answer_store.
        Args:
            existing_answers: If a list of answer dictionaries is provided, this will be used to initialise the store.

        """
        if isinstance(existing_answers, list):
            self.answer_map = self._build_map(existing_answers or [])
        else:
            self.answer_map = existing_answers or AnswerStoreMap(AnswerUnion)

    def __iter__(self):
        return iter(self.answer_map.values())

    def __len__(self):
        return sum(len(answer_union) for answer_union in self.answer_map.values())

    def __eq__(self, other):
        return self.answer_map == other.answer_map

    def __getitem__(self, key):
        return self.answer_map[key]

    @staticmethod
    def _build_map(answers):
        """ Build the answer_store's internal representation of a set of answers"""
        answer_map = AnswerStoreMap(AnswerUnion)

        for answer in answers:
            answer_map[answer['answer_id']].add_answer(answer)

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

        answer_to_add = vars(answer).copy()
        self.answer_map[answer.answer_id].add_answer(answer_to_add)

    def get_answer(self, answer_id: str, list_item_id: str=None):
        """ Find an answer in the store if it exists
        """
        answer_union = self.answer_map[answer_id]
        answer = answer_union.get_answer(list_item_id=list_item_id)

        return answer

    def find(self, answer):
        """
        Returns the position of an answer if it exists
        :param answer: The answer to search for
        :return: The position the answer exists at, None if it doesn't exist
        """
        self._validate(answer)

        if answer['answer_id'] in self.answer_map:
            for index, existing in enumerate(self.answer_map[answer['answer_id']]):
                if answer.matches_dict(existing):
                    return index

        return None

    def count(self):
        """
        Count of the number of answers in the answer store.
        NB: can be combined with `filter` method to find count of an answer, e.g.:

            `answer_store.filter(answer_id=example_id).count()`

        :return: Number of answers in this store.
        """
        return len(self)

    def values(self):
        """
        Return a flat list of all values in the answer store.

        :return: Return a list of answer values
        """
        return list(itertools.chain.from_iterable(answer_union.get_values() for answer_union in self))

    def map_values_by_list_item_id(self):
        """
        Generate a map keyed on the list_item_id
        """
        output = defaultdict(list)

        for answer_union in self:
            for answer in answer_union:
                if answer['list_item_id']:
                    output[answer['list_item_id']].append(answer)

        return output

    def escaped(self):
        """
        Escape all answer values and return a new AnswerStore instance.

        :return: Return a new AnswerStore object with escaped answers for chaining
        """
        escaped = []
        for answer_union in self.answer_map.values():
            print(answer_union)
            for answer in answer_union:
                print(answer)
                answer = answer.copy()
                if isinstance(answer['value'], str):
                    answer['value'] = escape(answer['value'])
                escaped.append(answer)
        return self.__class__(existing_answers=escaped)

    def filter(self, answer_ids: List[str]=None, list_item_id: str=None):
        """
        Find all answers in the answer store for a given set of filter parameter matches.
        If no filter parameters are passed it returns a copy of the instance.
        :param answer_ids: The answer ids to filter results by
        :param list_item_id: A list_item_id to filter results by.
        :return: Return a new AnswerStore object with filtered answers for chaining
        """

        if answer_ids:
            answers = itertools.chain(self.answer_map[answer_id] for answer_id in answer_ids)
        else:
            answers = itertools.chain(answer_union for answer_union in self.answer_map.values())

        matches = [answer_union.get_answer(list_item_id) for answer_union in answers if answer_union.get_answer(list_item_id)]

        return self.__class__(existing_answers=matches)

    def clear(self):
        """
        Clears answers *in place*
        """
        self.answer_map.clear()

    def remove(self, answer_ids=None, list_item_id=None):
        """
        Removes answer(s) *in place* from the answer store.

        :param answer_ids: The answer ids to remove
        """
        for answer in self.filter(answer_ids, list_item_id=list_item_id):
            self.answer_map[answer['answer_id']].remove(answer)

    def remove_answer(self, answer):
        """
        Removes answer *in place* from the answer store.

        :param answer: The answer to remove
        """

        if answer['answer_id'] in self.answer_map:
            del self.answer_map[answer['answer_id']]

    def get_hash(self):
        """
        Gets unique hash from answers contained within this AnswerStore

        :return: Return a unique hash value
        """
        return hash(json.dumps(self.answer_map, sort_keys=True))
