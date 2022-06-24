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

    def get_num_requests_attempted(self):
        """Returns the number of calls attempted."""
        return self._num_requests_attempted

    def get_num_requests_succeeded(self):
        """Returns the number of calls that succeeded."""
        return self._num_requests_succeeded

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
        cls._default_api = api
        cls._open_user_id = open_user_id
        return api

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

        response = self._session.requests.request(
            method,
            path,
            data=params,
            headers=headers,
            files=files,
            timeout=self._session.timeout
        )
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
        fields=None,
        params=None,
        api=None,
    ):
        self.params = dict(params or {})
        self._source_object = source_object
        self._api = api or source_object.get_api()
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

        response: dict = self._api.call(
            'GET',
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
        param_checker=TypeChecker({}, {}),
        target_class=None,
        api_type=None,
        allow_file_upload=False,
        response_parser=None,
        include_summary=True,
        api_version=None,
    ):

        self._api = api or FxiaokeApi.get_default_api()
        self._method = method
        self._endpoint = endpoint.replace('/', '')
        self._path = (node_id, endpoint.replace('/', ''))
        self._param_checker = param_checker
        self._target_class = target_class
        self._api_type = api_type
        self._allow_file_upload = allow_file_upload
        self._response_parser = response_parser
        self._include_summary = include_summary
        self._api_version = api_version
        self._params = {}
        self._fields = []
        self._file_params = {}
        self._file_counter = 0
        self._accepted_fields = []
        if target_class is not None:
            self._accepted_fields = target_class.Field.__dict__.values()

    def execute(self):
        params = copy.deepcopy(self._params)
        if self._fields:
            params['fields'] = ','.join(self._fields)
        if self._api_type == "EDGE" and self._method == "GET":
            cursor = Cursor(
                target_objects_class=self._target_class,
                params=params,
                fields=self._fields,
                include_summary=self._include_summary,
                api=self._api,
                node_id=self._node_id,
                endpoint=self._endpoint,
            )
            cursor.load_next_page()
            return cursor
