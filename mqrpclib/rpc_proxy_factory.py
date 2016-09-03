from rpc_proxy import RpcProxy
from rpc_exception import get_return_or_raise_exception as _get_ex
from contextlib import contextmanager
import pika


class RpcProxyFactory(object):
    """ RPC Proxy Factory can generate RpcProxy objects with service methods.
    
    RPC Proxy Factory can generate RpcProxy objects that abstract the
    interface for the specified remote service.  
    """

    def __call__(self, service_name, version, **kwargs):
        """ Create a proxy object that represents a service.

        Create a new Type that contains methods as defined by the service
        identified by service_name.

        Arguments:
            service_proxy:
                A RpcProxy that is connected to a service that implements the 
                _inspect interface.
            version:
                Create interface for the version provided

        Keyword Arguments:
            timeout: 
                Override the timeout used to call service._inspect
            with_exceptions:
                Implement the proxy methods using get_return_or_raise_exception
                method.
            extended_codes:
                Included a map to decode service specific error codes to a
                exception type. Thie argument only applies when with_exceptions
                is set.

        Returns:
            A type that, once instantiated, will expose the service methods.
        """

        kwargs.setdefault("timeout", self._timeout)
        kwargs.setdefault("with_exceptions", False)
        kwargs.setdefault("extended_codes", None)

        service_proxy = RpcProxy(
            service_name,
            self._chan,
            kwargs["timeout"]
        )

        return self._create_type(
            service_proxy,
            version,
            kwargs["with_exceptions"],
            kwargs["extended_codes"],
            kwargs["timeout"]
        );

    @classmethod
    @contextmanager
    def context(cls, url, timeout=None):
        """ Contextually managed instance of a RpcProxyFactory.

        This context manager will create a pika channel from the provided URL
        and instanciate a RpcProxyFacotry class for use. Once the context is
        expired, the channel will be closed.

        Arguments:
            url:
                A pika.URLParameters url that defines how to connect to rabbit.
            timeout:
                Optional. Define the timout to pass to the initialization of the
                RpcProxy instance.
        """
        conn = pika.BlockingConnection(pika.URLParameters(url))
        chan = conn.channel()
        ret = cls(chan, timeout)

        try:
            yield ret
        finally:
            conn.close()

    def __init__(self, chan, timeout=None):
        """ Initialize an instance of a RpcProxyFactory.

        Arguments:
            chan:
                A connected pika channel that has appropriate access to declare
                queues and consume requests.

            timeout:
                Optional, argument to pass RpcProxy for calls to
                service._inspect.
        """
        self._chan = chan
        self._timeout = None

    def _create_type(self, proxy, version, with_ex, codes, timeout):

        specs = _get_ex(proxy.remote_exec("_inspect", "built-in"))

        attr = {
            "__init__": self._make_init(proxy.service_name, self._chan),
            "__doc__": specs["description"]
        }

        for spec in specs["methods"]:

            if version != spec["version"]:
                continue

            attr[spec["method"]] = self._create_method(
                spec["method"],
                spec["version"],
                spec["desc"],
                with_ex,
                codes
            )

        type_name = "".join([proxy.service_name, "Proxy"])

        return type(str(type_name), (RpcAutoProxy,), attr)

    def _create_method(self, method, version, desc, with_ex, codes):

        def _wrapper(self, *args, **kwargs):

            _ret = self.remote_exec(method, version, args=args, kwargs=kwargs)

            if(with_ex):
                return _get_ex(_ret, codes)

            return _ret

        _wrapper.__doc__ = desc
        _wrapper.__name__ = str(method)
        _wrapper.__service_version__ = str(version)

        return _wrapper

    def _make_init(self, service_name, channel):

        def _wrapper(self):
            super(RpcAutoProxy, self).__init__(service_name, channel)

        _wrapper.__doc__ = "Create a proxy for the {} service.".format(service_name)
        _wrapper.__name__ = "__init__"
        return _wrapper


class RpcAutoProxy(RpcProxy):
    pass
