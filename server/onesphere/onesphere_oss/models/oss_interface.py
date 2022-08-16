# -*- coding: utf-8 -*-
import io
import os
from typing import List
from concurrent import futures
from odoo import models, _
from odoo.tools import ustr
import logging
import functools
import urllib3
from minio import Minio
from minio.helpers import ObjectWriteResult
from odoo.addons.oneshare_utils.constants import ENV_OSS_BUCKET, ENV_OSS_ENDPOINT, ENV_OSS_ACCESS_KEY, \
    ENV_OSS_SECRET_KEY, ENV_MAX_WORKERS, ENV_OSS_SECURITY_TRANSPORT

from typing import Optional, Union

_logger = logging.getLogger(__name__)

glb_minio_client = None


def oss_wrapper(raw_resp=True):
    """

    :param raw_resp: boolean, 是否返回urllib3.HTTPResponse对象
    :return:
    """

    def decorator(f):
        @functools.wraps(f)
        def _oss_wrap(*args, **kw):
            data = None
            resp = None
            _logger.debug(f"params:{args}, object params: {kw}")
            try:
                resp: Optional[ObjectWriteResult, urllib3.response.HTTPResponse] = f(*args, **kw)
                if isinstance(resp, ObjectWriteResult):
                    data = resp.object_name
                if isinstance(resp, urllib3.response.HTTPResponse):
                    data = resp.data
            except Exception as e:
                _logger.error(f"{f.__name__}: {ustr(e)}")
            finally:
                if not resp:
                    return resp
                if isinstance(resp, urllib3.response.HTTPResponse):
                    resp.close()
                    resp.release_conn()
                if raw_resp:
                    return resp
                return data

        return _oss_wrap

    return decorator


class OSSInterface(models.AbstractModel):
    _name = 'onesphere.oss.interface'
    _description = '对象存储接口抽象类'

    def ensure_oss_client(self):
        global glb_minio_client
        if glb_minio_client:
            return glb_minio_client
        ICP = self.env['ir.config_parameter']
        endpoint = ICP.get_param('oss.endpoint', ENV_OSS_ENDPOINT)
        access_key = ICP.get_param('oss.access_key', ENV_OSS_ACCESS_KEY)
        secret_key = ICP.get_param('oss.secret_key', ENV_OSS_SECRET_KEY)
        security = ICP.get_param('oss.security', ENV_OSS_SECURITY_TRANSPORT)
        c = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=security,
                  http_client=urllib3.PoolManager(timeout=float(os.environ.get("ODOO_HTTP_SOCKET_TIMEOUT", '20')),
                                                  retries=urllib3.Retry(
                                                      total=5,
                                                      backoff_factor=0.2,
                                                      status_forcelist=[500, 502, 503, 504],
                                                  ),
                                                  ), )
        glb_minio_client = c
        return glb_minio_client

    @classmethod
    def reset_global_minio_client(cls):
        global glb_minio_client
        glb_minio_client = None

    def get_oss_objects(self, bucket_names: str, object_names: List[str]):
        # 获取minio数据
        data = []
        if len(object_names) <= ENV_MAX_WORKERS:
            ret = list(map(lambda object_name: self.get_oss_object(bucket_names[0], object_name), object_names))
            return ret
        with futures.ThreadPoolExecutor(max_workers=ENV_MAX_WORKERS) as executor:
            # task_list = [executor.submit(self.get_oss_object, (bucket_names[0], object_name)) for object_name in object_names]
            task_list = [executor.submit(self.get_oss_object, *args) for args in
                         zip(bucket_names, object_names)]
        for task in task_list:
            task_exception = task.exception()
            if task_exception:
                _logger.error(f'get_oss_objects 任务执行失败: {ustr(task_exception)}')
                continue
            data.append(task.result())
        return data

    @oss_wrapper(raw_resp=False)
    def get_oss_object(self, bucket_name: str, object_name: str):
        # 获取minio数据
        c = self.ensure_oss_client()
        ret = c.get_object(bucket_name, object_name)
        return ret

    @oss_wrapper(raw_resp=False)
    def put_oss_object(self, bucket_name: str, object_name: str, data: Union[bytes, str]):
        c = self.ensure_oss_client()
        if isinstance(data, str):
            data = data.encode('utf-8')
        length = len(data)
        f = io.BytesIO(data)
        return c.put_object(bucket_name, object_name, f, length)
