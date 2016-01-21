from setuptools import setup
from mqrpclib.version import *

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    packages=["mqrpclib"],
    install_requires=['pika'],
    description="Remote Procedure Call using RabbitMQ",
    author=AUTHOR,
    author_email=EMAIL,
    url="https://github.com/en0/mqrpclib"
)
