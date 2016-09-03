#!/usr/bin/env python


from mqrpclib import RpcProxy, RpcProxyFactory
from shared import *
import logging
import json


logging.basicConfig(level="CRITICAL")


def run(proxy):
    proxy.test_exception()


if __name__ == "__main__":
        _uri = "mqp://guest:guest@archer/"
        exception_map = { 10: MyException }

        with RpcProxyFactory.context(_uri) as factory:
            TestServiceProxy = factory("autoproxy1", "v1", with_exceptions=True, extended_codes=exception_map)
            myService = TestServiceProxy()
            run(myService)
