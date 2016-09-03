#!/usr/bin/env python2
from mqrpclib import RpcServer
import logging


logging.basicConfig(level="CRITICAL")


class ImplClass(object):
    def hello_v1(self, name="world"):
        """ Greet user.

        Greet the user with a personalized message.

        Arguments:
            name: The name of the user.

        Returns:
            A personalized message as a string.
        """
        return "Hello, {}!".format(name)


if __name__ == "__main__":
        """ mqp://username:password@host:port/<virtual_host>[?query-string] """
        impl = ImplClass()
        srv = RpcServer.from_uri("simple1", "mqp://guest:guest@archer/")
        srv.service_description = "Rpc service example implementation."
        srv.register("hello", "v1", impl.hello_v1)
        srv.run()

