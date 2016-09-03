#!/usr/bin/env python


import json
import inspect
from mqrpclib import RpcServer
from mqrpclib.rpc_exception import RpcException
from shared import *
import logging


class Service(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def hello_v1(self, name):
        """ Greet the user.

        This method will send a personalized message back to the caller.

        Version: v1

        Arguments:
            name: The name of the caller.

        Returns:
            A greeting in the form of a unicode string.
        """
        _ret = "Hello, {}!".format(name)
        return _ret

    def hello_v2(self, name="world"):
        """ Greet the user.

        This method will send a personalized message back to the caller.

        Version: v2

        Arguments:
            name: The optional name of the caller. Default "world"

        Returns:
            A greeting in the form of a unicode string.
        """
        _ret = "Hello, {}!".format(name)
        return _ret

    def test_exception_v1(self):
        """ Cause a server side exception.

        This method will throw a custom server-side exception.

        Version: v1

        Arguments: None

        Returns: None

        Exceptions (Code):
            MyException (10): Thrown every time the method is called.
        """
        raise MyException("Failed to do something that is a documented failure")


if __name__ == "__main__":
    """ mqp://username:password@host:port/<virtual_host>[?query-string] """
    logging.basicConfig(level="CRITICAL")

    impl = Service()

    srv = RpcServer.from_uri("autoproxy1", "mqp://guest:guest@archer/")
    srv.service_description = "Rpc service example implementation."
    srv.register("hello", "v1", impl.hello_v1)
    srv.register("hello", "v2", impl.hello_v2)
    srv.register("test_exception", "v1", impl.test_exception_v1)

    srv.run()
