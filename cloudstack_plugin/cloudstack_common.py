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
import os
import json
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import libcloud.security
from cloudify import context

__author__ = 'uri1803, boul'

# properties
USE_EXTERNAL_RESOURCE_PROPERTY = 'use_external_resource'

# runtime properties
CLOUDSTACK_ID_PROPERTY = 'external_id'  # resource's cloudstack id
CLOUDSTACK_TYPE_PROPERTY = 'external_type'  # resource's cloudstack type
CLOUDSTACK_NAME_PROPERTY = 'external_name'  # resource's cloudstack name

# runtime properties which all types use
COMMON_RUNTIME_PROPERTIES_KEYS = [CLOUDSTACK_ID_PROPERTY,
                                  CLOUDSTACK_TYPE_PROPERTY,
                                  CLOUDSTACK_NAME_PROPERTY]


def _get_auth_from_context(ctx):

    if ctx.type == context.NODE_INSTANCE:
        config = ctx.node.properties.get('cloudstack_config')
    elif ctx.type == context.RELATIONSHIP_INSTANCE:
        config = ctx.source.node.properties.get('cloudstack_config')
        if not config:
            config = ctx.target.node.properties.get('cloudstack_config')
    else:
        config = None

    #auth_config = config
    #auth_config.update(copy.deepcopy(
    #    ctx.node.properties['cloudstack_config']))
    return config


def get_cloud_driver(ctx):
    auth_config = _get_auth_from_context(ctx)
    api_key = auth_config['cs_api_key']
    api_secret_key = auth_config['cs_secret_key']
    api_url = auth_config['cs_api_url']
    driver = get_driver(Provider.CLOUDSTACK)
    libcloud.security.VERIFY_SSL_CERT = False
    return driver(key=api_key, secret=api_secret_key,url=api_url)


class Config(object):

    CLOUDSTACK_CONFIG_PATH_ENV_VAR = 'CLOUDSTACK_CONFIG_PATH'
    CLOUDSTACK_CONFIG_PATH_DEFAULT_PATH = '~/cloudstack_config.json'

    def get(self):
        static_config = self._build_config_from_env_variables()
        env_name = self.CLOUDSTACK_CONFIG_PATH_ENV_VAR
        default_location_tpl = self.CLOUDSTACK_CONFIG_PATH_DEFAULT_PATH
        default_location = os.path.expanduser(default_location_tpl)
        config_path = os.getenv(env_name, default_location)
        try:
            with open(config_path) as f:
                Config.update_config(static_config, json.loads(f.read()))
        except IOError:
            pass
        return static_config

    @staticmethod
    def _build_config_from_env_variables():
        cfg = dict()

        def take_env_var_if_exists(cfg_key, env_var):
            if env_var in os.environ:
                cfg[cfg_key] = os.environ[env_var]

        take_env_var_if_exists('cs_api_key', 'CS_API_KEY')
        take_env_var_if_exists('cs_api_secret', 'CS_API_SECRET')
        take_env_var_if_exists('cs_api_url', 'CS_API_URL')

        return cfg

    @staticmethod
    def update_config(overridden_cfg, overriding_cfg):
        """ this method is like dict.update() only that it doesn't override
        with (or set new) empty values (e.g. empty string) """
        for k, v in overriding_cfg.iteritems():
            if v:
                overridden_cfg[k] = v


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


def get_public_ip_by_id(ctx, cloud_driver, public_ip_id):

    public_ips = [pubip for pubip in cloud_driver.ex_list_public_ips() if
                  public_ip_id == pubip.id]

    if not public_ips:
        ctx.logger.info('could not find public_ip by id {0}'
                        .format(public_ip_id))
        return None

    return public_ips[0]


def get_portmaps_by_node_id(ctx, cloud_driver, node_id):

    portmaps = [portmap for portmap in
                cloud_driver.ex_list_port_forwarding_rules()
                if node_id == portmap.node.id]

    return portmaps


def get_floating_ip_by_id(ctx, cloud_driver, floating_ip_id):

    fips = [fip for fip in cloud_driver.ex_list_public_ips() if
            floating_ip_id == fip.id]

    if not fips:
        ctx.logger.info('could not find floating ip by ID {0}'.
                        format(floating_ip_id))
        return None

    return fips[0]


def get_resource_id(ctx, type_name):
    if ctx.node.properties['resource_id']:
        return ctx.node.properties['resource_id']
    return "{0}_{1}_{2}".format(type_name, ctx.deployment.id, ctx.instance.id)


def network_exists(cloud_driver, network_name):
    exists = get_network(cloud_driver, network_name)
    if not exists:
        return False
    return True


def get_network(cloud_driver, network_name):
    networks = [net for net in cloud_driver
        .ex_list_networks() if net.name == network_name]

    if networks.__len__() == 0:
        return None
    return networks[0]


def get_location(cloud_driver, location_name):
    locations = [location for location in cloud_driver
        .list_locations() if location.name == location_name]
    if locations.__len__() == 0:
        return None
    return locations[0]


def get_network_offering(cloud_driver, netoffer_name):
    netoffers = [offer for offer in cloud_driver
        .ex_list_network_offerings() if offer.name == netoffer_name]
    if netoffers.__len__() == 0:
        return None
    return netoffers[0]


def get_vpc_id(cloud_driver, vpc_name):
    vpcs = [vpc for vpc in cloud_driver
        .ex_list_vpcs() if vpc.name == vpc_name]
    if vpcs.__len__() == 0:
        return None
    return vpcs[0]


def create_acl_list(cloud_driver, name, vpc_id, network_id):
    acllist = cloud_driver.ex_create_network_acllist(
        name=name,
        vpc_id=vpc_id,
        description=name)

    # Replace the newly created ACL list on to the network
    cloud_driver.ex_replace_network_acllist(
        acl_id=acllist.id,
        network_id=network_id)

    return acllist


def create_acl(cloud_driver, protocol, acl_id,
               cidr_list, start_port, end_port, traffic_type):
    acl = cloud_driver.ex_create_network_acl(
        protocol=protocol,
        acl_id=acl_id,
        cidr_list=cidr_list,
        start_port=start_port,
        end_port=end_port,
        traffic_type=traffic_type)
    return acl