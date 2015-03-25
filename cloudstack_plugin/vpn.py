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
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from cloudify import ctx
from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError

from cloudstack_plugin.cloudstack_common import (
    CLOUDSTACK_ID_PROPERTY,
    CLOUDSTACK_TYPE_PROPERTY,
    COMMON_RUNTIME_PROPERTIES_KEYS,
    USE_EXTERNAL_RESOURCE_PROPERTY,
    get_cloud_driver,
)
from cloudstack_plugin.vpc import get_vpc_by_id


RUNTIME_PROPERTIES_KEYS = COMMON_RUNTIME_PROPERTIES_KEYS

VPC_ROUTER_STATE_RUNNING = 'Running'

VPN_GATEWAY_CLOUDSTACK_TYPE = 'VpnGateway'
VPN_CUSTOMER_GATEWAY_CLOUDSTACK_TYPE = 'VpnCustomerGateway'
VPN_CONNECTION_CLOUDSTACK_TYPE = 'VpnConnection'


def get_vpn_gateway(cloud_driver, id_):
    """
    Returns the VPN Gateway.
    """
    vpn_gateways = cloud_driver.ex_list_vpn_gateways()

    if not len(vpn_gateways):
        return

    for obj in vpn_gateways:
        if id_ == obj.id:
            return obj


def get_vpn_gateway_by_vpc(cloud_driver, vpc_id):
    """
    Returns the VPN Gateway for a VPC.
    """
    for obj in cloud_driver.ex_list_vpn_gateways():
        if vpc_id == obj.vpc_id:
            return obj


def get_vpn_customer_gateway(cloud_driver, id_):
    """
    Returns the VPN Customer Gateway.
    """
    vpn_customer_gateways = cloud_driver.ex_list_vpn_customer_gateways()

    if not len(vpn_customer_gateways):
        return

    for obj in vpn_customer_gateways:
        if id_ == obj.id:
            return obj


def get_vpn_connections(cloud_driver):
    """
    Returns VPN Connections.
    """
    return cloud_driver.ex_list_vpn_connections()


def get_vpn_connection(cloud_driver, id_):
    """
    Returns the VPN Connection.
    """
    vpn_connections = get_vpn_connections(cloud_driver)

    if not len(vpn_connections):
        return

    for obj in vpn_connections:
        if id_ == obj.id:
            return obj


def get_vpn_connection_by_gateways(cloud_driver, vpn_gateway_id,
                                   vpn_customer_gateway_id):
    vpn_connections = cloud_driver.ex_list_vpn_connections()

    if not len(vpn_connections):
        return

    for obj in vpn_connections:
        if ((obj.vpn_customer_gateway_id == vpn_customer_gateway_id) and
                (obj.vpn_gateway_id == vpn_gateway_id)):
            return obj


def vpn_gateway_exists(cloud_driver, id_):
    """
    Returns if the VPN Gateway exists.
    """
    if get_vpn_gateway(cloud_driver, id_):
        return True

    return False


def vpn_gateway_exists_for_vpc(cloud_driver, vpc_id):
    """
    Returns if the VPN Gateway exists for the VPC.
    """
    vpn_gateway = get_vpn_gateway_by_vpc(cloud_driver, vpc_id)

    if vpn_gateway:
        return True

    return False


def vpn_customer_gateway_exists(cloud_driver, id_):
    """
    Returns if the VPN Customer Gateway exists.
    """
    if get_vpn_customer_gateway(cloud_driver, id_):
        return True

    return False


def vpn_connection_exists(cloud_driver, id_):
    """
    Returns if the VPN Connection exists.
    """
    if get_vpn_connection(cloud_driver, id_):
        return True

    return False


def get_vpc_routers(cloud_driver, vpc_id):
    """
    Returns the list of VPC Router objects.
    """
    vpc_routers = cloud_driver.ex_list_routers(vpc_id=vpc_id)

    if vpc_routers:
        return vpc_routers


def are_vpc_routers_running(cloud_driver, vpc_id):
    """
    Returns True if the routers are running, False otherwise.
    """
    vpc_routers = get_vpc_routers(cloud_driver, vpc_id)

    if not vpc_routers:
        return

    is_running = all(
        [obj.state == VPC_ROUTER_STATE_RUNNING for obj in vpc_routers])

    if is_running:
        return True

    return False


