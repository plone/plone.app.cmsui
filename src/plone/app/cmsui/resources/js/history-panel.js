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
        var url = $(this).attr("href");
        if(e.ctrlKey) {
            var sel_to = $('div.history-timeline a.sel_to');
            var results = new RegExp('sel_to=([0-9]+)').exec($(this).attr("href"));
            url = sel_to.attr("href") + "&sel_from=" + results[1];
        }
        
        $(this).closest('#overlay-content').loadOverlay(url + ' ' + common_content_filter);
        return false;
    });

});
