from math import ceil

from typing import Optional, Union

from urllib.parse import urlencode

from tornado.web import HTTPError
from tornado.httpclient import HTTPError as HTTPClientError
from tornado.escape import json_decode

from fuzzywuzzy import fuzz

from talkzoho import logger
from talkzoho.resource import Resource


class BaseResource(Resource):

    @property
    def module_url(self):
        return '{base_url}/{module}'.format(
            base_url=self.service.base_url,
            module=self.name)

    @property
    def base_query(self):
        return self.service.base_query

    async def get(self,
                  id: Union[int, str],
                  *,
                  organization_id: Union[str, int],
                  columns=None):
        url = '{base_url}/{id}?{query}'.format(
            base_url=self.module_url,
            id=id,
            query=urlencode({
                'organization_id': organization_id,
                **self.base_query}))

        try:
            logger.info('GET: {}'.format(url))
            response  = await self.http_client.fetch(url, method='GET')
        except HTTPClientError as http_error:
            http_code = http_error.code
            response  = json_decode(http_error.response.body.decode("utf-8"))
            message   = str(response['code']) + ': ' + response['message']
            raise HTTPError(http_code, reason=message)
        else:
            response  = json_decode(response.body.decode("utf-8"))
            results   = [v for k, v in response.items() if k not in ['code', 'message']]  # noqa

            if len(results) != 1:
                ValueError('More then one resource was returned.')

            return results[0]

    async def filter(self, *,
                     organization_id: Union[str, int],
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
        page_index = max(ceil(offset / batch_size), 1)
        results    = []

        # Loop until we reach index we need, unless their is a search term.
        # If search term we need all records.
        while paging and (term or not limit or len(results) < limit):
            url = '{base_url}?{query}'.format(
                base_url=self.module_url,
                query=urlencode({
                    'organization_id': organization_id,
                    'per_page': batch_size,
                    'page': page_index,
                    **self.base_query}))

            try:
                logger.info('GET: {}'.format(url))
                response = await self.http_client.fetch(url, method='GET')
            except HTTPClientError as http_error:
                http_code = http_error.code
                body      = http_error.response.body
                response  = json_decode(body.decode("utf-8"))
                message   = str(response['code']) + ': ' + response['message']
                raise HTTPError(http_code, reason=message)
            else:
                response    = json_decode(response.body.decode("utf-8"))
                results    += response[self.name]
                page_index += 1
                paging      = response['page_context']['has_more_page']

        def fuzzy_score(items):
            values = [str(v).lower() for v in items.values() if v]
            target = ' '.join(values)
            return fuzz.partial_ratio(term, target)

        if term:
            results = sorted(results, key=fuzzy_score, reverse=True)

        results = results[:limit]
        if columns:
            return [{k: pl[k] for k in columns if k in columns}
                for pl in results]
        else:
            return results
