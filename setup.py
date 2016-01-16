from setuptools import setup

setup(
    name="mqrpclib",
    version="0.1.0",
    packages=["mqrpclib"],
    install_requires=['pika'],
    description="Remote Procedure Call using RabbitMQ",
    author="Ian Laird",
    author_email="en0@mail.com",
    url="https://github.com/en0/mqrpclib"
)
