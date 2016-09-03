from contextlib import contextmanager
from rpc_exception import EX_CLIENT_TIMEOUT_EXCEPTION
from rpc_request_message import RpcRequestMessage
from rpc_response_message import RpcResponseMessage
from time import time
from uuid import uuid4
from version import VERSION
import logging
import pika


class RpcProxy(object):
    @classmethod
    @contextmanager
    def context(cls, service_name, url, timeout=None):
        """ Contextually managed instance of a RpcProxy.

        This context manager will create a pika channel from the provided URL
        and instanciate a RpcProxy class for use. Once the context is expired,
        the channel will be closed.

        Arguments:
            service_name:
                The name of the service to connect to.
            url:
                A pika.URLParameters url that defines how to connect to rabbit.
            timeout:
                Optional. Define the timout to pass to the initialization of the
                RpcProxy instance.
        """
        conn = pika.BlockingConnection(pika.URLParameters(url))
        chan = conn.channel()
        _proxy = cls(service_name, chan, timeout)

        try:
            yield _proxy
        finally:
            conn.close()

    def remote_exec(self, name, version, args=None, kwargs=None, blocking=True, timeout=None):
        """ Execute a remote procedure call on the specified method and version

        This method will dispatch a request for a remote execution of the method
        specified by `name`. The version is used to identify a specific version
        of the remote procedure.

        The request can take time to execute. This method can optionaly block
        for a response. If it does block, the method will return the result of
        the request or a timeout response if the time took longer then the
        timeout specified.

        If a non-blocking request is made, this method will return a correlation
        id that chan be used to retrieve the return value with the has_response
        and get_response methods.

        Arguments:
            name:
                The name of the remote method to call.
            version:
                The version of the remote method to call.
            args:
                Optional: A tuple of the arguments to pass to the remote method.
            kwargs:
                Optional: A dict of the arguments to pass as Keyword args to
                the remote method.
            blocking:
                Optional: A flag indicating if this method should wait for a
                response. Default: True
            timeout:
                Optional: The aproximate amount of time the method should block,
                if applicable, for a response. Default: instance default.

        Returns:
            correlation_id if blocking=False, else RpcResponseMessage that
            represents the result of the request.
        """
        _req = RpcRequestMessage(version, args, kwargs)
        _corr_id = str(uuid4())
        self._response[_corr_id] = None

        self._chan.basic_publish(
            exchange='',
            routing_key=".".join([self._service_name, name]),
            properties=pika.BasicProperties(
                correlation_id=_corr_id,
                reply_to=self._callback_queue
            ),
            body=_req.dumps()
        )

        # If not blocking, return the correlation id so the caller can lookup
        # the return if it wants too.
        if not blocking:
            return _corr_id

        return self.get_response(
            _corr_id,
            clear_response=True,
            wait=True,
            timeout=timeout or self._timeout
        )

    def has_response(self, correlation_id):
        """ Check if a response is available for the specified correlation_id

        Each request is assigned a unique correlation id when it is dispatched
        to the remote service. That correlation id is returned with the
        response. This ID can be used to lookup the return value.

        This method is an invarient test for get_response and should evaluate
        to True before calling get_response unless wait is set.

        Arguments:
            correlation_id:
                The unique ID of the dispatched request.

        Returns:
            True, if the response is available. Else, False.
        """
        # TODO: This is streaching the Law of Demeter just a little bit.
        # Are there other options?
        self._chan.connection.process_data_events()
        return (self._response[correlation_id] is not None)

    def get_response(self, correlation_id, clear_response=True, wait=False,
                     timeout=None):
        """ Get a response for the specified correlation_id.

        Each specific request is assigned a unique correlation id when it is
        dispatched to the remote service. That correlation id is returned. This
        ID can be used to lookup the return value.

        The response can take time. If this method is called without the wait
        option, it is expected that the caller will validate the invarient
        `has_response` to make sure the return data is available.

        If wait is specified, this function will block for the given timeout or
        default timeout if not provided before returning the result.

        Arguments:
            correlation_id:
                The unique ID of the dispatched request.
            clear_response:
                Flag indicating that the response should be cleared after it is
                retrieved.
            wait:
                FLag indicating the system should block until the response is
                available or untill the timeout has expired.
            timeout:
                Optional, the aproximate time the system will block in waiting
                for a response if the wait flag is set. A zero value indicates
                infinity. Default: instance timeout set at initialization.

        Returns:
            A RpcResponseMessage that represents the result of the associated
            request.
        """
        if wait:
            # If timeout is zero then we will wait forever
            _timeout = timeout or self._timeout
            _expr_time = time() + _timeout if _timeout > 0 else None
            while not self.has_response(correlation_id):
                if _expr_time and _expr_time <= time():
                    return RpcResponseMessage(
                        EX_CLIENT_TIMEOUT_EXCEPTION,
                        error_message="Request timed out."
                    )

        _resp = RpcResponseMessage.loads(self._response[correlation_id])

        if _resp._mqrpclib_version != VERSION:
            self._logger.warning(
                "Server version is {} and client is {}."
                "This could cause unexpected behavor.".format(
                    _resp._mqrpclib_version,
                    VERSION
                )
            )

        if clear_response:
            del self._response[correlation_id]

        return _resp

    def __init__(self, service_name, chan, timeout=None):
        """ Initialize an instance of a RPC Class.

        The RPC Class should be overridden. It expects a connected channel that
        it will use to declare its handler queues.

        Arguments:
            service_name:
                The name of the service to connect to on the given channel.

            chan:
                A connected pika channel that has appropriate access to declare
                queues and consume requests.

            timeout:
                Optional, argument to set the default amount of time to wait
                for a rpc resonse from a request. This timeout can be overridden
                on calls that use it (get_response and remote_exec). A zero
                value indicates infinite timeout. Default: 30 seconds.
        """
        self._logger = logging.getLogger(__name__)
        self._response = {}
        self._timeout = timeout or 30
        self._service_name = service_name
        self._chan = chan
        self._callback_queue = self._chan.queue_declare(
            exclusive=True
        ).method.queue
        self._chan.basic_consume(
            self._callback,
            self._callback_queue,
            no_ack=True
        )

    def _callback(self, ch, meth, prop, body):
        if prop.correlation_id in self._response:
            self._response[prop.correlation_id] = body
