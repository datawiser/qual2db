var qualTable;
var sqlTable;
$(document).ready(function () {
    qualTable = $('#qualtrics-table').DataTable({
        "ajax": {
            "url": "/qualtricsSurveys",
            "dataSrc": ""
        },
        "rowId": "Qid",
        "columnDefs": [
            {
                "data": null,
                "defaultContent": '',
                "className": "select-checkbox",
                "targets": 0
            },
            {
                "data": "Name",
                "targets": 1
            }
        ],
        "select": {
            "style": "multi",
            "selector": "td:first-child"
        },
        "scrollY": "75vh",
        "scrollCollapse": false,
        "searching":true,
        "paging": false
    });

    sqlTable = $('#sql-table').DataTable({
        "ajax": {
            "url": "/sqlSurveys",
            "dataSrc": ""
        },
        "rowId": "Qid",
        "columnDefs": [
            {
                "data": null,
                "defaultContent": '',
                "className": "select-checkbox",
                "targets": 0
            },
            {
                "data": "Name",
                "targets": 1
            }
        ],
        "select": {
            "style": "multi",
            "selector": "td:first-child"
        },
        "scrollY": "75vh",
        "scrollCollapse": false,
        "searching":true,
        "paging": false
    });

    $('#qualtrics-table tbody, #sql-table tbody').on('click', 'tr', function () {
        $(this).toggleClass('selected');
    });

});

function SyncAll() {
    var qids = {};
    iter = 0;
    $('#qualtrics-table tr.selected').each(function () {
        qids[iter] = $(this).attr('id');
        iter += 1;
    });
    if (!$.isEmptyObject(qids)) {
        var jsonData = JSON.stringify(qids);
        $.ajax({
            type: 'POST',
            url: "/qualtricsSyncAll",
            contentType: "application/json",
            data: jsonData,
            dataType: "json",
            success: function (data) {
                sqlTable.ajax.reload();
                $('#qualtrics-table tr.selected').each(function () {
                    $('#qualtrics-table ' + '#' + $(this).attr('id')).removeClass('selected');
                });
            },
            failure: function (data) { }
        });
    }
}

function Schema() {
	var qids = {};
	iter = 0;
	$('#qualtrics-table tr.selected').each(function () {
		qids[iter] = $(this).attr('id');
		iter += 1;
	});
	if (!$.isEmptyObject(qids)) {
		var jsonData = JSON.stringify(qids);
		$.ajax({
			type: 'POST',
			url: "addQualtricsSurveySchema",
			contentType: "application/json",
			data: jsonData,
			dataType: "json",
            success: function (data) {
                sqlTable.ajax.reload();
                $('#qualtrics-table tr.selected').each(function () {
                    $('#qualtrics-table ' + '#' + $(this).attr('id')).removeClass('selected');
                });
            },
            failure: function (data) { }
		});
	}
}

function Data() {
	var qids = {};
	iter = 0;
    $('#qualtrics-table tr.selected').each(function () {
		qids[iter] = $(this).attr('id');
		iter += 1;
	});
	if (!$.isEmptyObject(qids)) {
		var jsonData = JSON.stringify(qids);
		$.ajax({
			type: 'POST',
			url: "addQualtricsSurveyData",
			contentType: "application/json",
			data: jsonData,
			dataType: "json",
            success: function (data) {
                sqlTable.ajax.reload();
                $('#qualtrics-table tr.selected').each(function () {
                    $('#qualtrics-table ' + '#' + $(this).attr('id')).removeClass('selected');
                    sqlTable.rows('#' + $(this).attr('id')).data()[0]["Responses"] = qualTable.rows('#' + $(this).attr('id')).data()[0]["Responses"];
                });
            },
			failure: function (data) { }
        });
    }
}

function Remove() {
	var qids = {};
	iter = 0;
	$('#sql-table tr.selected').each(function () {
		qids[iter] = $(this).attr('id');
		iter += 1;
	});
	if (!$.isEmptyObject(qids)) {
		var jsonData = JSON.stringify(qids);
		$.ajax({
			type: 'POST',
			url: "/removeSqlSurvey",
			contentType: "application/json",
			data: jsonData,
			dataType: "json",
            success: function (data) {
                sqlTable.ajax.reload();
				$('#sql-table tr.selected').each(function () {
                    $('#sql-table #' + $(this).attr('id')).removeClass('selected');
                    sqlTable.rows('#' + $(this).attr('id')).remove();
                });
			},
			failure: function (data) { }
        });
    }
}

