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
from cloudify.decorators import operation
from libcloud.compute.types import Provider
from cloudstack_plugin.cloudstack_common import get_cloud_driver
CLOUDSTACK_ID_PROPERTY =

__author__ = 'adaml'


def _get_server_from_context(ctx):
    server = {
        'name': ctx.node_id.replace('_', '-')
    }
    server.update(copy.deepcopy(ctx.properties['server']))
    return server

@operation
def create(ctx, **kwargs):

    ctx.logger.info("initializing {0} cloud driver"
                    .format(Provider.CLOUDSTACK))
    cloud_driver = get_cloud_driver(ctx)
    #Change to debug level
    ctx.logger.info('reading server config from context')
    server_config = _get_server_from_context(ctx)

    name = server_config['name']
    image_id = server_config['image_id']
    size_name = server_config['size']
    keypair_name = server_config['keypair_name']
    default_security_group = server_config.get(['default_security_group'][0], None)
    default_network = server_config.get(['default_network'][0], None)
    ip_address = server_config.get(['ip_address'][0], None)

    ctx.logger.info('getting required size {0}'.format(size_name))
    sizes = [size for size in cloud_driver.list_sizes() if size.name
                                                          == size_name]
    if sizes is None:
        raise RuntimeError(
            'Could not find size with name {0}'.format(size_name))
    size = sizes[0]

    ctx.logger.info('getting required image with ID {0}'.format(image_id))
    images = [template for template in cloud_driver.list_images()
              if image_id == template.id]
    if images is None:
        raise RuntimeError('Could not find image with ID {0}'.format(image_id))
    image = images[0]

    if default_network is None:
        if default_security_group is None:
            raise RuntimeError("We need either a default_security_group or default_network, "
                               "none specified")

    if default_network is not None:
        if default_security_group is not None:
            raise RuntimeError("We need either a default_security_group or default_network, "
                               "both are specified")

    if default_network is not None:
        ctx.logger.info('Creating this VM in default_network:'.format(default_network))
        ctx.logger.info("Creating VM with the following details: {0}".format(
            server_config))
        _create_in_network(ctx=ctx,
                           cloud_driver=cloud_driver,
                           name=name,
                           image=image,
                           size=size,
                           keypair_name=keypair_name,
                           default_network_name=default_network,
                           ip_address=ip_address)

    if default_security_group is not None:
        ctx.logger.info('Creating this VM in default_security_group.'.format(default_security_group))
        ctx.logger.info("Creating VM with the following details: {0}".format(
            server_config))
        _create_in_security_group(ctx=ctx,
                                  cloud_driver=cloud_driver,
                                  name=name,
                                  image=image,
                                  size=size,
                                  keypair_name=keypair_name,
                                  default_security_group_name=default_security_group,
                                  ip_address=ip_address)


@operation
def _create_in_network(ctx, cloud_driver, name, image, size, keypair_name,
                       default_network_name, ip_address=None):

    # ctx.logger.info("initializing {0} cloud driver"
    #                 .format(Provider.CLOUDSTACK))
    # cloud_driver = get_cloud_driver(ctx)
    # #Change to debug level
    # ctx.logger.info('reading server config from context')
    # server_config = _get_server_from_context(ctx)
    #
    # name = server_config['name']
    # image_id = server_config['image_id']
    # size_name = server_config['size']
    # keypair_name = server_config['keypair_name']
    # #security_groups = server_config['security_groups']
    # networks = server_config['networks']
    # ipaddress = server_config['ip_address']

    network_list = cloud_driver.ex_list_networks()

    nets = [net for net in network_list if net.name in default_network_name]

    for net in nets:
        ctx.logger.info('id: {0} name: {1}'.format(net.id, net.name))

    node = cloud_driver.create_node(name=name,
                                    image=image,
                                    size=size,
                                    ex_keyname=keypair_name,
                                    networks=nets,
                                    ex_ip_address=ip_address,
                                    ex_start_vm=False)
    ctx.logger.info(
        'vm {0} was created successfully'.format(
            node.name))

    ctx['instance_id'] = node.id

@operation
def _create_in_security_group(ctx, cloud_driver, name, image, size, keypair_name,
                              default_security_group_name, ip_address=None):

    # ctx.logger.info("initializing {0} cloud driver".format(Provider.EXOSCALE))
    # cloud_driver = get_cloud_driver(ctx)
    #
    # ctx.logger.info('reading server config from context')
    # server_config = _get_server_from_context(ctx)
    #
    # name = server_config['name']
    # image_id = server_config['image_id']
    # size_name = server_config['size']
    # keypair_name = server_config['keypair_name']
    # security_groups = server_config['security_groups']

    # ctx.logger.info('getting required size {0}'.format(size_name))
    # sizes = [size for size in cloud_driver.list_sizes() if size.name == size_name]  # NOQA
    # if sizes is None:
    #     raise RuntimeError(
    #         'Could not find size with name {0}'.format(size_name))
    # size = sizes[0]
    #
    # ctx.logger.info('getting required image with ID {0}'.format(image_id))
    # images = [image for image in cloud_driver.list_images() if image_id == image.id]  # NOQA
    # if images is None:
    #     raise RuntimeError('Could not find image with ID {0}'.format(image_id))
    # image = images[0]

    # ctx.logger.info(
    #     "creating server vm with the following details: {0}".format(
    #         server_config))

    node = cloud_driver.create_node(name=name,
                                    image=image,
                                    size=size,
                                    ex_keyname=keypair_name,
                                    ex_security_groups=default_security_group_name,
                                    ex_start_vm=False,
                                    ex_ipaddress=ip_address)

    ctx.logger.info(
        'vm {0} was started successfully {1}'.format(
            node.name, server_config))

    ctx['instance_id'] = node.id


