from os import environ
from typing import Any, Dict, Optional

from spectator.commontags import common_tags


class SidecarConfig:
    """To provide a custom configuration for Spectator-py, pass a dictionary to the constructor
    which returns values for the keys listed below. Omitting keys will cause this class to return
    the default values.

    {
      "sidecar.common-tags": {"key": "value"},
      "sidecar.output-location": "location"
    }

    Then provide the custom instance to a new instance of the Registry, rather than relying on
    the GlobalRegistry, which has a default configuration. For example:

    r = Registry(config=SidecarConfig({"sidecar.output-location": "memory"}))
    r.counter("test").increment()
    """

    def __init__(self, config: Dict[str, Any] = None) -> None:
        """Optionally initialize with a dictionary which returns values that override the
        defaults."""
        if config is None:
            self._config = {}
        else:
            self._config = config

    def common_tags(self) -> Dict[str, str]:
        """Common infrastructure tags from the Netflix environment variables."""
        return self._config.get("sidecar.common-tags", common_tags())

    @staticmethod
    def _valid_output_location(output: Optional[str]) -> bool:
        if output is None:
            return False
        return (output in ["none", "memory", "stdout", "stderr"] or
                output.startswith("file://") or
                output.startswith("udp://"))

    def output_location(self) -> str:
        """
        The location where data will be emitted. Supported values include:

          * `none` - disable output
          * `memory` - write to memory (SidecarWriter internal list `_messages`)
          * `stdout` - write to standard out for the process
          * `stderr` - write to standard error for the process
          * `file://$path_to_file` - write to a file (e.g. file:///tmp/foo/bar)
          * `udp://$host:$port` - write to a UDP socket

        The default value is the port used by SpectatorD.

        The output location for the GlobalRegistry can be selected by configuring an
        environment variable SPECTATOR_OUTPUT_LOCATION with one of the values listed
        above. Setting a custom output location may be useful for integration testing.
        """
        config_value = self._config.get("sidecar.output-location")
        env_value = environ.get("SPECTATOR_OUTPUT_LOCATION")

        if self._valid_output_location(config_value):
            return config_value
        elif self._valid_output_location(env_value):
            return env_value
        else:
            return "udp://127.0.0.1:1234"
