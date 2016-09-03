#!/usr/bin/env python


from mqrpclib import RpcProxy, RpcProxyFactory
from shared import *
import logging
import json


logging.basicConfig(level="CRITICAL")


def run(proxy1, proxy2):
    help(proxy1)
    help(proxy2)


if __name__ == "__main__":
        _uri = "mqp://guest:guest@archer/"

        with RpcProxyFactory.context(_uri) as factory:
            TestServiceProxy_v1 = factory("autoproxy1", "v1")
            TestServiceProxy_v2 = factory("autoproxy1", "v2")
            p1 = TestServiceProxy_v1()
            p2 = TestServiceProxy_v2()
            run(p1, p2)
