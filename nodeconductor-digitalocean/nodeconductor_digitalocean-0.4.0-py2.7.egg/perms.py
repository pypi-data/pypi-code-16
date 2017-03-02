from nodeconductor.core.permissions import StaffPermissionLogic
from nodeconductor.structure import perms as structure_perms


PERMISSION_LOGICS = (
    ('nodeconductor_digitalocean.DigitalOceanService', structure_perms.service_permission_logic),
    ('nodeconductor_digitalocean.DigitalOceanServiceProjectLink', structure_perms.service_project_link_permission_logic),
    ('nodeconductor_digitalocean.Droplet', structure_perms.resource_permission_logic),
    ('nodeconductor_digitalocean.Image', StaffPermissionLogic(any_permission=True)),
    ('nodeconductor_digitalocean.Region', StaffPermissionLogic(any_permission=True)),
    ('nodeconductor_digitalocean.Size', StaffPermissionLogic(any_permission=True)),
)
