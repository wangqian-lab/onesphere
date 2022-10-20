# -*- coding: utf-8 -*-
import io
import os
from typing import List
from concurrent import futures

from minio.deleteobjects import DeleteObject

from odoo.tools.profiler import profile
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
from concurrent.futures import ThreadPoolExecutor, as_completed

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
                                                  maxsize=ENV_MAX_WORKERS * 8,
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

    @profile
    def get_oss_objects(self, bucket_name: str, object_names: List[str], curve_ids: List[str]):
        # 获取minio数据
        data = {}
        client = self.ensure_oss_client()
        if len(object_names) <= ENV_MAX_WORKERS:
            data.update({curve_id: self.get_oss_object(bucket_name, object_name, client) for
                         object_name, curve_id in zip(object_names, curve_ids)})
            return data
        with ThreadPoolExecutor(max_workers=ENV_MAX_WORKERS * 8) as executor:
            task_list = {executor.submit(self.get_oss_object, bucket_name, object_name, client): curve_id for object_name, curve_id in zip(object_names, curve_ids)}
            for task in as_completed(task_list):
                task_exception = task.exception()
                if task_exception:
                    _logger.error(f'get_oss_objects 任务执行失败: {ustr(task_exception)}')
                    continue
                data.update({task_list[task]: task.result()})
        return data

    @oss_wrapper(raw_resp=False)
    def get_oss_object(self, bucket_name: str, object_name: str, client: Union[Minio] = None):
        # 获取minio数据
        if not client:
            client = self.ensure_oss_client()
        ret = client.get_object(bucket_name, object_name)
        return ret

    @oss_wrapper(raw_resp=False)
    def remove_oss_objects(self, bucket_name: str, object_names: List[str], client: Union[Minio] = None):
        # 获取minio数据
        if not client:
            client = self.ensure_oss_client()
        objects = [DeleteObject(name) for name in object_names]
        errors = client.remove_objects(bucket_name, objects)
        for error in errors:
            _logger.error(ustr(error))
        return ''

    @oss_wrapper(raw_resp=False)
    def remove_bucket(self, bucket_name: str, client: Union[Minio] = None):
        if not client:
            client = self.ensure_oss_client()
        ret = client.remove_bucket(bucket_name)
        return ret

    @oss_wrapper(raw_resp=True)
    def bucket_exists(self, bucket_name: str, client: Union[Minio] = None):
        if not client:
            client = self.ensure_oss_client()
        return client.bucket_exists(bucket_name)

    @oss_wrapper(raw_resp=True)
    def create_bucket(self, bucket_name: str, client: Union[Minio] = None):
        if not client:
            client = self.ensure_oss_client()
        ret = client.bucket_exists(bucket_name)
        if ret:
            return ret
        try:
            client.make_bucket(bucket_name)
        except Exception as e:
            msg = f'对象存储: {bucket_name}创建失败: {ustr(e)}'
            _logger.error(msg)
            self.env.user.notify_danger(msg)
            return False
        return True

    @oss_wrapper(raw_resp=False)
    def put_oss_object(self, bucket_name: str, object_name: str, data: Union[bytes, str]):
        c = self.ensure_oss_client()
        if isinstance(data, str):
            data = data.encode('utf-8')
        length = len(data)
        f = io.BytesIO(data)
        return c.put_object(bucket_name, object_name, f, length)