@operation
def start(ctx, **kwargs):
    ctx.logger.info("initializing {0} cloud driver"
                    .format(Provider.CLOUDSTACK))
    cloud_driver = get_cloud_driver(ctx)

    instance_id = ctx.runtime_properties['instance_id']
    if instance_id is None:
        raise RuntimeError(
            'could not find node ID in runtime context: {0} '
            .format(instance_id))

    ctx.logger.info('getting node with ID: {0} '.format(instance_id))
    node = _get_node_by_id(cloud_driver, instance_id)
    if node is None:
        raise RuntimeError('could not find node with ID {0}'
                           .format(instance_id))

    ctx.logger.info('starting node with details {0}'.format(node))
    cloud_driver.ex_start(node)

@operation
def delete(ctx, **kwargs):

    ctx.logger.info("initializing {0} cloud driver"
                    .format(Provider.CLOUDSTACK))
    cloud_driver = get_cloud_driver(ctx)

    instance_id = ctx['instance_id']
    if instance_id is None:
        raise NameError('could not find node ID in runtime context: {0} '
                        .format(instance_id))

    ctx.logger.info('getting node with ID: {0} '.format(instance_id))
    node = _get_node_by_id(cloud_driver, instance_id)
    if node is None:
        raise NameError('could not find node with ID: {0} '
                        .format(instance_id))

    ctx.logger.info('destroying vm with details: {0}'.format(node))
    cloud_driver.destroy_node(node)


@operation
def stop(ctx, **kwargs):

    ctx.logger.info("initializing {0} cloud driver"
                    .format(Provider.CLOUDSTACK))
    cloud_driver = get_cloud_driver(ctx)

    instance_id = ctx.runtime_properties['instance_id']
    if instance_id is None:
        raise RuntimeError(
            'could not find node ID in runtime context: {0} '
            .format(instance_id))

    ctx.logger.info('getting node with ID: {0} '.format(instance_id))
    node = _get_node_by_id(cloud_driver, instance_id)
    if node is None:
        raise RuntimeError('could not find node with ID {0}'
                           .format(instance_id))

    ctx.logger.info('stopping node with details {0}'.format(node))
    cloud_driver.ex_stop(node)


def _get_node_by_id(cloud_driver, instance_id):

    nodes = [node for node in cloud_driver.list_nodes() if instance_id
                                                          == node.id]
    if nodes is None:
        raise RuntimeError('could not find node by ID {0}'.format(instance_id))
        return None

    return nodes[0]


@operation
def get_state(ctx, **kwargs):

    ctx.logger.info("initializing {0} cloud driver"
                    .format(Provider.CLOUDSTACK))
    cloud_driver = get_cloud_driver(ctx)

    instance_id = ctx.runtime_properties['instance_id']

    ctx.logger.info('getting node with ID {0}'.format(instance_id))
    node = _get_node_by_id(cloud_driver, instance_id)
    if node is None:
        return False

    ctx.runtime_properties['ip'] = node.private_ips[0]
    ctx.runtime_properties['ip_address'] = node.private_ips[0]
    ctx.logger.info(
        'instance started successfully with IP {0}'
        .format(ctx.runtime_properties['ip']))
    return True

@operation
def connect_network(ctx, **kwargs):

    instance_id = ctx.runtime_properties['instance_id']
    network_id = ctx.related.runtime_properties['network_id']

    ctx.logger.info('Adding a NIC to VM-ID {0} in Network-ID {1}'.format(instance_id, network_id))

    cloud_driver = get_cloud_driver(ctx)
    nodes = cloud_driver.list_nodes(instance_id)

    network = [net for net in cloud_driver.ex_list_networks() if
               net.id == network_id ][0]
    instance = [node for node in cloud_driver.list_nodes() if
                node.id == network_id][0]

    ctx.logger.info('Adding a NIC to VM {0} in Network {1}'.format(instance, network))

    result = cloud_driver.ex_add_nic_to_vm(instance, network)

    ctx.runtime_properties['nic_id'] = result.id

    return True

    # if is_external_relationship(ctx):
    #     ctx.logger.info('Validating external network and VM '
    #                     'are associated')
    #     cloud_driver = get_cloud_driver(ctx)
    #     nodes = cloud_driver.list_nodes(server_id)
    #     if [sg for sg in server.list_security_group() if sg.id ==
    #             security_group_id]:
    #         return
    #     raise NonRecoverableError(
    #         'Expected external resources server {0} and security-group {1} to '
    #         'be connected'.format(server_id, security_group_id))
    #
    # server = nova_client.servers.get(server_id)
    # server.add_security_group(security_group_id)