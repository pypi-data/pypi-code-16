from bitfusion.api.base import BaseMixin, CreatableMixin

class Volume(BaseMixin, CreatableMixin):
  base_url = '/volume'

  def __str__(self):
    output = '\nVolume {id} - {name}\nHost: {host_path}\nContainer: {container_path}'
    output = output.format(id=self.data['id'],
                           name=self.data['name'],
                           host_path=self.data['host_path'],
                           container_path=self.data['container_path'])

    return output + '\n'
