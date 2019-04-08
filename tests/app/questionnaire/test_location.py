from app.questionnaire.location import Location

from tests.app.app_context_test_case import AppContextTestCase


class TestLocation(AppContextTestCase):

    def test_location_url(self):
        location = Location('some-block')
        location_url = location.url()

        self.assertEqual(location_url, 'http://test.localdomain/questionnaire/some-block')

    def test_location_hash(self):
        location = Location('some-block')

        self.assertEqual(hash(location), hash(frozenset(location.__dict__.values())))

    def test_load_location_from_dict(self):
        location_dict = {
            'block_id': 'some-block',
            'list_item_id': 'adhjiiw',
            'list_operation': 'remove'
        }

        location = Location.from_dict(location_dict)

        self.assertEqual(location.block_id, 'some-block')
        self.assertEqual(location.list_item_id, 'adhjiiw')
        self.assertEqual(location.list_operation, 'remove')

    def test_load_location_from_dict_without_list_item_id(self):
        location_dict = {
            'block_id': 'some-block',
        }

        location = Location.from_dict(location_dict)

        self.assertEqual(location.block_id, 'some-block')
        self.assertEqual(location.list_item_id, None)
        self.assertEqual(location.list_operation, None)
