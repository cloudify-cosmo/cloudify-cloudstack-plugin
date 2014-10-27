########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.
import copy
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import libcloud.security

__author__ = 'uri1803, boul'


def _get_auth_from_context(ctx):
    auth_config = {}
    auth_config.update(copy.deepcopy(ctx.properties['cloudstack_config']))
    return auth_config


def get_cloud_driver(ctx):
    auth_config = _get_auth_from_context(ctx)
    api_key = auth_config['cs_api_key']
    api_secret_key = auth_config['cs_secret_key']
    api_url = auth_config['cs_api_url']
    driver = get_driver(Provider.CLOUDSTACK)
    libcloud.security.VERIFY_SSL_CERT = False
    return driver(key=api_key, secret=api_secret_key,url=api_url)


def get_node_by_id(ctx, cloud_driver, instance_id):

    nodes = [node for node in cloud_driver.list_nodes() if
             instance_id == node.id]

    if not nodes:
        ctx.logger.info('could not find node by ID {0}'.format(instance_id))
        return None

    return nodes[0]


def get_network_by_id(ctx, cloud_driver, network_id):

    networks = [network for network in cloud_driver.ex_list_networks() if
                network_id == network.id]

    if not networks:
        ctx.logger.info('could not find network by ID {0}'.format(network_id))
        return None

    return networks[0]


def get_nic_by_node_and_network_id(ctx, cloud_driver, node, network_id):

    #node = _get_node_by_id(cloud_driver, node_id)
    #network = _get_network_by_id(cloud_driver, network_id)

    nics = [nic for nic in cloud_driver.ex_list_nics(node) if
            network_id == nic.network_id]

    if not nics:
        ctx.logger.info('could not find nic by node_id {0} and network_id {1}'
                        .format(node.id, network_id))
        return None

    return nics[0]