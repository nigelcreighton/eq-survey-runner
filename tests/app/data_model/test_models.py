from app.data_model.models import QuestionnaireState
from tests.app.app_context_test_case import AppContextTestCase


class TestModels(AppContextTestCase):

    def test_questionnaire_state(self):
        original, new = self._make_models(QuestionnaireState, ['someuser', 'somedata', 1])

        self.assertEqual(original, new)

    @staticmethod
    def _make_models(model_type, args):
        orig = model_type(*args)
        new = model_type.from_app_model(orig.to_app_model())
        orig_dict = orig.__dict__
        del orig_dict['_sa_instance_state']
        new_dict = new.__dict__
        del new_dict['_sa_instance_state']

        return orig_dict, new_dict
