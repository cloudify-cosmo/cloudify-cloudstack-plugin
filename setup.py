__author__ = 'adaml'
from setuptools import setup

setup(
    zip_safe=True,
    name='cloudify-plugin',
    version='0.1.0',
    packages=[
        'cloudstack_plugin',
        'cloudstack_exoscale_plugin'
    ],
    license='LICENSE',
    description='Cloudify plugin for the Cloudstack cloud infrastructure.',
    dependency_links=[
        'http://github.com/boul/libcloud/archive/trunk.zip#egg=apache-libcloud'
    ],
    install_requires=[
        "cloudify-plugins-common",
        "cloudify-plugins-common>=3.0",
        "apache-libcloud"
    ]
)
