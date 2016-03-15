from app.model.section import Section
from app.model.question import Question
import unittest


class SectionModelTest(unittest.TestCase):
    def test_basics(self):
        section = Section()

        section.id = 'some-id'
        section.title = 'my section object'

        question1 = Question()
        question2 = Question()

        section.add_question(question1)
        section.add_question(question2)

        self.assertEquals(section.id, 'some-id')
        self.assertEquals(section.title, 'my section object')
        self.assertIsNone(section.container)
        self.assertEquals(len(section.questions), 2)
        self.assertEquals(section.questions[0], question1)
        self.assertEquals(section.questions[1], question2)

        self.assertEquals(question1.container, section)
        self.assertEquals(question2.container, section)