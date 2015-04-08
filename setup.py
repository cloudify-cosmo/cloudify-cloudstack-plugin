__author__ = 'adaml, boul, jedeko'
from setuptools import setup

setup(
    zip_safe=True,
    name='cloudify-cloudstack-plugin',
    version='3.2rc',
    packages=[
        'cloudstack_plugin',
        'cloudstack_exoscale_plugin'
    ],
    license='Apache License 2.0',
    description='Cloudify plugin for the Cloudstack cloud infrastructure.',

    install_requires=[
        "cloudify-plugins-common",
        "cloudify-plugins-common>=3.2rc",
        "apache-libcloud>=0.16"
    ]
)
