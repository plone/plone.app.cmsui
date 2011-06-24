/*globals window, jQuery*/

/* Code that runs inside the iframe menu
 */

(function ($) {
    var cmsui = window.parent.cmsui;
    cmsui.overlay.close(function () {

        // TODO

    });
    $().ready(function () {
        $('#document-info a, #folder-actions a, #site-setup a').click(function (e) {
            var link = $(this);
            cmsui.overlay.open(link.attr('href'), function () {
            });
            e.preventDefault();
        });

    });
}(jQuery));
