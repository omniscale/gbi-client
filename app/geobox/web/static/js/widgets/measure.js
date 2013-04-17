gbi.widgets = gbi.widgets || {};

gbi.widgets.Measure = function(editor, options) {
    var self = this;
    var defaults = {
        element: 'measurement',
    };
    this.options = $.extend({}, defaults, options);
    this.element = $('#' + this.options.element);

    this.render();

    this.toolbar = new gbi.Toolbar(editor, {
        tools : {},
        element: 'measure_toolbar'
    });

    this.pointMeasure = new gbi.Controls.Measure({
            measureType: gbi.Controls.Measure.TYPE_POINT,
            mapSRS: editor.map.olMap.projection.projCode,
            displaySRS: this.options.srs[0]
        }, function(event) { self.measureHandler(event); });
    this.pointMeasure.registerEvent('activate', this, function() {
        $('#position_srs').show();
        $("#measure-output").empty();
    });

    this.pointMeasure.registerEvent('deactivate', this, function() {
        $('#position_srs').hide();
        $("#measure-output").empty();
    });

    this.lineMeasure = new gbi.Controls.Measure({
            measureType: gbi.Controls.Measure.TYPE_LINE
        }, function(event) { self.measureHandler(event); });

    this.polygonMeasure = new gbi.Controls.Measure({
            measureType: gbi.Controls.Measure.TYPE_POLYGON
        }, function(event) { self.measureHandler(event); });

    this.toolbar.addControls([this.pointMeasure, this.lineMeasure, this.polygonMeasure]);

    $('#position_srs').change(function() {
        self.pointMeasure.updateSRS($(this).val());
    });

};
gbi.widgets.Measure.prototype = {
    render: function() {
        this.element.append(tmpl(gbi.widgets.Measure.template, {srs: this.options.srs}));
    },
    measureHandler: function(measure) {
        var element = $('#measure-output');
        var output = OpenLayers.i18n('measureResult')+': ';
        switch(measure.type) {
            case gbi.Controls.Measure.TYPE_POINT:
                var output = OpenLayers.i18n('coords')+': ';
                output += measure.measure[0] + ', ' + measure.measure[1];
                break;
            case gbi.Controls.Measure.TYPE_LINE:
                output += measure.measure + " " + measure.units;
                break;
            case gbi.Controls.Measure.TYPE_POLYGON:
                output += measure.measure + " " + measure.units + "<sup>2</sup>";
        }
        element.html(output);
    }
};
gbi.widgets.Measure.template = '\
    <div id="measure_toolbar" class="span12"></div>\
    <div class="span11"> \
        <hr> \
        <select id="position_srs" style="display:none;">\
        <% for(var i=0; i < srs.length; i++) { %>\
            <option value="<%=srs[i]%>"><%=srs[i]%></option>\
        <% } %>\
        </select>\
    </div>\
';