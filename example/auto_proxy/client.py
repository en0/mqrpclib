#!/usr/bin/env python


from mqrpclib import RpcProxy, RpcProxyFactory
from shared import *
import logging
import json


logging.basicConfig(level="CRITICAL")


def show_response(resp):
    if resp:
        try:
            print json.dumps(resp.return_value, indent=2)
        except:
            print resp
    else:
        print "{}: {}".format(hex(resp.code), resp.error_message)


def run(p1, p2):

    print "Calling 'hello' on p1"
    res = p1.hello("world")
    print res

    print ""

    print "Calling 'hello' on p2"
    print p2.hello("world")


if __name__ == "__main__":
        _uri = "mqp://guest:guest@192.168.99.100/"
        exception_map = { 10: MyException }

        with RpcProxy.context(_uri) as proxy:
            TestServiceProxy = RpcProxyFactory.create(proxy, "v1")
            TestServiceProxy_Ex = RpcProxyFactory.create_ex(proxy, "v1")
            p1 = TestServiceProxy()
            p2 = TestServiceProxy_Ex()
            run(p1, p2)
