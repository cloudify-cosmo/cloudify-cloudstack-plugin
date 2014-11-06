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

from cloudstack_plugin.cloudstack_common import(
    get_cloud_driver,
    get_location,
    get_resource_id,
    COMMON_RUNTIME_PROPERTIES_KEYS,
    CLOUDSTACK_ID_PROPERTY,
    CLOUDSTACK_TYPE_PROPERTY,
    CLOUDSTACK_NAME_PROPERTY
    )

VPC_CLOUDSTACK_TYPE = 'vpc'

# Runtime properties
RUNTIME_PROPERTIES_KEYS = COMMON_RUNTIME_PROPERTIES_KEYS

__author__ = 'jedeko, boul'


@operation
def create(ctx, **kwargs):
    """ Create vpc with rules.
    """

    cloud_driver = get_cloud_driver(ctx)

    vpc = {
        'description': None,
        'name': get_resource_id(ctx, VPC_CLOUDSTACK_TYPE),
    }

    ctx.logger.debug('reading vpc configuration.')
    vpc.update(ctx.node.properties['network'])

    vpc_name = vpc['name']
    cidr = vpc['cidr']
    zone = vpc['zone']
    location = get_location(cloud_driver, zone)
    vpcoffer = vpc['service_offering']
    vpc_offering = get_vpc_offering(cloud_driver, vpcoffer)

    ctx.logger.info('Creating VPC {0}'.format(vpc_name))

    #ctx.runtime_properties['vpc_id'] = ctx.node.properties

    if not vpc_exists(cloud_driver, vpc_name):
        ctx.logger.info('creating vpc: {0}'.format(vpc_name))

        vpc = cloud_driver.ex_create_vpc(
            cidr=cidr,
            name=vpc_name,
            display_text=vpc_name,
            vpc_offering=vpc_offering,
            zone_id=location.id)
    else:
        ctx.logger.info('Using existing vpc network {0}'.
                        format(vpc_name))
        vpc = get_vpc(cloud_driver, vpc_name)

    ctx.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY] = vpc.id
    ctx.instance.runtime_properties[CLOUDSTACK_NAME_PROPERTY] = \
        vpc.name
    ctx.instance.runtime_properties[CLOUDSTACK_TYPE_PROPERTY] = \
        VPC_CLOUDSTACK_TYPE


@operation
def delete(ctx, **kwargs):

    vpc_name = ctx.instance.runtime_properties['vpc_name']
    cloud_driver = get_cloud_driver(ctx)
    vpc = get_vpc(cloud_driver, vpc_name)

    try:
        cloud_driver.ex_delete_vpc(vpc)
    except:
        ctx.logger.warn(
            'vpc {0} may not have been deleted'
                .format(ctx.instance.runtime_properties['vpc_name']))
        pass


# def get_vpc(cloud_driver, vpc_name):
#     vpcs = [vpc for vpc in cloud_driver
#         .ex_list_vpcs() if vpc.name == vpc_name]
#
#     if vpcs.__len__() == 0:
#         return None
#     return vpcs[0]

# already in cloudify-comming
# def get_location(cloud_driver, location_name):
#
#     locations = [location for location in cloud_driver
#         .list_locations() if location.name == location_name]
#     if locations.__len__() == 0:
#         return None
#     return locations[0]


def get_vpc_offering(cloud_driver, vpcoffer_name):
    vpcoffers = [offer for offer in cloud_driver
        .ex_list_vpc_offerings() if offer.name == vpcoffer_name]
    if vpcoffers.__len__() == 0:
        return None
    return vpcoffers[0]

# TODO let's call this from operation directly, seems like double code.
def _create_egr_rules(cloud_driver, network_id, cidr_list, protocol,
                      start_port, end_port):

    cloud_driver.ex_create_egress_firewall_rule(
        network_id=network_id,
        cidr_list=cidr_list,
        protocol=protocol,
        start_port=start_port,
        end_port=end_port)


def get_vpc(cloud_driver, vpc_name):
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


def vpc_exists(cloud_driver, vpc_name):
    exists = get_vpc(cloud_driver, vpc_name)
    if not exists:
        return False
    return True