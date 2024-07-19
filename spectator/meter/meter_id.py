import logging
import re
from typing import Dict, Optional

from spectator.common_tags import validate_tags


class MeterId:
    """The name and tags which uniquely identify a Meter instance. The tags are key-value pairs of
    strings. This class should NOT be used directly. Instead, use the Registry.new_id() method, to
    ensure that any extra common tags are properly applied to the Meter."""

    INVALID_CHARS = re.compile("[^-._A-Za-z0-9~^]")

    def __init__(self, name: str, tags: Optional[Dict[str, str]] = None) -> None:
        if tags is None:
            tags = {}
        self._logger = logging.getLogger(__name__)
        self._name = name
        self._tags = self._validate_tags(tags)
        self.spectatord_id = self._to_spectatord_id(self._name, self._tags)

    def _validate_tags(self, tags: Dict[str, str]) -> Dict[str, str]:
        valid_tags = validate_tags(tags)

        if valid_tags != tags:
            msg = "Id(name=%s, tags=%s) is invalid due to tag keys or values which are not strings " \
                  "or are zero-length strings; proceeding with truncated tags Id(name=%s, tags=%s)"
            self._logger.warning(msg, self._name, tags, self._name, valid_tags)

        return valid_tags

    def _replace_invalid_chars(self, s: str) -> str:
        return self.INVALID_CHARS.sub("_", s)

    def _to_spectatord_id(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        result = self._replace_invalid_chars(name)

        for k, v in sorted(tags.items()):
            k = self._replace_invalid_chars(k)
            v = self._replace_invalid_chars(v)
            result += f",{k}={v}"

        return result

    def name(self) -> str:
        return self._name

    def tags(self) -> Dict[str, str]:
        return self._tags.copy()

    def with_tag(self, k: str, v: str) -> "MeterId":
        new_tags = self._tags.copy()
        new_tags[k] = v
        return MeterId(self._name, new_tags)

    def with_tags(self, tags: Dict[str, str]) -> "MeterId":
        if len(tags) == 0:
            return self
        new_tags = self._tags.copy()
        new_tags.update(tags)
        return MeterId(self._name, new_tags)

    def __hash__(self):
        return hash((self._name, frozenset(self._tags.items())))

    def __eq__(self, other) -> bool:
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __str__(self) -> str:
        return f"Id(name={self._name}, tags={self._tags})"
