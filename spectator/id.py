from typing import Dict, Optional


class MeterId:
    def __init__(self, name: str, tags: Optional[Dict[str, str]] = None) -> None:
        if tags is None:
            self._tags = {}
        else:
            self._tags = tags
        self.name = name

    def tags(self) -> Dict[str, str]:
        return self._tags.copy()

    def with_stat(self, v: str) -> "MeterId":
        """Avoid breaking the API."""
        return self

    def with_default_stat(self, v: str) -> "MeterId":
        """Avoid breaking the API."""
        return self

    def with_tag(self, k: str, v: str) -> "MeterId":
        tags = self._tags.copy()
        tags[k] = v
        return MeterId(self.name, tags)

    def with_tags(self, new_tags: Dict[str, str]) -> "MeterId":
        tags = self._tags.copy()
        tags.update(new_tags)
        return MeterId(self.name, tags)

    def __hash__(self):
        return hash((self.name, frozenset(self._tags.items())))

    def __eq__(self, other) -> bool:
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __str__(self) -> str:
        if len(self._tags) > 0:
            tags = ["{}={}".format(k, v) for k, v in sorted(self._tags.items())]
            return "{},{}".format(self.name, ",".join(tags))
        else:
            return self.name
