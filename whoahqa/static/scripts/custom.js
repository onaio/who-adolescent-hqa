/**
Custom module for you to write your own javascript functions
**/
var Custom = function () {

    // private functions & variables

    var addCheckAllListener = function(text) {
        $('.group-checkable').change(function () {
            var set = $(this).attr("data-set");
            var checked = $(this).is(":checked");
            $(set).each(function () {
                if (checked) {
                    $(this).attr("checked", true);
                } else {
                    $(this).attr("checked", false);
                }
                $(this).parents('tr').toggleClass("active");
            });
            $.uniform.update(set);

        });
    };

    var enableDatatables = function() {
		$(document).ready(function() {
            var oTable = $('#score_summary_compare').dataTable( {
 	                        "sScrollX": "100%",
                            "sScrollY": "300px",
 		                    "bScrollCollapse": true,
 		                    "bPaginate": false,
 		                    "bInfo":false,
                            "bFilter": false,
                            "bSortable":false,
                            "aaSorting": []
 	                        } );
 	        new FixedColumns( oTable, {
 		            "iLeftColumns": 2,
		            "iLeftWidth": 300
 	        } );

            $('.score').tooltip()
		} )
    };
    return {
        addCheckAllListener: addCheckAllListener,
        enableDatatables: enableDatatables
    }
}();

/***
Usage
***/
//Custom.init();
//Custom.doSomeStuff();