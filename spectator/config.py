from os import environ
from typing import Dict, Optional

from spectator.common_tags import tags_from_env_vars, validate_tags


class Config:
    """Create a new configuration with the provided location and extra common tags. All fields are
    optional. The extra common tags are added to every metric, on top of the common tags provided
    by `spectatord`.

    Possible values for `location` are:

      * `none`   - Configure a no-op writer that does nothing. Can be used to disable metrics collection.
      * `memory` - Write metrics to memory. Useful for testing.
      * `stderr` - Write metrics to standard error.
      * `stdout` - Write metrics to standard output.
      * `udp`    - Write metrics to the default spectatord UDP port. This is the default value.
      * `unix`   - Write metrics to the default spectatord Unix Domain Socket. Useful for high-volume scenarios.
      * `file:///path/to/file` - Write metrics to a file.
      * `udp://host:port`      - Write metrics to a UDP port.
      * `unix:///path/to/file` - Write metrics to a Unix Domain Socket.

    The output location can be overridden by configuring an environment variable `SPECTATOR_OUTPUT_LOCATION`
    with one of the values listed above. Overriding the output location may be useful for integration testing.

    The `buffer_size` is used to configure an optional `LineBuffer`, which caches protocol lines locally, before
    flushing them to `spectatord`. Flushes occur under two conditions: (1) the buffer size is exceeded, or (2)
    five seconds has elapsed. The buffer is available for the `SocketWriter` (udp and unix), where performance
    matters most, and it can increase the maximum RPS of communication to `spectatord` from ~80K to 150K (1.8X).
    The `LineBuffer` is disabled by default (with size zero), to ensure that the default operation of the library
    works under most circumstances. Under single-threaded performance testing, a 2KB buffer is a good configuration.

    When the `LineBuffer` is enabled, a background thread is started which will flush metrics every five seconds,
    which means that some care should be exercised when a custom Registry with buffering is instantiated in pre-fork
    environments.

    The `is_global` flag is used to help control logging for the GlobalRegistry.
    """

    def __init__(self, location: str = "udp", extra_common_tags: Optional[Dict[str, str]] = None,
                 buffer_size: int = 0, is_global: bool = False) -> None:
        self.location = self.calculate_location(location)
        if extra_common_tags is None:
            extra_common_tags = {}
        self.extra_common_tags = self.calculate_extra_common_tags(extra_common_tags)
        self.buffer_size = buffer_size
        self.is_global = is_global

    @staticmethod
    def is_valid_output_location(location: str) -> bool:
        if not isinstance(location, str):
            return False
        return location in ["none", "memory", "stdout", "stderr", "udp", "unix"] or \
            location.startswith("file://") or \
            location.startswith("udp://") or \
            location.startswith("unix://")

    def calculate_location(self, location: str) -> str:
        if not self.is_valid_output_location(location):
            raise ValueError(f"spectatord output location is invalid: {location}")

        override = environ.get("SPECTATOR_OUTPUT_LOCATION")
        if override is not None:
            if not self.is_valid_output_location(override):
                raise ValueError(f"SPECTATOR_OUTPUT_LOCATION is invalid: {override}")
            location = override

        return location

    @staticmethod
    def calculate_extra_common_tags(common_tags: Dict[str, str]) -> Dict[str, str]:
        merged_tags = validate_tags(common_tags)

        # merge common tags with env var tags; env vars take precedence
        for k, v in tags_from_env_vars().items():
            merged_tags[k] = v

        return merged_tags
