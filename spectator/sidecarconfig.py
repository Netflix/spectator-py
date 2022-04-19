from typing import Dict, Any

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

    def output_location(self) -> str:
        """
        The location where data will be emitted. Supported values include:

          * `none` - disable output
          * `stdout` - write to standard out for the process
          * `stderr` - write to standard error for the process
          * `file://$path_to_file` - write to a file (e.g. file:///tmp/foo/bar)
          * `udp://$host:$port` - write to a UDP socket

        The default value is the port used by SpectatorD.
        """
        return self._config.get("sidecar.output-location", "udp://127.0.0.1:1234")
