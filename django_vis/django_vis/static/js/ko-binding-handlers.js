ko.bindingHandlers.selectedRows = {
    init: function (element, valueAccessor) {
        // maybe should throw an error if the element is not a datatable
        $(element).parent().on("selectionChanged", function () {
            var value, selectedData, tools;
            tools = TableTools.fnGetInstance($(element).parent().attr('id'));
            selectedData = tools.fnGetSelectedData();
            value = valueAccessor();
            value(selectedData);
        });
    },
    update: function (element, valueAccessor, allBindingsAccessor, viewModel) {
        var parent, tools, val, data, dt;
        parent = $(element).parent();
        tools = TableTools.fnGetInstance(parent.attr("id"));
        val = ko.unwrap(valueAccessor());
        data = viewModel.items();
        dt = parent.dataTable();
        for (var i = 0; i < val.length; ++i) {
            for (var j = 0; j < data.length; ++j) {
                if (_.isEqual(data[j], val[i])) tools.fnSelect(dt.fnGetNodes(j));
            }
        }
    }
};
ko.bindingHandlers.tableData = {
    init: function (element, valueAccessor) {
        var data, value;
        data = $(element).dataTable().fnGetData();
        value = valueAccessor();
        for (var i = 0; i < data.length; ++i) {
            value.push(data[i]);
        }
    },
    update: function (element, valueAccessor) {
        var val = ko.unwrap(valueAccessor());
        var dt = $(element).dataTable();
        dt.fnClearTable();
        dt.fnAddData(val);
    }
};
var selectedItem = function (element) {
    return $(element).wizard('selectedItem').step;
};
ko.bindingHandlers.wizardStep = {
    init: function (element, valueAccessor) {
        $(element).on('changed', function () {
            var value = valueAccessor();
            value(selectedItem(element));
        });
    },
    update: function (element, valueAccessor) {
        var tryNext, value, val;
        tryNext = function (direction) {
            var curVal;
            curVal = selectedItem(element);
            if (direction) $(element).wizard('next');
            else $(element).wizard('previous');
            return curVal != selectedItem(element);
        };
        value = valueAccessor();
        val = ko.unwrap(value);
        while (val > selectedItem(element)) if (!tryNext(true)) break;
        while (val < selectedItem(element)) if (!tryNext(false)) break;
        value(selectedItem(element));
    }
};
