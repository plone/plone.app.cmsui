/*
    Set up javascript required for history panel
*/

/*jslint white:false, onevar:true, undef:true, nomen:true, eqeqeq:true,
  plusplus:true, bitwise:true, regexp:true, newcap:true, immed:true,
  strict:false, browser:true */
/*global jQuery:false, document:false, window:false, location:false */

jQuery(function ($) {

    // Ctrl-clicking means change which version to diff against
    $('div.history-timeline a').live('click', function(e) {
        if(e.ctrlKey) {
            console.log("Ctrl-click detected");
            return e.preventDefault();
        }
    });

});
