odoo.define('onesphere.spc.view', function (require) {
    "use strict";

    var FormView = require('web.FormView');
    const FormRenderer = require("web.FormRenderer");
    const SPCViewerController = require('onesphere.spc.controller');
    var viewRegistry = require('web.view_registry');


    var SPCViewerRenderer = FormRenderer.extend({
        _renderTabPage: function (page, page_id) {
            var self = this;
            var $result = this._super.apply(this, arguments);
            $result.css({width: '100%'});
            var native_page = $result.get(0);
            var chart = echarts.init(native_page, null, {height: 600});
            $(window).resize(function () {
                chart.resize();
            });
            return $result;
        },
        // _onNotebookTabChanged: function (evt) {
        //     var activeTab = evt;
        //     // var tab = activeTab.get(0);
        //     var href = activeTab.attr('href'); //為id
        //     var ele = activeTab.find(href).get(0);
        //     var chart = echarts.getInstanceByDom(ele);
        //     chart.resize();
        //     this._super.apply(this, arguments);
        // },
    });


    var SPCFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: SPCViewerController,
            Renderer: SPCViewerRenderer,
        }),
    });

    viewRegistry.add('spc_form', SPCFormView);

});