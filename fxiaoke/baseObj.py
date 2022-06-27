from fxiaoke.api import FxiaokeApi
class baseObj(object):

    def __init__(self, api=None):
        self._api = api or FxiaokeApi.get_default_api()

    def get_id_assured(self):
        return self.get_id()

    def get_api(self):
        """
        Returns the api associated with the object.
        """
        return self._api
