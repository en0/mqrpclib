from rpc_request_message import RpcRequestMessage
from rpc_response_message import RpcResponseMessage
import rpc_exception as exp
import pika
import logging


class RpcServer(object):
    @classmethod
    def from_uri(cls, uri, prefetch=None):
        """ Create a RPC Sserver using a url.

        This method will connect to rabbit and create a channel that is then
        passed to the RpcService initialization.

        Arguments:
            uri:
                A pika.URLParameters url that defines how to connect.
            prefetch:
                Set the qos prefetch on queues used by this service.

        Returns:
            An instanciated RpcServer class with connected pika channel.
        """
        _chan = pika.BlockingConnection(
            pika.URLParameters(uri)
        ).channel()

        if prefetch:
            _chan.basic_qos(prefetch_count=prefetch)

        return cls(_chan)

    @property
    def service_description(self):
        """ The help method's Service Description value """
        return self._desc

    @service_description.setter
    def service_description(self, value):
        self._desc = value

    def register(self, name, version, fn):
        """ Expose a method or function as a RPC method.

        Create a queue that can except requests from a remote client that will
        be dispatched to the provided function or method. This method is
        registered under a specific version tag to allow server side version
        management.

        Arguments:
            name:
                The exposed name of the method.
            version:
                The version tag for this function associated with this name.
            fn:
                The function or method to execute when requests are recieved for
                this name and version.

        Raises:
            Exception if a version is already registered.
        """
        if name not in self._procs:
            self._procs[name] = dict(
                versions={},
                queue=self._chan.queue_declare(name)
            )
            self._chan.basic_consume(
                self._request_handler,
                queue=name
            )

        elif version in self._procs[name]['versions']:
            raise Exception(
                "Attempt to register a duplicate version on '{}'".format(name)
            )

        self._procs[name]["versions"][version] = fn

    def run(self):
        """ Start recieving requests. (Blocking)

        This method starts the async core main loop. The main loop can be
        started manually with the same effect if you have multiple RpcServers
        attached to the same channel.
        """
        self._chan.start_consuming()

    def __init__(self, channel):
        """ Initialize a RpcService.

        This method requires a connected channel with the proper authority to
        recieve and publish requests to queues it creates.

        Arguments:
            channel:
                A connected pika channel.
        """
        self._procs = {}
        self._desc = ''
        self._logger = logging.getLogger(__name__)
        self._chan = channel
        self.register("_help", "v1", self._help)

    def _help(self, name=None, version=None):
        """ Retrieve details about remote functions.

        Retireve detials about registered methods and version available in this
        service. All parameters are optional.

        Arguments:
            name: The name of the method to describe.
            version: The specific version of the method to describe.

        If no arguments are given, a list of available methods are provided.
        Format:
            {
                help_type: "options",
                service: <Service Description>,
                methods: [<List of available methods>]
            }

        If only name is provided, a list of available versions are provided.
        Format:
            {
                help_type: "versions",
                method: <Method Name>,
                versions: [<List of available versions>]
            }

        If name and version is provided, details of the function are provided.
        Format:
            {
                help_type: "method",
                method: <Method Name>,
                version: <Method Version>,
                desc: <Doc string of target method>
            }

        Returns:
            Dict with information about the the provided method.
        """
        if not name or name not in self._procs:
            return {
                "help_type": "options",
                "service": self._desc,
                "methods": self._procs.keys(),
            }

        elif not version:
            return {
                "help_type": "versions",
                "method": name,
                "versions": self._procs[name]["versions"].keys()
            }

        else:
            return {
                "help_type": "method",
                "method": name,
                "version": version,
                "desc": self._get_function(name, version).__doc__
            }

    def _get_function(self, name, version):
        try:
            _proc = self._procs[name]

        except KeyError:
            raise exp.DispatchException(
                "Failed to locate handler for routing key '{}'".format(name)
            )

        try:
            _fn = _proc["versions"][version]

        except KeyError:
            raise exp.DispatchException(
                "Failed to locate version '{}' for routing key '{}'".format(
                    version,
                    name
                )
            )

        return _fn

    def _request_handler(self, ch, meth, prop, body):
        _key = meth.routing_key

        try:
            _req = RpcRequestMessage.loads(body)
            _fn = self._get_function(_key, _req.version)

            self._logger.debug("Dipsatching Request: {}".format(_req))

            if _req.args:
                _data = _fn(**_req.args)

            else:
                _data = _fn()

            _resp = RpcResponseMessage(0, return_value=_data)

            self._logger.debug("Preparing Response: {}".format(_resp))

            _ret = _resp.dumps()

        except exp.ExceptionBase as ex:
            self._logger.info("Exception Detected: {}".format(ex))
            _ret = RpcResponseMessage(ex.code, error_message=ex.message).dumps()

        except Exception as ex:
            self._logger.warning("Unhandled Exception Detected: {}".format(ex))
            _ex = exp.UnhandledException(ex.message)
            _ret = RpcResponseMessage(
                _ex.code,
                error_message=_ex.message
            ).dumps()

        self._logger.debug("Dispatching Response: {}".format(_ret))

        ch.basic_ack(delivery_tag=meth.delivery_tag)
        if prop.reply_to:
            self._logger.debug("Responding to request: {}".format(_key))
            ch.basic_publish(
                exchange='',
                routing_key=prop.reply_to,
                body=str(_ret),
                properties=pika.BasicProperties(
                    correlation_id=prop.correlation_id
                )
            )
