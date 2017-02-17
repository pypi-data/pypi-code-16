# -*- coding: UTF-8 -*-
#
# @author huangyue<huangyue@haodou.com>
# @since 17/2/17
#


from hd_es_tools.mongo_connector_doc_managers.formatters_proxy import DefaultDocumentFormatter
from hd_es_tools.es_sync.fav_title_sync.task_sync_fav_title import TaskSyncFavTitle


class FavDocumentFormatter(DefaultDocumentFormatter):
    # 补全 标题
    # 在 DefaultDocumentFormatter 基础上 再 补全 objTitle  objPinYin objSimPinYin

    def __init__(self, option):
        super(FavDocumentFormatter, self).__init__(option)
        self.sync = TaskSyncFavTitle()

    def format_document(self, doc_id, document, namespace):
        res = super(FavDocumentFormatter, self).format_document(doc_id,document, namespace)
        try:
            if 'objId' in res and 'objType' in res:
                try:
                    for objTitle, objPinYin, objSimPinYin in self.sync.getObj(res):
                        if objTitle is not None:
                            res['objTitle'] = objTitle
                        if objPinYin is not None:
                            res['objPinYin'] = objPinYin
                        if objSimPinYin is not None:
                            res['objSimPinYin'] = objSimPinYin
                except Exception as e:
                    self.sync.saveErrorDoc([{"_id": doc_id, "objId": res['objId'], "objType": res['objType']}])

        except Exception as e:
            pass
        return res
