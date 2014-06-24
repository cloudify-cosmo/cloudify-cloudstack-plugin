__author__ = 'adaml'
from setuptools import setup

setup(
    zip_safe=True,
    name='cloudify-exoscale-plugin',
    version='0.1.0',
    packages=[
        'cloudstack_plugin'
    ],
    license='LICENSE',
    description='Cloudify plugin for the Exoscale cloud infrastructure.',
    install_requires=[
        "cloudify-plugins-common",
        "apache-libcloud>=0.14.1",
        'cloudify-plugins-common==3.0',
    ],
)
