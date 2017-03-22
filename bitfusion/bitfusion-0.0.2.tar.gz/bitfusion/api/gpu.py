from bitfusion.api.base import BaseMixin

class Gpu(BaseMixin):
  def _str_(self):
    output = 'GPU {id} - {type} - {mem} MB Memory - {state}'
    output = output.format(id=self.data['id'],
                           type=self.data['type'],
                           mem=self.data.get('memory', '???'),
                           state=self.data['state'])

    return output
