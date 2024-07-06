from spectator.registry import Registry

# DEPRECATED: The GlobalRegistry construct is no longer necessary, since this library became a thin
# client implementation, but it was kept to help minimize the work associated with adopting the new
# version of this library. The previous advice for using this library offered many examples like the
# following:
#
#   from spectator import GlobalRegistry
#
#   GlobalRegistry.counter("server.numRequests").increment()
#
# Now, with the thin client version, this library is stateless. You can have one or more Registry
# objects in your code, and the preferred method of using it is as follows:
#
#   from spectator.registry import Registry
#
#   r = Registry()
#   r.counter("server.numRequests").increment()
#
# Using this method of instantiating the Registry offers you the opportunity to provide an alternate
# configuration, to supply a different output location or a set of extra common tags. Or, keep the
# defaults and use the Registry as-is.

GlobalRegistry = Registry()
