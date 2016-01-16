from rpc_request_message import RpcRequestMessage
from rpc_response_message import RpcResponseMessage
import rpc_exception as exp
import pika
import logging


class RpcServer(object):
    def __init__(self, url, prefetch=1, desc=None):
        self._procs = {}
        self._desc = desc or "Not Available"
        parameters = pika.URLParameters(url)
        self._logger = logging.getLogger(__name__)
        self._conn = pika.BlockingConnection(parameters)
        self._chan = self._conn.channel()
        self._chan.basic_qos(prefetch_count=prefetch)
        self.register("_help", "v1", self._help)

    def _help(self, name=None, version=None):
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

    def register(self, name, version, fn, desc=None):
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
        self._chan.start_consuming()
