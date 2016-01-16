#!/usr/bin/env python2
from mqrpclib import RpcServer
import logging


class ImplClass(object):
    def method1_v1(self, a, b):
        """ Add 2 numbers.

        Get the sum of 2 provided numbers.

        Arguments:
            a: An integer representing the first number.
            b: An integer representing the second number.

        Returns:
            An integer represeting the sum of a and b
        """
        return a + b


if __name__ == "__main__":
        """ mqp://username:password@host:port/<virtual_host>[?query-string] """
        logging.basicConfig(level="DEBUG")
        impl = ImplClass()
        srv = RpcServer("mqp://guest:guest@localhost/")
        srv.register("method1", "v1", impl.method1_v1)
        srv.run()
