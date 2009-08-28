from kumquat.tests import *

class TestActionController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='action', action='index'))
        # Test response...