@operation
def create_vpn_gateway(**kwargs):
    """
    Creates a VPN Gateway for a VPC.
    """
    cloud_driver = get_cloud_driver(ctx)

    vpc_id = ctx.target.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY]
    vpc = get_vpc_by_id(cloud_driver, vpc_id)

    if not vpc:
        raise NonRecoverableError('Could not find VPC id={0}'.format(vpc_id))

    if not are_vpc_routers_running(cloud_driver, vpc.id):
        return ctx.operation.retry(
            message='VPC Routers not running, waiting...', retry_after=5)

    exists = vpn_gateway_exists_for_vpc(cloud_driver, vpc_id)
    use_external = ctx.source.node.properties[USE_EXTERNAL_RESOURCE_PROPERTY]

    if (not exists) and (not use_external):
        vpn_gateway = cloud_driver.ex_create_vpn_gateway(vpc)

        ctx.logger.info(
            'Created VPN Gateway id={0} vpc_id={1}'.format(
                vpn_gateway.id, vpc_id))

    elif exists and use_external:
        vpn_gateway = get_vpn_gateway_by_vpc(cloud_driver, vpc_id)

        ctx.logger.info('Using VPN Gateway id={0}'.format(vpn_gateway.id))

    elif exists and (not use_external):
        raise NonRecoverableError(
            'VPN Gateway already exists vpc_id={0}'.format(vpc_id))

    elif (not exists) and use_external:
        raise NonRecoverableError(
            'Could not find VPN Gateway vpc_id={0}'.format(vpc_id))

    ctx.source.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY] = \
        vpn_gateway.id

    ctx.source.instance.runtime_properties[CLOUDSTACK_TYPE_PROPERTY] = \
        VPN_GATEWAY_CLOUDSTACK_TYPE


@operation
def delete_vpn_gateway(**kwargs):
    """
    Deletes a VPN Gateway for a VPC.
    """
    cloud_driver = get_cloud_driver(ctx)

    id_ = ctx.source.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY]
    vpn_gateway = get_vpn_gateway(cloud_driver, id_)

    if not vpn_gateway:
        raise NonRecoverableError(
            'Could not find VPN Gateway id={0}'.format(id_))

    use_external = ctx.source.node.properties[USE_EXTERNAL_RESOURCE_PROPERTY]

    if not use_external:
        vpn_gateway.delete()

        ctx.logger.info(
            'Deleted VPN Gateway id={0} vpc_id={1}'.format(
                id_, vpn_gateway.vpc_id))
    else:
        ctx.logger.info(
            'Did not delete VPN Gateway id={0} vpc_id={1}'.format(
                id_, vpn_gateway.vpc_id))


@operation
def create_vpn_customer_gateway(**kwargs):
    """
    Creates a VPN Customer Gateway.
    """
    cloud_driver = get_cloud_driver(ctx)

    vpn_gateway = get_vpn_gateway(
        cloud_driver,
        ctx.target.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY],
    )

    if not vpn_gateway:
        raise NonRecoverableError('Could not find VPN Gateway id={0}'.format(
            ctx.target.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY]))
    try:
        id_ = ctx.source.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY]
    except KeyError:
        id_ = None

    exists = vpn_customer_gateway_exists(cloud_driver, id_)
    use_external = ctx.source.node.properties[USE_EXTERNAL_RESOURCE_PROPERTY]

    if (not exists) and (not use_external):
        data = {
            'cidr_list': ctx.source.node.properties['cidr_list'],
            'dpd': ctx.source.node.properties['dpd'],
            'esp_lifetime': ctx.source.node.properties['esp_lifetime'],
            'esp_policy': ctx.source.node.properties['esp_policy'],
            'gateway': vpn_gateway.public_ip,
            'ike_lifetime': ctx.source.node.properties['ike_lifetime'],
            'ike_policy': ctx.source.node.properties['ike_policy'],
            'ipsec_psk': ctx.source.node.properties['ipsec_psk'],
        }

        vpn_customer_gateway = cloud_driver.ex_create_vpn_customer_gateway(
            **data)

        ctx.logger.info(
            'Created VPN Customer Gateway id={0} vpn_gateway_id={1}'.format(
                vpn_customer_gateway.id, vpn_gateway.id))

    elif exists and use_external:
        vpn_customer_gateway = get_vpn_customer_gateway(cloud_driver, id_)

        ctx.logger.info('Using VPN Customer Gateway id={0}'.format(
            vpn_customer_gateway.id))

    elif exists and (not use_external):
        raise NonRecoverableError(
            'VPN Customer Gateway already exists id={0}'.format(id_))

    elif (not exists) and use_external:
        raise NonRecoverableError(
            'Could not find VPN Customer Gateway id={0}'.format(id_))

    ctx.source.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY] = \
        vpn_customer_gateway.id
    ctx.source.instance.runtime_properties[CLOUDSTACK_TYPE_PROPERTY] = \
        VPN_CUSTOMER_GATEWAY_CLOUDSTACK_TYPE


