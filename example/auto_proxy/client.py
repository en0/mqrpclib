#!/usr/bin/env python


from mqrpclib import RpcProxy, RpcProxyFactory
from shared import *
import logging
import json


logging.basicConfig(level="CRITICAL")


def run(p1, p2):

    print "Calling 'hello' on p1"
    res = p1.hello("world")
    print res

    print ""

    print "Calling 'hello' on p2"
    print p2.hello("world")


if __name__ == "__main__":
        _uri = "mqp://guest:guest@archer/"

        with RpcProxyFactory.context(_uri) as factory:
            TestServiceProxy = factory("autoproxy1", "v1")
            TestServiceProxy_Ex = factory("autoproxy1", "v1", with_exceptions=True)

            p1 = TestServiceProxy()
            p2 = TestServiceProxy_Ex()

            run(p1, p2)
