document.addEventListener('DOMContentLoaded', function () {
   var input = document.getElementById('locale');
   if (localStorage['locale']) { // if locale is set
       input.value = localStorage['locale']; // set the value
       if (input.value == 'en') {
       	 $("button#update").text("Update")
       	 $("a#cancel").text("Cancel")
       }
       if (input.value == 'pt') {
       	 $("button#update").text("Atualizar")
       	 $("a#cancel").text("Cancelar")
       }
   }
   input.onchange = function () {
        localStorage['locale'] = this.value; // change localStorage on change
        if (this.value == 'en') {
       	 $("button#update").text("Update")
       	 $("a#cancel").text("Cancel")
       }
       if (this.value == 'pt') {
       	 $("button#update").text("Atualizar")
       	 $("a#cancel").text("Cancelar")
       }
    }
});