@operation
def delete_vpn_customer_gateway(**kwargs):
    """
    Deletes a VPN Customer Gateway.
    """
    cloud_driver = get_cloud_driver(ctx)

    id_ = ctx.source.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY]
    vpn_customer_gateway = get_vpn_customer_gateway(cloud_driver, id_)

    if not vpn_customer_gateway:
        raise NonRecoverableError(
            'Could not find VPN Customer Gateway with id={0}'.format(id_))

    use_external = ctx.source.node.properties[USE_EXTERNAL_RESOURCE_PROPERTY]

    if not use_external:
        for obj in get_vpn_connections():
            if obj.vpn_customer_gateway_id == id_:
                raise NonRecoverableError(
                    'Could not delete VPN Customer Gateway id={0} because '
                    'of VPN Connection id={1}'.format(id_, obj.id))

        vpn_customer_gateway.delete()

        ctx.logger.info('Deleted VPN Customer Gateway id={0}'.format(id_))
    else:
        ctx.logger.info(
            'Did not delete VPN Customer Gateway id={0}'.format(id_))


@operation
def create_vpn_connection(**kwargs):
    """
    Creates a VPN Connection.
    """
    cloud_driver = get_cloud_driver(ctx)

    vpn_gateway_id = kwargs.get('vpn_gateway_id')
    vpn_customer_gateway_id = kwargs.get('vpn_customer_gateway_id')

    vpn_gateway = get_vpn_gateway(cloud_driver, vpn_gateway_id)

    if not vpn_gateway:
        raise NonRecoverableError(
            'Could not find VPN Gateway id={0}'.format(vpn_gateway_id))

    vpn_customer_gateway = get_vpn_customer_gateway(cloud_driver,
                                                    vpn_customer_gateway_id)

    if not vpn_customer_gateway:
        raise NonRecoverableError(
            'Could not find VPN Customer Gateway id={0}'.format(
                vpn_customer_gateway_id))

    try:
        id_ = ctx.node.properties['resource_id']
    except KeyError:
        id_ = None

    exists = get_vpn_connection(cloud_driver, id_)
    use_external = ctx.node.properties[USE_EXTERNAL_RESOURCE_PROPERTY]

    if (not exists) and (not use_external):
        if not are_vpc_routers_running(cloud_driver, vpn_gateway.vpc_id):
            return ctx.operation.retry(
                message='VPC Routers not running, waiting...', retry_after=5)

        vpn_connection = cloud_driver.ex_create_vpn_connection(
            vpn_customer_gateway=vpn_customer_gateway,
            vpn_gateway=vpn_gateway,
            passive=ctx.node.properties['passive'],
        )

        ctx.logger.info('Created VPN Connection id={0} for VPN Gateway '
                        'id={1} and VPN Customer Gateway id={2}'.format(
                            vpn_connection.id,
                            vpn_gateway.id,
                            vpn_customer_gateway.id,
                        ))

    elif exists and use_external:
        vpn_connection = get_vpn_connection(cloud_driver, id_)

        if not vpn_connection:
            raise NonRecoverableError(
                'Could not find VPN Connection id={0}'.format(id_))

    elif exists and (not use_external):
        raise NonRecoverableError(
            'VPN Connection id={0} already exists'.format(exists.id))

    elif (not exists) and use_external:
        raise NonRecoverableError(
            'Could not find VPN Connection id={0}'.format(id_))

    ctx.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY] = \
        vpn_connection.id
    ctx.instance.runtime_properties[CLOUDSTACK_TYPE_PROPERTY] = \
        VPN_CONNECTION_CLOUDSTACK_TYPE


@operation
def delete_vpn_connection(**kwargs):
    """
    Deletes a VPN Connection.
    """
    cloud_driver = get_cloud_driver(ctx)

    id_ = ctx.node.runtime_properties[CLOUDSTACK_ID_PROPERTY]
    vpn_connection = get_vpn_connection(cloud_driver, id_)

    if not vpn_connection:
        raise NonRecoverableError(
            'Could not find VPN Connection id={0}'.format(id_))

    use_external = ctx.node.properties[USE_EXTERNAL_RESOURCE_PROPERTY]

    if not use_external:
        vpn_connection.delete()

        ctx.logger.info('Deleted VPN Connection id={0}'.format(id_))
    else:
        ctx.logger.info('Did not delete VPN Connection id={0}'.format(id_))
