__author__ = 'adaml, Roeland Kuipers'
from setuptools import setup

setup(
    zip_safe=True,
    name='cloudify-plugin',
    version='0.1.1',
    packages=[
        'cloudstack_plugin',
        'cloudstack_exoscale_plugin'
    ],
    license='Apache License 2.0',
    description='Cloudify plugin for the Cloudstack cloud infrastructure.',
    dependency_links=[
        'http://github.com/boul/libcloud/archive/trunk.zip#egg=apache-libcloud-0.15.1'
    ],
    install_requires=[
        "cloudify-plugins-common",
        "cloudify-plugins-common>=3.0",
        "apache-libcloud==0.15.1"
    ]
)
