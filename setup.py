__author__ = 'adaml'
from setuptools import setup

PLUGINS_COMMON_VERSION = "3.0"
PLUGINS_COMMON_BRANCH = "develop"
PLUGINS_COMMON = "https://github.com/cloudify-cosmo/" \
                 "cloudify-plugins-common/tarball/{0}".format(
    PLUGINS_COMMON_BRANCH)

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
        "apache-libcloud>=0.14.1"
    ],
    dependency_links=["{0}#egg=cloudify-plugins-common-{1}"
                          .format(PLUGINS_COMMON, PLUGINS_COMMON_VERSION)]
)
