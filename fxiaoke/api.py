import copy
import logging

import six

from fxiaoke.session import FxiaokeSession

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FxiaokeApi(object):
    API_VERSION = 'v2'

    HTTP_DEFAULT_HEADERS = {}

    def __init__(self, session: FxiaokeSession, api_version=None, enable_debug_logger=False):
        """Initializes the api instance.
        Args:
            session: FacebookSession object that contains a requests interface
                and attribute GRAPH (the Facebook GRAPH API URL).
            api_version: API version
        """
        self._session = session
        self._num_requests_succeeded = 0
        self._num_requests_attempted = 0
        self._api_version = api_version or self.API_VERSION
        self._enable_debug_logger = enable_debug_logger
        self._last_response = None

    def get_num_requests_attempted(self):
        """Returns the number of calls attempted."""
        return self._num_requests_attempted

    def get_num_requests_succeeded(self):
        """Returns the number of calls that succeeded."""
        return self._num_requests_succeeded

    def get_last_response(self):
        """Returns the last requests calls, for developer."""
        return self._last_response

    @classmethod
    def init(
        cls,
        app_id=None,
        app_secret=None,
        permanent_code=None,
        open_user_id=None,
        api_version='v2',
        proxies=None,
        timeout=None,
        debug=False,
        crash_log=True,
    ):
        session = FxiaokeSession(app_id, app_secret, permanent_code, proxies,
                                 timeout)
        api = cls(session, api_version, enable_debug_logger=debug)
        cls.set_default_api(api)
        cls._open_user_id = open_user_id
        return api

    @classmethod
    def set_default_api(cls, api_instance):
        """Sets the default api instance.
        When making calls to the api, objects will revert to using the default
        api if one is not specified when initializing the objects.
        Args:
            api_instance: The instance which to set as default.
        """
        cls._default_api = api_instance

    @classmethod
    def get_default_api(cls):
        """Returns the default api instance."""
        return cls._default_api

    def call(
        self,
        method,
        path,
        params=None,
        headers=None,
        files=None,
        url_override=None,
        api_version=None,
    ):
        if not params:
            params = {}
        if not headers:
            headers = {}
        if not files:
            files = {}

        api_version = api_version or self._api_version

        self._num_requests_attempted += 1

        if not isinstance(path, six.string_types):
            # Path is not a full path
            path = "/".join((
                url_override or self._session.GRAPH,
                api_version,
                '/'.join(map(str, path)),
            ))

        # Include api headers in http request
        headers = headers.copy()
        headers.update(FxiaokeApi.HTTP_DEFAULT_HEADERS)

        token = self._session.fresh_token()
        params.update({"currentOpenUserId": self._open_user_id, **token})

        try:
            response = self._session.requests.request(
                method,
                path,
                json=params,
                headers=headers,
                files=files,
                timeout=self._session.timeout
            )
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            logger.exception(e)
            logger.warning(f'{method}: {path}, with {params}, headers:{headers}')
            raise e
        
        self._last_response = response
        if self._enable_debug_logger:
            import curlify
            print(curlify.to_curl(response.request))
        if response.status_code != six.moves.http_client.OK:
            raise RuntimeError(f'status code: response.status_code')

        json_body = response.json()
        if json_body['errorCode'] != 0:
            raise RuntimeError(f'reponse error: {json_body}')

        self._num_requests_succeeded += 1
        data = json_body
        if 'data' in json_body and isinstance(json_body['data'], dict):
            data = json_body['data']
        return data


class Cursor(object):

    def __init__(
        self,
        source_object=None,
        params=None,
        api=None,
        node_id=None,
        endpoint=None,
    ):
        self.params = dict(params or {})
        self._source_object = source_object
        self._api = api or source_object.get_api()
        self._node_id = node_id or source_object.get_id_assured()
        self._endpoint = endpoint or source_object.get_endpoint()
        self._path = (
            self._node_id,
            self._endpoint,
        )
        self._queue = []
        self._headers = []
        self._finished_iteration = False
        self._total_count = None

    def __repr__(self):
        return str(self._queue)

    def __len__(self):
        return len(self._queue)

    def __iter__(self):
        return self

    def __next__(self):
        # Load next page at end.
        # If load_next_page returns False, raise StopIteration exception
        if not self._queue and not self.load_next_page():
            raise StopIteration()

        return self._queue.pop(0)

    def total(self):
        return self._total_count

    def load_next_page(self):
        """Queries server for more nodes and loads them into the internal queue.
        Returns:
            True if successful, else False.
        """
        if self._finished_iteration:
            return False

        logger.debug(f'Request url: {self._path}')
        logger.debug(f' with payload: {self.params}')

        response: dict = self._api.call(
            'POST',
            self._path,
            params=self.params,
        )


        if (
            'total' in response and
            'offset' in response and
            response['total'] > response['offset'] + response['limit']
        ):
            self.params['data']['search_query_info']['offset'] = (
                response['offset']
                + response['limit']
            )
        else:
            # Indicate if this was the last page
            self._finished_iteration = True

        if (
            'total' in response
        ):
            self._total_count = response['total']
        logger.info(
            f'response: {response.get("offset")}+{response.get("limit")}/{response.get("total")}.')

        self._queue = response['dataList']
        return len(self._queue) > 0

    def get_one(self):
        for obj in self:
            return obj
        return None


class Request(object):

    def __init__(
        self,
        node_id,
        method,
        endpoint,
        api=None,
        api_type=None,
        response_parser=None,
        include_summary=True,
    ):

        self._api = api or FxiaokeApi.get_default_api()
        self._method = method
        self._node_id = node_id
        self._endpoint = endpoint.replace('/', '')
        self._path = (node_id, endpoint.replace('/', ''))
        self._api_type = api_type
        self._response_parser = response_parser
        self._include_summary = include_summary
        self._params = {}
        self._fields = []
        self._file_params = {}
        self._file_counter = 0
        self._accepted_fields = []

    def execute(self):
        params = copy.deepcopy(self._params)
        # if self._fields:
        #     params['fields'] = ','.join(self._fields)
        cursor = Cursor(
            params=params,
            api=self._api,
            node_id=self._node_id,
            endpoint=self._endpoint,
        )
        cursor.load_next_page()
        return cursor

    def add_field(self, field):
        self._fields.append(field)
        # if field not in self._fields:
        #     self._fields.append(field)
        # if field not in self._accepted_fields:
        #     logger.warning(self._endpoint + ' does not allow field ' + field)
        return self

    def add_fields(self, fields):
        if fields is None:
            return self
        for field in fields:
            self.add_field(field)
        return self

    def get_fields(self):
        return list(self._fields)

    def add_param(self, key, value):
        self._params[key] = value
        # if not self._param_checker.is_valid_pair(key, value):
        #     api_utils.warning('value of ' + key + ' might not be compatible. ' +
        #         ' Expect ' + self._param_checker.get_type(key) + '; ' +
        #         ' got ' + str(type(value)))
        # if self._param_checker.is_file_param(key):
        #     self._file_params[key] = value
        # else:
        #     self._params[key] = self._extract_value(value)
        return self

    def add_params(self, params):
        if params is None:
            return self
        for key in params.keys():
            self.add_param(key, params[key])
        return self

    def get_params(self):
        return copy.deepcopy(self._params)
