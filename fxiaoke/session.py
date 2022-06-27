
import os
import time

import requests


class FxiaokeSession(object):
    GRAPH = 'https://open.fxiaoke.com/cgi/crm'

    def __init__(self, app_id=None, app_secret=None, permanent_code=None,
                 proxies=None, timeout=None, debug=False):
        self.app_id = app_id
        self.app_secret = app_secret
        self.permanent_code = permanent_code
        self.proxies = proxies
        self.timeout = timeout
        self.debug = debug
        self.requests = requests.Session()

        self.corpAccessToken = None
        self.corpId = None
        self.token_expired = 0

        # params = {
        #     'access_token': self.access_token
        # }
        # if app_secret:
        #     params['appsecret_proof'] = self._gen_appsecret_proof()
        # self.requests.params.update(params)

        if self.proxies:
            self.requests.proxies.update(self.proxies)

    def fresh_token(self):
        if self.corpAccessToken and time.time() < self.token_expired:
            return {
                "corpAccessToken": self.corpAccessToken,
                "corpId": self.corpId,
            }
        url = 'https://open.fxiaoke.com/cgi/corpAccessToken/get/V2'
        payload = {
            "appId": self.app_id,
            "appSecret": self.app_secret,
            "permanentCode": self.permanent_code,
        }

        resp = self.requests.post(url, json=payload)
        data = resp.json()
        if data['errorCode'] == 0:
            self.corpAccessToken = data['corpAccessToken']
            self.corpId = data['corpId']
            self.token_expired = time.time() + data['expiresIn'] - 30

        return {
            "corpAccessToken": self.corpAccessToken,
            "corpId": self.corpId,
        }


__all__ = ['FxiaokeSession']
