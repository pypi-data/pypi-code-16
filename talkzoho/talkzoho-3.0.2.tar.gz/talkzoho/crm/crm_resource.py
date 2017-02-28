from typing import Optional, Union

from urllib.parse import urlencode

from tornado.web import HTTPError
from tornado.escape import json_decode

from fuzzywuzzy import fuzz

from talkzoho import logger
from talkzoho.resource import Resource
from talkzoho.crm.utils\
    import select_columns, unwrap_items, wrap_items, make_module_id_name


class CRMResource(Resource):

    def module_url(self, module_name):
        return '{base_url}/{module}'.format(
            base_url=self.service.base_url,
            module=module_name)

    @property
    def base_query(self):
        return self.service.base_query

    async def get_canonical_map(self):
        """
        Will return the module map associated to
        the Module's instance name.
        Zoho's canonical names will take precidence and user
        aliases second.
        e.g.
        The Potentials module in Zoho has been renamed opportunities
        and crm.
        """
        name = self.name
        maps = await self.service.get_module_maps()
        if self.service.use_module_aliases:
            [m] = [m for m in maps if m.plural_alias.replace(' ', '') == name]
        else:
            [m] = [m for m in maps if m.canonical_name == name]
        return m

    async def get(self, id: Union[int, str], *, columns=None):
        module_map  = await self.get_canonical_map()
        module_name = module_map.canonical_name
        module_url  = self.module_url(module_name)

        query = {
            'id': id,
            'version': 2,
            'newFormat': 2,
            **self.base_query}

        if columns:
            query['selectColumns'] = select_columns(module_name, columns)

        url = '{module_url}/getRecordById?{query}'.format(
            module_url=module_url,
            query=urlencode(query))

        logger.info('GET: {}'.format(url))
        response = await self.http_client.fetch(url, method='GET')
        body     = json_decode(response.body.decode('utf-8'))

        [item] = unwrap_items(body)
        return item

    async def insert(self, record: dict, *, trigger_workflows: bool=True):
        module_map  = await self.get_canonical_map()
        module_name = module_map.canonical_name
        module_url  = self.module_url(module_name)
        xml_record = wrap_items(record, module_name=module_name)

        url  = '{module_url}/insertRecords'.format(module_url=module_url)
        body = urlencode({
            'version': 2,
            'xmlData': xml_record,
            'newFormat': 2,
            'wfTrigger': str(trigger_workflows).lower(),
            'duplicateCheck': 1,
            **self.base_query})

        logger.info('POST: {}, BODY: {}'.format(url, body))
        response = await self.http_client.fetch(url, method='POST', body=body)
        body     = json_decode(response.body.decode('utf-8'))

        [item] = unwrap_items(body)
        return item['Id']

    async def filter(self, *,
                     term: Optional[str]=None,
                     columns: Optional[list]=None,
                     offset: int=0,
                     limit: Optional[int]=None):
        module_map  = await self.get_canonical_map()
        module_name = module_map.canonical_name
        module_url  = self.module_url(module_name)

        if limit == 0:
            return []
        elif not term and limit and limit <= self.service.MAX_PAGE_SIZE:
            batch_size = limit
        else:
            batch_size = self.service.MAX_PAGE_SIZE

        paging     = True
        from_index = offset + 1  # Zoho indexes at one not zero
        to_index   = offset + batch_size
        results    = []

        # Loop until we reach index we need, unless their is a search term.
        # If search term we need all records.
        while paging and (term or limit is None or to_index <= limit):
            query = {
                'fromIndex': from_index,
                'toIndex': to_index,
                'newFormat': 2,
                'version': 2,
                **self.base_query}

            if columns:
                query['selectColumns'] = select_columns(module_name, columns)

            url = '{module_url}/getRecords?{query}'.format(
                module_url=module_url,
                query=urlencode(query))

            logger.info('GET: {}'.format(url))
            response = await self.http_client.fetch(url, method='GET')
            body     = json_decode(response.body.decode('utf-8'))

            try:
                items = unwrap_items(body)
            except HTTPError as http_error:
                # if paging and hit end suppress error
                # unless first request caused the 404
                if http_error.status_code == 404 and from_index - 1 != offset:
                    paging = False
                else:
                    raise
            else:
                results   += items
                from_index = to_index + 1
                to_index  += batch_size

        def fuzzy_score(resource):
            values = [str(v) for v in resource.values() if v]
            target = ' '.join(values)
            return fuzz.partial_ratio(term, target)

        if term:
            results = sorted(results, key=fuzzy_score, reverse=True)

        return results[:limit]

    async def update(self,
                     record: dict, *,
                     trigger_workflows: bool=True):
        module_map  = await self.get_canonical_map()
        module_name = module_map.canonical_name
        module_url  = self.module_url(module_name)
        module_key  = make_module_id_name(module_map=module_map)
        record_id  = record.pop(module_key)
        xml_record = wrap_items(record, module_name=module_name)

        url  = '{module_url}/updateRecords'.format(module_url=module_url)
        body = urlencode({
            'version': 2,
            'newFormat': 2,
            'wfTrigger': str(trigger_workflows).lower(),
            'id': record_id,
            'xmlData': xml_record,
            **self.base_query})

        logger.info('POST: {}, BODY: {}'.format(url, body))
        response = await self.http_client.fetch(url, method='POST', body=body)
        body     = json_decode(response.body.decode('utf-8'))

        [item] = unwrap_items(body)
        return item['Id']

    async def upsert(self,
                     record: dict, *,
                     trigger_workflows: bool=True):
        module_map = await self.get_canonical_map()
        module_key = make_module_id_name(module_map=module_map)
        if module_key in record:
            self.update(record=record, trigger_workflows=trigger_workflows)
        else:
            self.insert(record=record, trigger_workflows=trigger_workflows)

    async def delete(self, id: Union[int, str]):
        module_map  = await self.get_canonical_map()
        module_name = module_map.canonical_name
        module_url  = self.module_url(module_name)

        query = {'id': id, **self.base_query}
        url   = '{module_url}/deleteRecords?{query}'.format(
            module_url=module_url,
            query=urlencode(query))

        logger.info('DELETE: {}'.format(url))
        response = await self.http_client.fetch(url, method='GET')
        body     = json_decode(response.body.decode('utf-8'))

        success = unwrap_items(body)
        return success

    async def upload_file(self, *, record_id: Union[int, str], url: str):
        module_map  = await self.get_canonical_map()
        module_name = module_map.canonical_name
        module_url  = self.module_url(module_name)

        endpoint = '{module_url}/uploadFile'.format(module_url=module_url)
        body = urlencode({
            'id': record_id,
            'attachmentUrl': url,
            **self.base_query})

        logger.info('POST: {}, BODY: {}'.format(endpoint, body))
        response = await self.http_client.fetch(endpoint, method='POST', body=body)
        body     = json_decode(response.body.decode('utf-8'))

        [item] = unwrap_items(body)
        return item['Id']

    async def delete_file(self, id: Union[int, str]):
        module_map  = await self.get_canonical_map()
        module_name = module_map.canonical_name
        module_url  = self.module_url(module_name)

        query = {'id': id, **self.base_query}
        url   = '{module_url}/deleteFile?{query}'.format(
            module_url=module_url,
            query=urlencode(query))

        logger.info('GET: {}'.format(url))
        response = await self.http_client.fetch(url, method='GET')
        body     = json_decode(response.body.decode('utf-8'))

        success = unwrap_items(body)
        return success
