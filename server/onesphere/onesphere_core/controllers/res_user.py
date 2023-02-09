# -*- coding: utf-8 -*-
from odoo import http, SUPERUSER_ID, api
from odoo.http import request, Response
from http import HTTPStatus
import odoo
import json
from odoo.addons.web.controllers.main import ensure_db
from odoo.addons.onesphere_core.constants import DEFAULT_LIMIT


class UsersAPI(http.Controller):
    @http.api_route('/api/v1/res.users', type='apijson', auth='none', cors='*', csrf=False)
    def _get_users_list_info(self, **query_params):
        _limit = DEFAULT_LIMIT
        if 'limit' in query_params:
            _limit = int(query_params['limit'])
        domain = [('id', '!=', 1)]
        if 'uuids' in query_params:
            uuids = query_params['uuids'].split(',')
            domain += [('uuid', 'in', uuids)]
        user_ids = request.env['res.users'].sudo().with_context(active_test=False).search(domain, limit=_limit)
        ret = []
        if not user_ids:
            return Response(json.dumps({'msg': 'User not found'}), headers={'content-type': 'application/json'},
                            status=HTTPStatus.BAD_REQUEST)
        for user_id in user_ids:
            ret.append(self.pack_user_info(user_id))
        return Response(json.dumps(ret), headers={'content-type': 'application/json'}, status=HTTPStatus.OK)

    @staticmethod
    def pack_user_info(user_id):
        img_base64 = user_id.partner_id.image_128.decode() if user_id.partner_id.image_128 else ""
        ret = {
            'id': user_id.id,
            'name': user_id.name,
            'login': user_id.login,
            'status': 'active' if user_id.active else 'archived',
            'uuid': user_id.uuid,
            'hmi_role': user_id.hmi_role_id.code if user_id.hmi_role_id else 'anonymous',
            'image_small': f'data:image/png;base64,{img_base64}'
        }
        if not user_id.active:
            ret.update({
                'hmi_role': 'anonymous'
            })
        return ret

    @http.api_route('/api/v1/res.users/<string:uuid>', type='apijson', auth='none', cors='*', csrf=False)
    def _get_user_info(self, uuid):

        user_id = request.env['res.users'].sudo().with_context(active_test=False).search([('uuid', '=', uuid)], limit=1)

        if not user_id:
            return Response(json.dumps({'msg': 'User not found'}), headers={'content-type': 'application/json'},
                            status=HTTPStatus.BAD_REQUEST)

        ret = self.pack_user_info(user_id)

        return Response(json.dumps(ret), headers={'content-type': 'application/json'}, status=HTTPStatus.OK)

    @http.api_route('/api/v1/res.users/login', type='apijson', auth='none', cors='*', csrf=False)
    def _login(self):
        params = request.ApiJsonRequest
        login = params.get('login')
        password = params.get('password')
        ensure_db()
        if not request.session.db:
            return Response(json.dumps({'msg': 'Database not found'}), headers={'content-type': 'application/json'},
                            status=HTTPStatus.BAD_REQUEST)
        db = request.session.db
        res_users = odoo.registry(db)['res.users']
        wsgienv = request.httprequest.environ
        env = dict(
            interactive=False,
            base_location=request.httprequest.url_root.rstrip('/'),
            HTTP_HOST=wsgienv['HTTP_HOST'],
            REMOTE_ADDR=wsgienv['REMOTE_ADDR'],
        )
        uid = res_users._login(db, login, password, env)
        if not uid:
            return Response(json.dumps({'msg': 'User Auth Fail'}), headers={'content-type': 'application/json'},
                            status=HTTPStatus.BAD_REQUEST)

        user_id = request.env['res.users'].sudo().with_context(active_test=False).browse(uid)

        ret = self.pack_user_info(user_id)

        return Response(json.dumps(ret), headers={'content-type': 'application/json'}, status=HTTPStatus.OK)

    @http.api_route('/api/v1/res.users/batch_archived', type='apijson', auth='none', cors='*', csrf=False)
    def _bach_patch_user_archived(self, **query_params):
        uuids = query_params['uuids'].split(',') if query_params.get('uuids','') else []
        user_ids = request.env['res.users'].sudo().search([('uuid', 'in', uuids)])

        if not user_ids:
            return Response(json.dumps({'msg': 'User not found'}), headers={'content-type': 'application/json'},
                            status=HTTPStatus.NOT_FOUND)

        ret = user_ids.sudo().write({
            'active': False
        })
        if not ret:
            return Response(json.dumps({'msg': 'Batch Archived fail'}), headers={'content-type': 'application/json'},
                            status=HTTPStatus.METHOD_NOT_ALLOWED)
        ret = self.pack_user_info(user_ids[0])
        return Response(json.dumps(ret), headers={'content-type': 'application/json'}, status=HTTPStatus.OK)
