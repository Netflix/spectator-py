class MeterId:
    def __init__(self, name, tags={}):
        self.name = name
        self._tags = tags.copy()

    def tags(self):
        return self._tags.copy()

    def with_stat(self, v):
        return self.with_tag('statistic', v)

    def with_tag(self, k, v):
        tags = self._tags.copy()
        tags[k] = v
        return MeterId(self.name, tags)

    def with_tags(self, ts):
        tags = self._tags.copy()
        tags.update(ts)
        return MeterId(self.name, tags)

    def __hash__(self):
        return hash((self.name, frozenset(self._tags.items())))

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __str__(self):
        items = sorted(self._tags.items())
        tagStr = ",".join(["{}={}".format(t[0], t[1]) for t in items])
        return "{}:{}".format(self.name, tagStr)
