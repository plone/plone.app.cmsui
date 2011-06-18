/* Code that runs inside the iframe menu
 */

(function ($) {
    var cmsui = window.parent.cmsui;
    cmsui.overlay.close(function () {
        
        // TODO
        
    });
    $().ready(function() {
        $('a.overlayLink').click(function (e) {
            var link = $(this);
            cmsui.overlay.open(link.attr('href'), function () {
            });
            return false;
        })

    });
}(jQuery));
