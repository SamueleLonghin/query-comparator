const RAW = false;
$.get("consegne.json", function (consegne) {

    $.get("result.json", function (data) {
        console.log(data)
        data.forEach((model) => {
            let div = $("<div id='d-" + model.id + "' class='card " + (model.status == 'err' ? 'bg-warning' : (model.status == 'div' ? 'bg-info' : '')) + "'> <h2>" + model.id + "</h2></div>");

            let link = $('<a class="btn btn-secondary btn-lg btn-block text-wrap" data-bs-toggle="collapse" href="#container-' + model.id + '" role="button" aria-expanded="false" aria-controls="multiCollapseExample1" style="margin-bottom:4px;white-space: normal;">')
                .append($("<p>").text(consegne[model.id - 1]));

            div.append(link);

            let querys = $("<div class='row ' id='query-" + model.id + "'></div>");
            let results = $("<div class='row' id='result-" + model.id + "'>");
            let diffs = $("<div class='row' id='diffs-" + model.id + "'>");
            let container = $("<div class='container collapse' id='container-" + model.id + "'>");
            let div_error = $("<div id='error-" + model.id + "' class=''>" + (model.status == 'err' ? model.error : '') + "</div>")


            Object.keys(model.content).forEach(key => {
                let element = model.content[key]
                console.log(element)
                let query_E = element.query;
                // query_E = query_E.replaceAll("select", "<span class='select'>SELECT</span>")
                // query_E = query_E.replaceAll("from", "<span class='from'>FROM</span>")
                // query_E = query_E.replaceAll("join", "<span class='join'>JOIN</span>")
                // query_E = query_E.replaceAll("inner", "<span class='join'>INNER</span>")
                // query_E = query_E.replaceAll("left", "<span class='join'>LEFT</span>")
                // query_E = query_E.replaceAll("right", "<span class='join'>RIGHT</span>")
                // query_E = query_E.replaceAll("table", "<span class='join'>TABLE</span>")
                // query_E = query_E.replaceAll("view", "<span class='join'>VIEW</span>")
                // query_E = query_E.replaceAll("temp", "<span class='join'>TEMP</span>")
                // query_E = query_E.replaceAll("create", "<span class='join'>CREATE</span>")
                // query_E = query_E.replaceAll("drop", "<span class='join'>DROP</span>")

                // query_E = query_E.replaceAll("max(", "<span class='functions'>max</span>(")
                // query_E = query_E.replaceAll("min(", "<span class='functions'>min</span>(")
                // query_E = query_E.replaceAll("count(", "<span class='functions'>count</span>(")
                // query_E = query_E.replaceAll("avg(", "<span class='functions'>avg</span>(")
                query_E = hljs.highlight(query_E, { language: 'sql' }).value

                query_E = query_E.replaceAll(";", ";<br> <br>");

                let container_query_E = $("<div id='d-E-" + model.id + "' class='col query'>" + query_E + "</div>")
                querys.append(container_query_E);
                let result_E;
                let length_res_E = element.result ? element.result.length : 0;
                let div_result_E;
                if (RAW) {
                    result_E = JSON.stringify(element.result, null, 2);
                    div_result_E = $("<div id='d-E-" + model.id + "' class='col '>" + result_E + " <br><b>count: " + length_res_E + "</b></div>")
                } else {
                    result_E = generaTabella(element.result);
                    div_result_E = $("<div id='d-E-" + model.id + "' class='col '> <br><b>count: " + length_res_E + "</b></div>");
                    div_result_E.append(result_E);
                }
                results.append(div_result_E);
                if (element.diff) {
                    let diff_E = JSON.stringify(element.diff, null, 2);
                    let length_diff_E = element.diff ? element.diff.length : 0;
                    let div_diff_E = $("<div id='diff-E-" + model.id + "' class='col '>" + diff_E + " <br><b>count: " + length_diff_E + "</b></div>")
                    diffs.append(div_diff_E);
                }
            });



            container.append(querys);
            container.append(results);
            container.append(diffs);
            container.append(div_error);

            div.append(container);

            $("#root").append(div);
        })
    });

});

function generaTabella(json) {
    let table = $("<table class='table table-striped table-bordered'>");
    let thead = $("<thead>");
    let tbody = $("<tbody>");
    table.append(thead);
    table.append(tbody);
    var columnSet = [];
    var headerTr$ = $('<tr/>');

    for (var i = 0; i < json.length; i++) {
        var rowHash = json[i];
        for (var key in rowHash) {
            if ($.inArray(key, columnSet) == -1) {
                columnSet.push(key);
                if (parseInt(key) > 10)
                    headerTr$.append($('<th/>').html(key));
                console.log(key)
            }
        }
    }
    thead.append(headerTr$);
    var columns = columnSet;

    for (var i = 0; i < json.length; i++) {
        var row$ = $('<tr/>');
        for (var colIndex = 0; colIndex < columns.length; colIndex++) {
            var cellValue = json[i][columns[colIndex]];
            if (cellValue == null) cellValue = "";
            row$.append($('<td/>').html(cellValue));
        }
        tbody.append(row$);
    }

    return table;
}
