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

from cloudify.decorators import operation

from cloudstack_plugin.cloudstack_common import get_cloud_driver


__author__ = 'uri1803'


@operation
def create(ctx, **kwargs):
    """ Create network with rules.
    """

    cloud_driver = get_cloud_driver(ctx)

    network = {
        'description': None,
        'name': ctx.node_id,
    }

    ctx.logger.debug('reading network configuration.')
    network.update(ctx.properties['network'])

    network_name = network['name']
    zone = network['zone']
    location = get_location(cloud_driver, zone)
    netoffer = network['service_offering']
    network_offering = get_network_offering(cloud_driver, netoffer)
    firewall_config = ctx.properties['firewall']['default']

    # if network['vpc']:
    #     vpc = get_vpc_id(cloud_driver, network['vpc'])
    #     ctx.logger.info('DEBUG: VPC id: '.format(vpc.id))
    vpc = False

    ctx.logger.info('Current node {0}{1}'.format(ctx.node_id, ctx.properties))

    ctx['network_id'] = ctx.node_id

    if not _network_exists(cloud_driver, network_name):

        if vpc:
            ctx.logger.info('creating network: {0} in VPC with ID: {1}'.format(network_name, vpc.id))

            net = cloud_driver.ex_create_network(
                display_text=network_name,
                name=network_name,
                network_offering=network_offering,
                location=location,
                gateway=network['gateway'],
                netmask=network['netmask'],
                vpc_id=vpc.id)
        else:
            ctx.logger.info('creating network: {0}'.format(network_name))

            net = cloud_driver.ex_create_network(
                display_text=network_name,
                name=network_name,
                network_offering=network_offering,
                location=location)

        # Create ACL for the network if it's is part of a VPC
        if vpc:

            acl_list = create_acl_list(cloud_driver, vpc.name, vpc.id, net.id)

            # Creat ingress ACL rules in ACLlist
            acl_ingress_ports = firewall_config['ingress']['ports']
            acl_ingress_protocol = firewall_config['ingress']['protocol']
            acl_ingress_cidr = firewall_config['ingress']['cidr']

            for port in acl_ingress_ports:
                create_acl(cloud_driver, acl_ingress_protocol, acl_list.id,
                           acl_ingress_cidr, port, port, "ingress")

             # Creat egress ACL rules in ACLlist
            acl_egress_ports = firewall_config['egress']['ports']
            acl_egress_protocol = firewall_config['egress']['protocol']
            acl_egress_cidr = firewall_config['egress']['cidr']

            for port in acl_egress_ports:
                create_acl(cloud_driver, acl_egress_protocol, acl_list.id,
                           acl_egress_cidr, port, port, "egress")

        else:
            # Create firewall rules for new network
            egress_rules = firewall_config['egress']
            egr_ports = egress_rules['ports']

            for port in egr_ports:
                _create_egr_rules(cloud_driver, net.id, egress_rules['cidr'],
                                  egress_rules['protocol'],
                                  port, port)

    else:
        ctx.logger.info('using existing management network {0}'.
                        format(network_name))
        net = get_network(cloud_driver, network_name)

    ctx['network_id'] = net.id
    ctx['network_name'] = net.name


@operation
def delete(ctx, **kwargs):

    network_name = ctx.runtime_properties['network_name']
    cloud_driver = get_cloud_driver(ctx)
    network = get_network(cloud_driver, network_name)

    try:

        cloud_driver.ex_delete_network(network)
    except:
        ctx.logger.warn(
            'network {0} may not have been deleted'
                .format(ctx.runtime_properties['network_name']))
        pass


def _network_exists(cloud_driver, network_name):
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


@operation
def _create_egr_rules(cloud_driver, network_id, cidr_list, protocol,
                      start_port, end_port):

    cloud_driver.ex_create_egress_firewall_rule(
        network_id=network_id,
        cidr_list=cidr_list,
        protocol=protocol,
        start_port=start_port,
        end_port=end_port)


# def _add_ingress_rule(ctx, node_name, protocol,
#                       cidr_list, start_port, end_port=None):
#
#     network_name = ctx.runtime_properties['network_name']
#     cloud_driver = get_cloud_driver(ctx)
#
#     ctx.logger.debug(
#         'creating port forward rule for {0} with details {1}'
#         .format(network_name, locals().values()))
#
#     cloud_driver.ex_create_port_forwarding_rule(
#         address=ip_address,
#         private_port=privateport,
#         public_port=publicport,
#         node=node,
#         protocol=protocol,
#         openfirewall=False)
