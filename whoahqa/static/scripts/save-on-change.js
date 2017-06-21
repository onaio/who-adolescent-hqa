document.addEventListener('DOMContentLoaded', function () {
   var input = document.getElementById('locale');
   if (localStorage['locale']) { // if locale is set
       input.value = localStorage['locale']; // set the value
   }
   input.onchange = function () {
        localStorage['locale'] = this.value; // change localStorage on change
    }
});