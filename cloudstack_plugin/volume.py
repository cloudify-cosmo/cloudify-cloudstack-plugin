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


from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError

from cloudstack_plugin.cloudstack_common import (
    get_cloud_driver,
    get_resource_id,
    CLOUDSTACK_ID_PROPERTY,
    CLOUDSTACK_NAME_PROPERTY,
    CLOUDSTACK_TYPE_PROPERTY,
    COMMON_RUNTIME_PROPERTIES_KEYS

)
from cloudstack_plugin.virtual_machine import get_vm_by_id

VOLUME_CLOUDSTACK_TYPE = 'volume'

RUNTIME_PROPERTIES_KEYS = COMMON_RUNTIME_PROPERTIES_KEYS

__author__ = 'jedeko'


@operation
def attach_volume(ctx, **kwargs):
    """ Create volume and attach to virtual machine.
    """

    cloud_driver = get_cloud_driver(ctx)

    vm_id = ctx.target.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY]
    vm = get_vm_by_id(ctx, cloud_driver, vm_id)

    volume_name = ctx.source.node.properties['name']
    volume_size = ctx.source.node.properties['size']

    volume = cloud_driver.create_volume(name=volume_name,
                                        size=volume_size)

    cloud_driver.attach_volume(node=vm,
                               volume=volume)

    ctx.source.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY] = volume.id
    ctx.source.instance.runtime_properties[CLOUDSTACK_TYPE_PROPERTY] = \
        VOLUME_CLOUDSTACK_TYPE
    

@operation
def detach_volume(ctx, **kwargs):
    """ Detaches a volume and delete if expunge is requested.
    """

    cloud_driver = get_cloud_driver(ctx)

    volume_id = ctx.source.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY]
    volume = get_volume_by_id(ctx, cloud_driver, volume_id)

    # Detach the volume from the vm
    try:
        cloud_driver.detach_volume(volume=volume)
    except Exception as e:
        ctx.logger.warn('Volume {0} may not have been detached: {1}'
                        .format(volume, str(e)))
        pass

    # Expunge the volume if true in blueprint configuration
    volume_expunge = ctx.source.node.properties['expunge']

    if volume_expunge:
        try:
            cloud_driver.destroy_volume(volume=volume)
        except Exception as e:
            ctx.logger.warn('Volume {0} may not have been destroyed: {1}'
                            .format(volume, str(e)))
            pass


def get_volume_by_id(ctx, cloud_driver, volume_id):

    volumes = [volume for volume in cloud_driver.list_volumes() if
               volume_id == volume.id]

    if not volumes:
        ctx.logger.info('Could not find volume with ID {0}'.
                        format(volume_id))
        return None

    return volumes[0]