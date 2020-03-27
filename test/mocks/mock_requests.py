class MockResponse():
    def __init__(self, status='OK', articles=[]):
        self.data = {
            'status': status,
            'response': {
                'docs': articles,
            },
        }

    def json(self):
        return self.data
