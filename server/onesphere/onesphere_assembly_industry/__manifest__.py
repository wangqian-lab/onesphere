# -*- coding: utf-8 -*-
{
    'name': "onesphere_assembly_industry",

    'summary': """
        智能装配行业扩展模块""",

    'description': """
        智能装配行业扩展模块
    """,

    'author': "上海文享信息科技有限公司",
    'website': "http://www.oneshare.com.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacturing/Manufacturing',
    'version': '14.0.10.1',

    # any module necessary for this one to work correctly
    'depends': ['onesphere_mdm', 'onesphere_oss', 'web_image_editor', 'web_notify', 'onesphere_spc', 'web_echarts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/product_data.xml',
        'data/maintenance_category_data.xml',
        'data/quality_data.xml',
        'data/tightening_data.xml',
        'data/tightening_vendor_data.xml',
        'data/product_category_data.xml',
        'data/template_download_data.xml',
        'wizards/oneshare_modal.xml',
        'wizards/assembly_industry_spc_views.xml',
        'views/maintenance_views.xml',
        'views/tightening_result_views.xml',
        'views/templates.xml',
        'views/tightening_unit_views.xml',
        'views/quality_views.xml',
        'views/work_step_tag_views.xml',
        'views/tightening_bolt_views.xml',
        'views/mdm_menu_views.xml',
        'views/mrp_routing_workcenter_views.xml',
        # 'views/real_oper_version_views.xml',
        'views/mrp_bom.xml',
        'views/assembly_industry_menuitem.xml',
        'views/group_tightening_tool.xml',
        'views/res_config_settings_views.xml',
        'wizards/import_view.xml',
        'wizards/multi_update_wizard.xml',
        'views/import_menu_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/maintenance_equipment_demo.xml',
        'demo/tightening_bolt_demo.xml',
        'demo/tightening_unit_demo.xml',
        'demo/tightening_result_demo.xml',
    ],
    'qweb': [
        'static/xml/template.xml',
    ],
    'application': True,
}
