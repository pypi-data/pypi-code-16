
import logging

class ScannedDataService(object):
  logger = logging.getLogger(__name__)

  def __init__(self, worker_id, worker_dao):
    if not worker_id:
      raise Exception("id must be set")
    self.worker_dao = worker_dao
    self.worker_id = worker_id
    self.logger.info("worker_id: {}".format(worker_id))

  @classmethod
  def extract_and_merge_data(slc, old_data, new_data):
    splitted_str = new_data.split('-')
    if splitted_str[0] == "mit":
      return dict(old_data, **{"employee": splitted_str[1]})
    if splitted_str[0] == "platz":
      return dict(old_data, **{"stage": splitted_str[1]})
    if splitted_str[0] == "a":
      d = dict(old_data)
      d["jobs"].append(splitted_str[1])
      d["jobs"] = sorted(list(set(d["jobs"])))
      return d

  def get_worker(self):
    worker = self.worker_dao.get(self.worker_id)
    self.worker_dao.save(self.worker_id, worker)
    return worker

  def put_scanned_data(self, scaned_data):
    worker = self.worker_dao.get(self.worker_id)
    update_worker = self.extract_and_merge_data(worker, scaned_data)

    self.worker_dao.save(self.worker_id, update_worker)
    return update_worker




