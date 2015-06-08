########
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
from cloudify import ctx
from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError

from cloudstack_plugin.cloudstack_common import (
    get_cloud_driver,
    CLOUDSTACK_ID_PROPERTY,
    CLOUDSTACK_NAME_PROPERTY,
    CLOUDSTACK_TYPE_PROPERTY,
    COMMON_RUNTIME_PROPERTIES_KEYS,
    USE_EXTERNAL_RESOURCE_PROPERTY,
)

VOLUME_CLOUDSTACK_TYPE = 'volume'

RUNTIME_PROPERTIES_KEYS = COMMON_RUNTIME_PROPERTIES_KEYS


@operation
def create(**kwargs):
    """ Create a volume
    """

    cloud_driver = get_cloud_driver(ctx)
    volume = {}

    if ctx.node.properties[USE_EXTERNAL_RESOURCE_PROPERTY] is False:

        ctx.logger.debug('reading volume attributes.')
        volume.update(copy.deepcopy(ctx.node.properties['volume']))

        if 'name' in volume:
            volume_name = volume['name']
        else:
            raise NonRecoverableError("To create a volume, the name of the "
                                      "volume is needed")

        if 'size' in volume:
            volume_size = volume['size']
        else:
            raise NonRecoverableError("To create a volume, the size of the "
                                      "volume is needed")

        volume = cloud_driver.create_volume(name=volume_name,
                                            size=volume_size)

        if volume_exists(cloud_driver, volume.id):

            ctx.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY] = volume.id
            ctx.instance.runtime_properties[CLOUDSTACK_TYPE_PROPERTY] = \
                VOLUME_CLOUDSTACK_TYPE
        else:
            raise NonRecoverableError("Volume not created")

    elif ctx.node.properties[USE_EXTERNAL_RESOURCE_PROPERTY] is True:

        if ctx.node.properties['resource_id']:
            resource_id = ctx.node.properties['resource_id']

            volume = get_volume_by_id(cloud_driver, resource_id)

            if volume is not None:
                ctx.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY] = \
                    volume.id
                ctx.instance.runtime_properties[CLOUDSTACK_NAME_PROPERTY] = \
                    volume.name
                ctx.instance.runtime_properties[CLOUDSTACK_TYPE_PROPERTY] = \
                    VOLUME_CLOUDSTACK_TYPE
            else:
                raise NonRecoverableError("Could not find volume with id {0}".
                                          format(resource_id))
        else:
            raise NonRecoverableError("Resource_id for volume is not supplied")

        return


@operation
def delete(**kwargs):
    """ Delete a volume
    """

    cloud_driver = get_cloud_driver(ctx)

    volume_id = ctx.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY]
    volume = get_volume_by_id(cloud_driver, volume_id)

    if volume is None:
        raise NonRecoverableError('Volume with id {0} not found'
                                  .format(volume_id))

    if not ctx.node.properties[USE_EXTERNAL_RESOURCE_PROPERTY]:
        ctx.logger.info('Trying to destroy volume {0}'.format(volume))
        cloud_driver.destroy_volume(volume=volume)
    else:
        ctx.logger.info('Volume {0} does not need to be destroyed'.format(
            volume))


def volume_exists(cloud_driver, volume_id):
    exists = get_volume_by_id(cloud_driver, volume_id)
    if not exists:
        return False
    return True


def get_volume_by_id(cloud_driver, volume_id):
    volumes = [volume for volume in cloud_driver.list_volumes()
               if volume_id == volume.id]

    if not volumes:
        ctx.logger.info('Could not find volume with ID {0}'.
                        format(volume_id))
        return None
    return volumes[0]
