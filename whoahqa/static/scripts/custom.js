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

    var enablefloatThead = function() {
        $(document).ready(function() {
            var oTable = $('#score_summary').dataTable( {
 	                        "sScrollX": "100%",
                            "sScrollY": "300px",
 		                    "bScrollCollapse": true,
 		                    "bPaginate": false,
 		                    "bInfo":false,
                            "bFilter": false,

 	                        } );
 	        new FixedColumns( oTable, {
 		            "iLeftColumns": 2,
		            "iLeftWidth": 500
 	        } );
		} );
    };

    return {
        addCheckAllListener: addCheckAllListener,
        enablefloatThead: enablefloatThead
    }
}();

/***
Usage
***/
//Custom.init();
//Custom.doSomeStuff();