function Clear() {
    var qids = {};
    iter = 0;
    $('#sql-table tr.selected').each(function () {
        qids[iter] = $(this).attr('id');
        iter += 1;
    });
    if (!$.isEmptyObject(qids)) {
        var jsonData = JSON.stringify(qids);
        $.ajax({
            type: 'POST',
            url: "/clearSqlSurveyData",
            contentType: "application/json",
            data: jsonData,
            dataType: "json",
            success: function (data) {
                sqlTable.ajax.reload();
                $('#sql-table tr.selected').each(function () {
                    $('#sql-table #' + $(this).attr('id')).removeClass('selected');
                    sqlTable.rows('#' + $(this).attr('id')).data()[0]["Responses"] = 0;
                });
            },
            failure: function (data) { }
        });
    }
}


function compareTables() {
    sqlTable.ajax.reload();
    sqlTable.rows().every(function (index) {
        var id = this.data()["Qid"];
        var sqlDate = this.data()["lastmodified"];
        var qualDate = qualTable.rows('#' + id).data()[0]["lastmodified"];
        if (sqlDate < qualDate) {
            setSchemaSync(id);
        } else if (sqlDate == qualDate) {
            var sqlResponses = this.data()["Responses"];
            var qualResponses = qualTable.rows('#' + id).data()[0]["Responses"];
            if (qualResponses > sqlResponses) {
                setDataSync(id);
            } else if (qualResponses == sqlResponses) {
                setSurveySync(id);
            }
        }
    });
}

setInterval(function () {
    qualTable.rows().every(function (index) {
        var id = this.data()["Qid"];
        var row = sqlTable.rows('#' + id).selector.cols;
        //var name = sqlTable.rows('#' + id).data()[0]["Name"];
        try {
            var qualDate = this.data()["lastmodified"];
            var sqlDate = sqlTable.rows('#' + id).data()[0]["lastmodified"];
            if (sqlDate < qualDate) {
                setSchemaSync(id);
            } else if (sqlDate == qualDate) {
                var qualResponses = this.data()["Responses"];
                var sqlResponses = sqlTable.rows('#' + id).data()[0]["Responses"];
                if (qualResponses > sqlResponses) {
                    setDataSync(id);
                } else if (qualResponses == sqlResponses) {
                    setSurveySync(id);
                }
            }
        } catch (err) {
            removeStatus(id);
        }
    });
}, 1000);

/**
 * These functions change the color of the box depending on the status of their import
 */
function setSchemaSync(qid) {
    $('#qualtrics-table ' + '#' + qid + " td:nth-child(5) div").removeClass();
    $('#qualtrics-table ' + '#' + qid + " td:nth-child(5) div").addClass('statusBox');
    $('#qualtrics-table ' + '#' + qid + " td:nth-child(5) div").addClass('schemaUpdateNeeded');
}
function setDataSync(qid) {
    $('#qualtrics-table ' + '#' + qid + " td:nth-child(5) div").removeClass();
    $('#qualtrics-table ' + '#' + qid + " td:nth-child(5) div").addClass('statusBox');
    $('#qualtrics-table ' + '#' + qid + " td:nth-child(5) div").addClass('dataUpdateNeeded');
}
function setSurveySync(qid) {
    $('#qualtrics-table ' + '#' + qid + " td:nth-child(5) div").removeClass();
    $('#qualtrics-table ' + '#' + qid + " td:nth-child(5) div").addClass('statusBox');
    $('#qualtrics-table ' + '#' + qid + " td:nth-child(5) div").addClass('uptodate');
}
function removeStatus(qid) {
    $('#qualtrics-table ' + '#' + qid + " td:nth-child(5) div").removeClass();
    $('#qualtrics-table ' + '#' + qid + " td:nth-child(5) div").addClass('statusBox');
}