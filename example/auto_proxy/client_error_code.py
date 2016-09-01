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


def run(proxy):
    res = proxy.test_exception()
    show_response(res)


if __name__ == "__main__":
        _uri = "mqp://guest:guest@192.168.99.100/"
        exception_map = { 10: MyException }

        with RpcProxy.context(_uri) as proxy:
            TestServiceProxy_V1 = RpcProxyFactory.create(proxy, "v1")
            myService = TestServiceProxy_V1()
            run(myService)
