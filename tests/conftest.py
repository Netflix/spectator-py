import os

# Remove the container and process names that the platform may inject into the environment, so that
# tests which create a Config or Registry from the real environment get the expected tags on any host.
# This runs before the test modules import spectator, which creates the GlobalRegistry at import time.
for key in ["NETFLIX_CONTAINER_NAME", "NETFLIX_PROCESS_NAME", "TITUS_CONTAINER_NAME"]:
    os.environ.pop(key, None)
