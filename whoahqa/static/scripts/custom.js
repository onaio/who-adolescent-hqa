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

    var ENTER_KEY_CODE = 13;
    var filterClinicTable = function() {
        $("#search_term").keypress(function(e) {
            var search_term, filter_url;
            if (e.which == ENTER_KEY_CODE) {
                search_term = $("#search_term").val();
                filter_url = "?search="+search_term
                $.ajax({
                    type: "GET",
                    url: filter_url
                })
                .done(function( msg ) {
                    $(".clinics_table").html(msg);
                });
            }
        });
    }

    var getParameterByName = function (name) {
        name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
        var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
        return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
    }

    var filterCharacteristics = function () {
        var type_value = location.search.replace('?', '').split('=')[1]
        $('#charactersictic_type').on('change', function (e) {
            var valueSelected = this.value;
            window.location = '?char_type=' + valueSelected;
        });
        var type_value = getParameterByName('char_type')
        $('#charactersictic_type').val(type_value)

    }

    var userFormValidation = function() {
        $('select[name=group]').on('change', function(e){
            value = this.value
            $('select[name!=group]').closest('div.form-group').hide();
            if(value === 'municipality_manager'){
                $('select[name=municipality]').closest('div.form-group').show();
            } else if(value === 'state_official'){
                $('select[name=state]').closest('div.form-group').show();
            } else {
                $('select[name=clinic]').closest('div.form-group').show();
            }
        });
    }

    return {
        addCheckAllListener: addCheckAllListener,
        enableDatatables: enableDatatables,
        filterClinicTable:filterClinicTable,
        filterCharacteristics: filterCharacteristics,
        userFormValidation: userFormValidation
    }
}();

/***
Usage
***/
//Custom.init();
//Custom.doSomeStuff();