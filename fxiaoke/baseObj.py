from fxiaoke.api import FxiaokeApi
from fxiaoke.api import Request


class baseObj(object):
    dataObjectApiName = ''

    def __init__(self, api=None, dataObjectApiName=None):
        self._api = api or FxiaokeApi.get_default_api()
        self.dataObjectApiName = dataObjectApiName

    @classmethod
    def get_endpoint(cls):
        return cls.endpoint

    @classmethod
    def get_id_assured(cls):
        return cls.node_id

    def get_api(self):
        """
        Returns the api associated with the object.
        """
        return self._api

    def query(
        self,
        dataObjectApiName: str = None,
        filters: list = None,
        orders: list = None,
        fieldProjection: list = None,
        offset: int = 0,
        limit: int = 100,
    ):
        params = {
            'data': {
                'dataObjectApiName': dataObjectApiName or self.dataObjectApiName,
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

    def create(
        self,
        object_data: dict = None,
        details: dict = None,
        dataObjectApiName: str = None,
    ):
        if dataObjectApiName or self.dataObjectApiName:
            object_data['dataObjectApiName'] = dataObjectApiName or self.dataObjectApiName
        details = details or {}
        params = {
            'data': {
                'object_data': object_data,
                'details': details,
            }
        }

        request = Request(
            self.node_id,
            method='POST',
            endpoint='query',
            api=self._api,
        )
        # request.add_fields(fieldProjection)
        request.add_params(params)

        return request.execute()

    def get(
        self,
        objectDataId: str,
        dataObjectApiName: str = None,
    ):
        params = {
            'data': {
                'dataObjectApiName': dataObjectApiName or self.dataObjectApiName,
                'objectDataId': objectDataId,
            }
        }

        request = Request(
            self.node_id,
            method='POST',
            endpoint=self.endpoint,
            api=self._api,
        )
        request.add_params(params)

        return request.execute()
