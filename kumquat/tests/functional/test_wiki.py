from kumquat.tests import *

class TestWikiController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='wiki'))
        # Test response...
