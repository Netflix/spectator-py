from os import environ
from typing import Dict, Optional

from spectator.common_tags import tags_from_env_vars, validate_tags
from spectator.writer.new_writer import is_valid_output_location


class Config:
    """Create a new configuration with the provided location and extra common tags. All fields are
    optional. The extra common tags are added to every metric, on top of the common tags provided
    by spectatord.

    Possible values for `location` are:

      * `none`   - Configure a no-op writer that does nothing. Can be used to disable metrics collection.
      * `memory` - Write metrics to memory. Useful for testing.
      * `stderr` - Write metrics to standard error.
      * `stdout` - Write metrics to standard output.
      * `udp`    - Write metrics to the default spectatord UDP port. This is the default value.
      * `unix`   - Write metrics to the default spectatord Unix Domain Socket. Useful for high-volume scenarios.
      * `file:///path/to/file` - Write metrics to a file or a Unix Domain Socket.
      * `udp://host:port`      - Write metrics to a UDP socket.

    The output location can be overridden by configuring an environment variable SPECTATOR_OUTPUT_LOCATION
    with one of the values listed above. Overriding the output location may be useful for integration testing.
    """

    def __init__(self, location: str = "udp", extra_common_tags: Optional[Dict[str, str]] = None) -> None:
        if extra_common_tags is None:
            extra_common_tags = {}
        self.extra_common_tags = self.calculate_extra_common_tags(extra_common_tags)
        self.location = self.calculate_location(location)

    @staticmethod
    def calculate_extra_common_tags(common_tags: Dict[str, str]) -> Dict[str, str]:
        merged_tags = validate_tags(common_tags)

        # merge common tags with env var tags; env vars take precedence
        for k, v in tags_from_env_vars().items():
            merged_tags[k] = v

        return merged_tags

    @staticmethod
    def calculate_location(location: str) -> str:
        if not is_valid_output_location(location):
            raise ValueError(f"spectatord output location is invalid: {location}")

        override = environ.get("SPECTATOR_OUTPUT_LOCATION")
        if override is not None:
            if not is_valid_output_location(override):
                raise ValueError(f"SPECTATOR_OUTPUT_LOCATION is invalid: {override}")
            location = override

        return location
