from call_to_api import call_to_api
from ParametrizedTestCase import ParametrizedTestCase


class TestMarbles(ParametrizedTestCase):

    def test_records_not_empty(self):
        print(self.year)
        records = call_to_api.get_information(self,2020,1,"Chabacano")
        self.assertNotEqual(len(records), 0, note=" the names should be uppercase because bla bla bla")