import logging
from typing import Optional

from LayerAkira.src.common.common import Result


class BaseHTTPClient:

    async def _get_query(self, url, jwt: Optional[str] = None):
        if self._verbose:
            logging.info(f'GET {url}')
        res = await self._http.get(url, headers={'Authorization': jwt} if jwt is not None else {})
        if self._verbose:
            logging.info(f'Response {await res.json()} {res.status}')
        resp = await res.json()
        if 'result' in resp:
            return Result(resp['result'])
        return Result(None, resp['code'], resp['error'])

    async def _post_query(self, url, data, jwt: Optional[str] = None):
        if self._verbose:
            logging.info(f'POST {url} and data {data}')
        res = await self._http.post(url, json=data, headers={'Authorization': jwt} if jwt is not None else {})
        if self._verbose:
            logging.info(f'Response {await res.json()} {res.status}')
        resp = await res.json()
        if 'result' in resp:
            return Result(resp['result'])
        return Result(None, resp['code'], resp['error'])
