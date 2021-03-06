from ingest.call_to_api import call_to_api
from ingest.ParametrizedCallToAPITest import ParametrizedCallToAPITest

class CallToAPITest(ParametrizedCallToAPITest):
    def test_records_not_empty(self):
        records = call_to_api.get_information(self,self.year,self.month)
        self.assertNotEqual(len(records), 0)
