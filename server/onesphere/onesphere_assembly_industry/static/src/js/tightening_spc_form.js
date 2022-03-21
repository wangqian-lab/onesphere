odoo.define('onesphere.tightening.spc.view', function (require) {
    "use strict";

    const SPCViewerController = require('onesphere.spc.controller');
    var viewRegistry = require('web.view_registry');
    const SPCFormView = require('onesphere.spc.view');
    var Dialog = require('web.Dialog');

    var core = require('web.core');

    var _t = core._t;
    var FormRenderingEngine = require('web.FormRenderer');
    let renderChart = null;
    let chartsData = null;
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

            self.render_pages =function(pages){
            _.map(pages, function (opts, selection) {
                var sel = 'div.' + selection;
                var ele = self.$el.find(sel).get(0);
                if (!!ele) {
                    // 找到这个echarts DOM元素
                    const charts = echarts.getInstanceByDom(ele);
                    charts.setOption(opts, {notMerge: false}); // 如果有的话会删除之前所有的option
                    charts.resize();
                    }
                });
            },
            renderChart = self.render_pages;
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
                chartsData = result.pages;
                    self.render_pages(result.pages);
                }
            });

        },
    });

    var SPCViewerRenderer = FormRenderingEngine.extend({
        _renderTabPage: function (page, page_id) {
            var self = this;
            var $result = this._super.apply(this, arguments);
            $result.css({width: '100%'});
            var $container = $result.get(0).firstChild;
            var chart = echarts.init($container, null, {height: 600});
            $(window).resize(function () {
                chart.resize();
            });
            $result.one('shown.bs.tab', function () {
                var activeTab = $(this);
                // var tab = activeTab.get(0);
                var href = activeTab.attr('href'); //為id
                var ele = $new_notebook.find(href).get(0);
                var chart = echarts.getInstanceByDom(ele);
                chart.resize();
            });
            return $result;
        },

         _onNotebookTabChanged: function (evt) {
            if(renderChart){renderChart(chartsData);}
//             var activeTab = evt;
//             // var tab = activeTab.get(0);
//             var href = activeTab.attr('href'); //為id
//             var ele =  $new_notebook.find(href).get(0);
//             var chart = echarts.getInstanceByDom(ele);
//             chart.resize();
//             this._super.apply(this, arguments);
         },

    });
    var TighteningSPCFormView = SPCFormView.extend({
        config: _.extend({}, SPCFormView.prototype.config, {
            Controller: TighteningSPCFormController,
            Renderer: SPCViewerRenderer
        }),
    });

    viewRegistry.add('tightening_spc_form', TighteningSPCFormView);

});

