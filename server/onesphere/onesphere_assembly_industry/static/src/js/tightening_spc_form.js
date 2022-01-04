odoo.define('onesphere.tightening.spc.view', function (require) {
    "use strict";

    const SPCViewerController = require('onesphere.spc.controller');
    var viewRegistry = require('web.view_registry');
    const SPCFormView = viewRegistry.get('spc_form');
    var Dialog = require('web.Dialog');

    var core = require('web.core');

    var _t = core._t;


    var TighteningSPCFormController = SPCViewerController.extend({
        _onButtonQuerySPC: function (ev) {
            var self = this;
            var query_date_from = self.renderer.state.data['query_date_from'];
            var query_date_to = self.renderer.state.data['query_date_to'];
            var query_type = self.renderer.state.data['measurement_type'] || 'torque';
            var usl = self.renderer.state.data['usl'] || 10.0;
            var lsl = self.renderer.state.data['lsl'] || 1.0;
            var limit = self.renderer.state.data['limit'] || 1000;
            var diff = query_date_to.diff(query_date_from);
            if (diff <= 0) {
                Dialog.alert(self, _t("Date Time Window Is Invalid!"), {
                    title: _t('Date Time Window Is Invalid'),
                });
                return;
            }
            var dd = _.map(this.renderer.state.fieldsInfo[this.viewType], function (val, field_name) {
                var required = val.required;
                if (!!!required) {
                    //非必填一定是有效
                    return {'field': field_name, 'isValid': true};
                }
                return {'field': field_name, 'isValid': required && self.renderer.state.data[field_name]};
            });
            try {
                var d = _.find(dd, function (v) {
                    return !v.isValid; //返回第一个无效
                });
                if (!!d) {
                    Dialog.alert(self, _t("Field Required: ") + d.field, {
                        title: _t('Field Required'),
                    });
                    return;
                }
            } catch (error) {

            }
            var others = {
                'model_object': self.renderer.state.data['model_object'],
                'model_object_field': self.renderer.state.data['model_object_field'],
                'spc_step': self.renderer.state.data['spc_step'] || 0.1,
            };

            this._rpc({
                model: 'onesphere.assy.industry.spc',
                method: 'query_spc',
                args: [query_date_from, query_date_to, query_type, usl, lsl, limit, others],
            }).then(function (result) {
                if (!!result.cmk) {
                    self.setData(self.handle, 'cmk', result.cmk);
                } else {
                    self.setData(self.handle, 'cmk', 0.0);
                }
                if (!!result.cpk) {
                    self.setData(self.handle, 'cpk', result.cpk);
                } else {
                    self.setData(self.handle, 'cpk', 0.0);
                }
                if (!!result.pages) {
                    // self.render_pages(result.pages);
                }
            });

        },
    });

    var TighteningSPCFormView = SPCFormView.extend({
        config: _.extend({}, SPCFormView.prototype.config, {
            Controller: TighteningSPCFormController,
        }),
    });

    viewRegistry.add('tightening_spc_form', TighteningSPCFormView);

});

