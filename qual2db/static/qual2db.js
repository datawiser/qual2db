$(document).ready(function () {
    $('#qualtrics-table').DataTable( {
        "scrollY": "100vh",
        "scrollCollapse": false,
        "paging": false,
        "searching": true,

        columDefs: [
            {
                targets: -1,
                className: 'dt-body-nowrap',
                className: 'dt-compact',
                className: 'dt-cell-border',
            }
        ]
    } );
});

$(document).ready(function () {
    $('#exported-table').DataTable({
        "scrollY": "76vh",
        "scrollCollapse": false,
        "paging": false,
        "searching":true,
    });
});

function loadSpinner() {
    document.getElementById('loader').style.display = "block";
}
