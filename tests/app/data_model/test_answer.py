import unittest
from app.data_model.answer_store import Answer

class TestAnswer(unittest.TestCase):
    def test_matches_answer(self):
        answer_1 = Answer(
            answer_id='4',
            list_item_id='dj892j',
            value=25,
        )
        answer_2 = Answer(
            answer_id='4',
            list_item_id='dj892j',
            value=25,
        )

        self.assertEqual(answer_1.matches(answer_2), True)

    def test_matches_answer_dict(self):
        answer_1 = Answer(
            answer_id='4',
            list_item_id='dj892j',
            value=25,
        )
        answer_2 = {
            'answer_id': '4',
            'list_item_id': 'dj892j',
            'value': 25,
        }

        self.assertEqual(answer_1.matches_dict(answer_2), True)

    def test_non_matching_answer(self):
        answer_1 = Answer(
            answer_id='4',
            list_item_id='iw892j',
            value=25,
        )
        answer_2 = Answer(
            answer_id='4',
            list_item_id='dj892j',
            value=65,
        )

        self.assertEqual(answer_1.matches(answer_2), False)

    def test_matches_answer_simple(self):
        answer_1 = Answer(
            answer_id='4',
            value=25,
        )
        answer_2 = Answer(
            answer_id='4',
            value=65,
        )

        self.assertEqual(answer_1.matches(answer_2), True)

    def test_matches_answer_simple_dict(self):
        answer_1 = Answer(
            answer_id='4',
            value=25,
        )
        answer_2 = {
            'answer_id': '4',
            'value': 25,
        }

        self.assertEqual(answer_1.matches_dict(answer_2), True)
