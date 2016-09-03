#!/usr/bin/env python2

from mqrpclib import RpcProxy
import logging


logging.basicConfig(level="CRITICAL")


class Proxy(RpcProxy):
    def hello(self, *args, **kwargs):
        resp = self.remote_exec(
            "hello",
            "v1",
            args=args,
            kwargs=kwargs
        )

        # Your error handling should very.
        if resp.code == 0:
            return resp.return_value

        print "Warning: the call failed."
        return "ERROR!"


if __name__ == "__main__":
    with Proxy.context("simple1", "mqp://guest:guest@archer/") as proxy:
        print "With Args"
        print proxy.hello("user")

        print ""

        print "With Keyword Args"
        print proxy.hello(name="user")

        print ""

        print "With NO Args"
        print proxy.hello()
