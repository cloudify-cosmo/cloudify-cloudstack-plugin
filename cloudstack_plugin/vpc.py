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
    get_vpc, vpc_exists)



__author__ = 'jedeko, boul'


@operation
def create(ctx, **kwargs):
    """ Create vpc with rules.
    """

    cloud_driver = get_cloud_driver(ctx)

    vpc = {
        'description': None,
        'name': ctx.node_id,
    }

    ctx.logger.debug('reading vpc configuration.')
    vpc.update(ctx.node.properties['network'])

    vpc_name = vpc['name']
    cidr = vpc['cidr']
    zone = vpc['zone']
    location = get_location(cloud_driver, zone)
    vpcoffer = vpc['service_offering']
    vpc_offering = get_vpc_offering(cloud_driver, vpcoffer)

    ctx.logger.info('Current node {0}{1}'.format(ctx.node_id, ctx.node.properties))

    ctx['vpc_id'] = ctx.node.properties

    if not vpc_exists(cloud_driver, vpc_name):
        ctx.logger.info('creating vpc: {0}'.format(vpc_name))

        vpc = cloud_driver.ex_create_vpc(
            cidr=cidr,
            name=vpc_name,
            display_text=vpc_name,
            vpc_offering=vpc_offering,
            zone_id=location.id)
    else:
        ctx.logger.info('using existing vpc network {0}'.
                        format(vpc_name))
        vpc = get_vpc(cloud_driver, vpc_name)

    ctx['vpc_id'] = vpc.id
    ctx['vpc_name'] = vpc.name


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