import os

if not os.getenv('KIVY_DOC'):
    import sys
    import kivy.input.providers.probesysfs
    from kivy.logger import Logger
    from kivy.input.providers.probesysfs import getconf

    def _read_line(path):
        with open(path) as f:
            return f.readline().strip()

    def _get_capabilities(self):
        path = os.path.join(self.path, "device", "capabilities", "abs")
        capabilities = []

        try:
            line = _read_line(path)
        except PermissionError:
            name = os.getenv('SNAP_NAME')
            if name:
                Logger.warn(
                    ('Snap Error: {} needs the hardware-observe interface to '
                     'access {}. To connect it, enter sudo snap connect '
                     '{}:hardware-observe').format(name, path, name)
                )
        else:
            long_bit = getconf("LONG_BIT")
            for i, word in enumerate(line.split(" ")):
                word = int(word, 16)
                subcapabilities = [bool(word & 1 << i)
                                   for i in range(long_bit)]
                capabilities[:0] = subcapabilities

        return capabilities

    def update_probesysfs():
        sys.modules['kivy.input.providers.probesysfs'].read_line = _read_line
        sys.modules['kivy.input.providers.probesysfs'].Input.get_capabilities = _get_capabilities  # NOQA: E501
