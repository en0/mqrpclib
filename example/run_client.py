#!/usr/bin/env python2
from mqrpclib import RpcProxy
import logging
from time import sleep
from sys import stdout


logging.basicConfig(level="CRITICAL")


class TestProxy(RpcProxy):
    def async_method1_v1(self, a, b):
        return self.remote_exec(
            "method1",
            "v1",
            args={"a": a, "b": b},
            blocking=False
        )

    def method1_v1(self, a, b):
        return self.remote_exec("method1", "v1", args={"a": a, "b": b})

    def method2_v1(self):
        return self.remote_exec("method2", "v1")


def show_response(resp):
    if resp:
        print resp.return_value
    else:
        print "{}: {}".format(hex(resp.code), resp.error_message)


if __name__ == "__main__":
        _uri = "mqp://guest:guest@localhost/"
        _a, _b = 1, 2

        print "Testing syncronous example..."
        with TestProxy.context(_uri) as proxy:
            print "Calculating: {} + {}...".format(_a, _b)
            show_response(proxy.method1_v1(_a, _b))

        print "\nTesting asyncronous example..."
        with TestProxy.context(_uri) as proxy:
            print "Calculating: {} + {}...".format(_a, _b)
            _corr_id = proxy.async_method1_v1(_a, _b)
            while not proxy.has_response(_corr_id):
                stdout.write(".")
                stdout.flush()

            stdout.write("\nResponse: ")
            show_response(proxy.get_response(_corr_id))
