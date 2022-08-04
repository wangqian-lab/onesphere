# -*- coding: utf-8 -*-

import logging
import os
import tempfile
from distutils.util import strtobool
from odoo.tools import ustr
import docker
import werkzeug
from odoo.addons.oneshare_utils.zip import zip_dir
from odoo.addons.web.controllers.main import Database as webDatabaseController

from odoo import http

_logger = logging.getLogger(__name__)

ENV_DOCKER_URL = os.getenv('ENV_DOCKER_URL', 'unix://var/run/docker.sock')

ENV_BACKUP_WITH_MINIO = strtobool(os.getenv('ENV_BACKUP_WITH_MINIO', 'False'))
try:
    client = docker.DockerClient(base_url=ENV_DOCKER_URL)
except Exception as e:
    client = None
    _logger.error(f'初始化docker客户端错误: {ustr(e)}')


class Database(webDatabaseController):

    @http.route()
    def backup(self, master_pwd, name, backup_format='zip'):
        # request = http.request
        # platform = request.httprequest.user_agent.platform
        resp = super(Database, self).backup(master_pwd, name, backup_format)
        if not resp.is_streamed:
            return resp
        if not ENV_BACKUP_WITH_MINIO:
            return resp
        stream = resp.response
        minio_container = None
        if not client:
            _logger.error(f'请先初始化docker客户端')
            return resp
        containers = client.containers.list(filters={'status': 'running'})
        for container in containers:
            image_name = container.image.tags[0]
            if 'minio' in image_name:
                minio_container = container
                break
            _logger.info(f'{image_name}')
        if not minio_container:
            return resp
        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                c = client.containers.run('ubuntu', volumes_from=[minio_container.name], detach=True,
                                          volumes=[f'{tmp_dir}:/backup'],
                                          command='tar cvf /backup/backup.tar /data')
                exit_status = c.wait()['StatusCode']
                _logger.info(f'容器返回值: {exit_status}')
                c.remove()
            except Exception as e:
                pass
            zip_dir(tmp_dir, stream, mode='a', include_dir=False,
                    fnct_sort=lambda file_name: file_name != 'dump.sql')
            stream.seek(0)
        response = werkzeug.wrappers.Response(stream, headers=resp.headers, direct_passthrough=True)
        return response
