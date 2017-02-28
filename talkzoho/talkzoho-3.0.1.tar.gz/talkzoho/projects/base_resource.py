from typing import Optional, Union

from urllib.parse import urlencode

from tornado.web import HTTPError
from tornado.httpclient import HTTPError as HTTPClientError
from tornado.escape import json_decode

from fuzzywuzzy import fuzz

from talkzoho import logger
from talkzoho.resource import Resource
from talkzoho.projects.utils import unwrap_items, to_zoho_value


class BaseResource(Resource):

    def module_url(self, module_name):
        return '{base_url}/{module}/'.format(
            base_url=self.service.base_url,
            module=module_name)

    @property
    def base_query(self):
        return self.service.base_query

    async def get(self, id: Union[int, str], *, columns=None):
        url = '{module_url}{id}/?{query}'.format(
            module_url=self.module_url(self.name),
            id=id,
            query=urlencode(self.base_query))

        logger.info('GET: {}'.format(url))
        response = await self.http_client.fetch(url, method='GET')
        body     = json_decode(response.body.decode("utf-8"))

        [item] = unwrap_items(body)
        return {k: v for k, v in item.items() if not columns or k in columns}

    async def filter(self, *,
                     term: Optional[str]=None,
                     columns: Optional[list]=None,
                     offset: int=0,
                     limit: Optional[int]=None):
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

        while paging and (term or limit is None or to_index <= limit):
            query = {
                'index': from_index,
                'range': batch_size,
                **self.base_query}

            url = '{module_url}?{query}'.format(
                module_url=self.module_url(self.name),
                query=urlencode(query))

            logger.info('GET: {}'.format(url))
            response = await self.http_client.fetch(url, method='GET')

            if response.code == 204 and from_index - 1 != offset:
                # if paging and hit end finish paging
                paging = False
            elif response.code == 204:
                # unless first request caused the 204
                raise HTTPError(204, reason='No items found')
            else:
                body       = json_decode(response.body.decode('utf-8'))
                items      = unwrap_items(body)
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

    async def insert(self, record: dict):
        url    = self.module_url(self.name)
        record = {k: to_zoho_value(v) for k, v in record.items()}
        body   = urlencode({**record, **self.base_query})

        logger.info('POST: {}, BODY: {}'.format(url, body))
        response = await self.http_client.fetch(url, method='POST', body=body)
        body     = json_decode(response.body.decode('utf-8'))

        [item] = unwrap_items(body)
        return item['id']

    async def update(self, record: dict):
        url  = '{module_url}{id}/'.format(
            module_url=self.module_url(self.name),
            id=record.pop('id'))
        body = urlencode({**record, **self.base_query})

        logger.info('POST: {}, BODY: {}'.format(url, body))
        response = await self.http_client.fetch(url, method='POST', body=body)
        body     = json_decode(response.body.decode('utf-8'))

        [item] = unwrap_items(body)
        return item

    async def delete(self, id: Union[int, str]):
        url = '{module_url}{id}/?{query}'.format(
            module_url=self.module_url(self.name),
            id=id,
            query=urlencode(self.base_query))

        logger.info('DELETE: {}'.format(url))
        # mimic zoho crm response and always return True
        # TODO: add get test to zoho CRM
        try:
            await self.http_client.fetch(url, method='DELETE')
        except HTTPClientError:
            pass
        return True
