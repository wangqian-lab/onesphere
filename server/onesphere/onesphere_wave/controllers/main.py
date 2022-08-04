# -*- coding: utf-8 -*-

import logging
import os
import tempfile
import zipfile

import docker
import werkzeug
from distutils.util import strtobool
from odoo.addons.web.controllers.main import Database as webDatabaseController

from odoo import http

ENV_DOCKER_URL = os.getenv('ENV_DOCKER_URL', 'unix://var/run/docker.sock')

ENV_BACKUP_WITH_MINIO = strtobool(os.getenv('ENV_BACKUP_WITH_MINIO', 'False'))

client = docker.DockerClient(base_url=ENV_DOCKER_URL)

_logger = logging.getLogger(__name__)


def zip_dir(path, stream, mode='w', include_dir=True, fnct_sort=None):  # TODO add ignore list
    """
    : param fnct_sort : Function to be passed to "key" parameter of built-in
                        python sorted() to provide flexibility of sorting files
                        inside ZIP archive according to specific requirements.
    """
    path = os.path.normpath(path)
    len_prefix = len(os.path.dirname(path)) if include_dir else len(path)
    if len_prefix:
        len_prefix += 1

    with zipfile.ZipFile(stream, mode, compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zipf:
        for dirpath, dirnames, filenames in os.walk(path):
            filenames = sorted(filenames, key=fnct_sort)
            for fname in filenames:
                bname, ext = os.path.splitext(fname)
                ext = ext or bname
                if ext not in ['.pyc', '.pyo', '.swp', '.DS_Store']:
                    path = os.path.normpath(os.path.join(dirpath, fname))
                    if os.path.isfile(path):
                        zipf.write(path, path[len_prefix:])


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
