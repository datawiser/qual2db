
var qualTable;
var sqlTable;
$(document).ready(function () {
	qualTable = $('#qualtrics-table').DataTable({ //, #sql-table
		"ajax": {
			"url": "/qualtricsSurveys",
			"dataSrc": ""
		},
		//"processing": true,
		"rowId": "Qid",
		"columnDefs": [
			{
				"data": null,
				"defaultContent": '',
				"className": "select-checkbox",
				"targets":   0
			},
			{
				"data": "Name",
				"targets": 1
			},
			{
				"data": "Active",
				"targets": 2
			},
			{
				"data": "Responses",
				"targets": 3
			},
			{
				"data": "Indatabase",
				"targets": 4
			}
		],
        "select": {
            "style":    "multi",
            "selector": "td:first-child"
        },
		"scrollY": "600px",
        //"scrollCollapse": true, //collapses table to match data height
		"paging": 	false
	});

	sqlTable = $('#sql-table').DataTable({ //, #sql-table
		"ajax": {
			"url": "/sqlSurveys",
			"dataSrc": ""
		},
		//"processing": true,
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
			},
			{
				"data": "Active",
				"targets": 2
			},
			{
				"data": "Responses",
				"targets": 3
			},
			{
				"data": "Indatabase",
				"targets": 4
			}
		],
		"select": {
			"style": "multi",
			"selector": "td:first-child"
		},
		"scrollY": "600px",
		//"scrollCollapse": true, //collapses table to match data height
		"paging": false
	});

    $('#qualtrics-table tbody, #sql-table tbody').on( 'click', 'tr', function () {
        $(this).toggleClass('selected');
    } );
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
/*
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
			success: function (data) { },
			failure: function (data) { }
		});
		$('#sql-table').ajax.reload();
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
			success: function (data) { },
			failure: function (data) { }
		});
		$('#sql-table').ajax.reload();
	}
}*/

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
				$('#qualtrics-table tr.selected').each(function () {
					alert($(this).attr('id'));
					$('#qualtrics-table ' + '#' + $(this).attr('id')).removeClass('selected');
				});
			},
			failure: function (data) { }
		});
	}
}