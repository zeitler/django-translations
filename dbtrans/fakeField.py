class FakeField(object):
    loaded = False

    def __init__(self, languages):
        for f in languages:
            setattr(self, f, "")
