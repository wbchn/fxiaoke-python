# fxiaoke-python

基于[纷享开放平台](https://open.fxiaoke.com/wiki.html)开发。

设计思路参考 facebook_business

## Install

`pip install fxiaoke-python`

## Usage

```python
from fxiaoke.api import FxiaokeApi
from fxiaoke.query import queryObj

api = FxiaokeApi.init(
    app_id="FSAID_xx",
    app_secret="xxx",
    permanent_code="xxx",
    open_user_id="FSUID_xxx",
)

data = queryObj().api_get(
    dataObjectApiName='LeadsObj',
    filters=[{
        'field_name': 'last_modified_time',
        'field_values': [1656213600000, 1656400000000],
        'operator': 'BETWEEN',
    }],
    limit=100,
    offset=0
)

import time
for i, rec in enumerate(data):
    print(i, rec['name'], time.ctime(rec['create_time']/1000), time.ctime(rec['last_modified_time']/1000), )
```