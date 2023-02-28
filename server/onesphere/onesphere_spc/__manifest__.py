# -*- coding: utf-8 -*-
{
    "name": "onesphere_spc",
    "summary": """
        通用SPC模块""",
    "description": """
        通用SPC模块
    """,
    "author": "上海文享数据科技有限公司",
    "website": "http://www.oneshare.com.cn",
    "category": "Manufacturing/Manufacturing",
    "version": "14.0.10.1",
    # any module necessary for this one to work correctly
    "depends": ["mrp"],
    # always loaded
    "data": [
        # 'security/ir.model.access.csv',
        "views/spc_menu_views.xml",
        "views/assets.xml",
    ],
    "qweb": [
        "static/xml/spc_view_template.xml",
    ],
    "application": True,
}
