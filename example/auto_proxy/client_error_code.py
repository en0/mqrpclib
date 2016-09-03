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
        _uri = "mqp://guest:guest@archer/"

        with RpcProxyFactory.context(_uri) as factory:
            TestServiceProxy = factory("autoproxy1", "v1")
            myService = TestServiceProxy()
            run(myService)
