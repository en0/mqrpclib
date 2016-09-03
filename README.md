mqrpclib is a framework to build decentralized and highly available
destributed systems. It enables developers to rapidly build microservice in
python using [RabbitMQ](https://www.rabbitmq.com/) backend.


## Key Features:
- Simple service creation and publishing of functions.
- Flexable proxy base classes for client librarys.
- Proxy factory for automatic client configurations.
- Built-in python help() method reflects the exposed servers interface on proxy.


## Install

```bash
pip install https://github.com/en0/mqrpclib/tarball/master
```

_[pika](https://pika.readthedocs.io/en/0.10.0/) is installed as a dependency._

## Usage

```python
""" MyService """
from mqrpclib import RpcServer
import logging

logging.basicConfig(level="CRITICAL")

def hello_v1(name=None):
    return "Hello, {}!".format(name or "world")

if __name__ == "__main__":
    srv = RpcServer.from_uri("MyService", "mqp://guest:guest@localhost/")
    srv.service_description = "Hello world service."
    srv.register("hello", "v1", hello_v1)
    srv.run()

```

```python
""" MyClient """

from mqrpclib import RpcProxy
import logging

logging.basicConfig(level="CRITICAL")

if __name__ == "__main__":
    with RpcProxyFactory.context("mqp://guest:guest@localhost/") as factory:
        MyServiceProxy = factory("MyService", "v1", with_exceptions=True)
        proxy = MyServiceProxy()
        print proxy.hello("User")

```

_Checkout the example directory for other options and more details._
