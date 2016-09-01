from rpc_exception import get_return_or_raise_exception as _get_ex


class RpcAutoProxy(object):
    pass

class RpcProxyFactory(object):

    @classmethod
    def create(cls, service_proxy, version):
        """ Create a proxy object that represents a service.

        Create a new Type that contains methods as defined by the service
        connected to the service_proxy.  

        Arguments:
            service_proxy:
                A RpcProxy that is connected to a service that implements the 
                _inspect interface.
            version:
                Create interface for the version provided

        Returns:
            A type that, once instantiated, will expose the service methods.
        """
        return _create_type(service_proxy, version, False, None);


    @classmethod
    def create_ex(cls, service_proxy, version, extended_codes=None):
        """ Create a proxy object that represents a service.

        Create a new Type that contains methods as defined by the service
        connected to the service_proxy.  When a method is invoked, the method
        will retrieve values useing the get_return_or_raise_exception method.

        Arguments:
            service_proxy:
                A RpcProxy that is connected to a service that implements the 
                _inspect interface.
            version:
                Create interface for the version provided
            extended_codes:
                Add service specific exception types. For more information, see
                get_return_or_raise_exception documentation.

        Returns:
            A type that, once instantiated, will expose the service methods.
        """
        return _create_type(service_proxy, version, True, extended_codes);


def _create_type(proxy, version, with_exceptions, extended_codes):

    specs = _get_ex(proxy.remote_exec("_inspect", "built-in"))

    attr = {}

    for spec in specs["methods"]:

        if version != spec["version"]:
            continue

        attr[spec["method"]] = _create_method(
            proxy,
            spec["method"],
            spec["version"],
            spec["desc"],
            with_exceptions,
            extended_codes
        )

    type_name = "".join([specs.get("service", "Auto"), "Proxy"])

    return type(str(type_name), (RpcAutoProxy,), attr)


def _create_method(proxy, method, version, desc, with_exceptions, extended_codes):

    def _wrapper(self, *args, **kwargs):

        _ret = proxy.remote_exec(method, version, args=args, kwargs=kwargs)

        if(with_exceptions):
            return _get_ex(_ret, extended_codes)

        return _ret

    _wrapper.__doc__ = desc
    _wrapper.__name__ = str(method)
    _wrapper.__service_version__ = str(version)

    return _wrapper;
