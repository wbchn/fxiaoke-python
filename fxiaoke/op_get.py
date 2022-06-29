"""
请求路径：https://open.fxiaoke.com/cgi/crm/v2/data/create
请求方式：post+application/json 方式
"""
from fxiaoke.api import Request
from fxiaoke.baseObj import baseObj


class getObj(baseObj):
    node_id = 'data'
    endpoint = 'get'

    def execute(self, *args, **kwargs):
        return super().get(*args, **kwargs)
