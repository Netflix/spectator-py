import os

from typing import Dict


def _add_non_empty(tags: Dict[str, str], tag: str, *env_vars: str) -> None:
    for env_var in env_vars:
        value = os.environ.get(env_var)
        if value is None:
            continue
        value = value.strip()
        if len(value) != 0:
            tags[tag] = value
            break


def tags_from_env_vars() -> Dict[str, str]:
    """Extract common infrastructure tags from the Netflix environment variables, which are
    specific to a process and thus cannot be managed by a shared SpectatorD instance."""
    tags = {}
    _add_non_empty(tags, "nf.container", "TITUS_CONTAINER_NAME")
    _add_non_empty(tags, "nf.process", "NETFLIX_PROCESS_NAME")
    return tags


def validate_tags(tags: Dict[str, str]) -> Dict[str, str]:
    valid_tags = {}

    for k, v in tags.items():
        if not isinstance(k, str) or len(k) == 0:
            continue
        if not isinstance(v, str) or len(v) == 0:
            continue
        valid_tags[k] = v

    return valid_tags
