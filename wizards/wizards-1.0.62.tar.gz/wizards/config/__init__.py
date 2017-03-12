import os

from ea.lib.datastructures import DTO
import ioc
import origin
import yaml


class SGConfiguration(DTO):
    pass



def load(src):
    with open(src) as f:
        dto = SGConfiguration(yaml.safe_load(f.read())).as_dto()

    dto.config_dir = os.path.dirname(src)
    dto.ioc_dir = os.path.join(
        dto.config_dir, "%s/*.ioc" % dto.general.ioc)
    return dto.as_dto()
