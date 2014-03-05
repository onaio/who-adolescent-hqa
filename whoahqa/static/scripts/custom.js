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

       $.fn.fixheader = function (){
          return this.each(function() {
             var $this = $(this),
                $t_fixed;
             function init() {
                $this.wrap('<div class="container" />');
                $t_fixed = $this.clone();
                $t_fixed.find("tbody").remove().end().addClass("fixed").insertBefore($this);
                resizeFixed();
             }
             function resizeFixed() {
                $t_fixed.find("th").each(function(index) {
                   $(this).css("width",$this.find("th").eq(index).outerWidth()+"px");
                });
             }
             function scrollFixed() {
                var offset = $(this).scrollTop(),
                tableOffsetTop = $this.offset().top,
                tableOffsetBottom = tableOffsetTop + $this.height() - $this.find("thead").height();
                if(offset < tableOffsetTop || offset > tableOffsetBottom)
                   $t_fixed.hide();
                else if(offset >= tableOffsetTop && offset <= tableOffsetBottom && $t_fixed.is(":hidden"))
                   $t_fixed.show();
             }
             $(window).resize(resizeFixed);
             $(window).scroll(scrollFixed);
             init();
          });
       };
       $(".characteristics").fixheader();
       $(".score_indicators").fixheader();

       var leftInit = $(".fixed").offset().left;
       var initialLeftint = $(".score-summary-table2").offset().left +2;

      // var top = $('.score-summary-table2 .fixed').offset().top - parseFloat($('.fixed').css('margin-top').replace(/auto/, 0));

       $('.score-summary-table2').scroll(function(event) {
            var x = initialLeftint - $(this).scrollLeft();
            var y = $(this).scrollTop();

            // whether that's below the form
            if (y >= top) {
                // if so, ad the fixed class
               $('.score-summary-table2 .fixed').addClass('.fixed');
            } else {
                // otherwise remove it
                $('.score-summary-table2 .fixed').removeClass('.fixed');
            }

            $(".score-summary-table2 .fixed").offset({
                left: x + leftInit
            });
        });

    };

    var filterClinicTable = function() {
        $("#search_term").keypress(function(e) {
            if(e.which == 13) {
                search_term = $("#search_term").val();
                $.ajax({
                    type: "POST",
                    url: "/clinics/filterclinics",
                    data: {st: search_term }
                })
                .done(function( msg ) {
                    $(".clinics_table").html(msg);
                });
            }
        });
    }
    return {
        addCheckAllListener: addCheckAllListener,
        enablefloatThead: enablefloatThead,
        filterClinicTable:filterClinicTable
    }
}();

/***
Usage
***/
//Custom.init();
//Custom.doSomeStuff();