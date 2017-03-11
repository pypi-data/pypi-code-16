from mock import Mock


class MockOsPopen(Mock):
    def read(self, *args, **kwargs):
        return MockOsPopenSplitlines


class MockOsPopenSplitlines(object):
    @staticmethod
    def splitlines(*args, **kwargs):
        return ['00:02.0 VGA compatible controller: Intel Corporation Iris Graphics 6100 (rev 09)',
                '00:02.0 VGA compatible controller: Intel Corporation Iris Graphics 6100 (rev 09)']



