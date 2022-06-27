"""
请求路径：https://open.fxiaoke.com/cgi/crm/v2/data/query
请求方式：post+application/json 方式
"""
from fxiaoke.api import Request
from fxiaoke.baseObj import baseObj


class queryObj(baseObj):
    node_id = 'data'
    endpoint = 'query'

    @classmethod
    def get_endpoint(cls):
        return cls.endpoint
    
    @classmethod
    def get_id_assured(cls):
        return cls.node_id

    def api_get(
        self,
        dataObjectApiName: str,
        filters: list=None,
        orders: list=None,
        fieldProjection: list = None,
        offset: int = 0,
        limit: int = 100,
    ):
        params = {
            'data': {
                'dataObjectApiName': dataObjectApiName,
                'search_query_info': {
                    'limit': limit,
                    'offset': offset,
                    'filters': filters or [],
                    'orders': orders or [],
                    'fieldProjection': fieldProjection or []
                }
            }
        }

        request = Request(
            self.node_id,
            method='POST',
            endpoint=self.endpoint,
            api=self._api,
        )
        # request.add_fields(fieldProjection)
        request.add_params(params)

        return request.execute()