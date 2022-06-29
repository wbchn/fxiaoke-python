"""
请求路径：https://open.fxiaoke.com/cgi/crm/v2/data/query
请求方式：post+application/json 方式
"""

from fxiaoke.baseObj import baseObj


class queryObj(baseObj):
    node_id = 'data'
    endpoint = 'query'

    def execute(self, *args, **kwargs):
        return super().query(*args, **kwargs)
