/*globals window, jQuery*/

/* Code that runs inside the iframe menu
 */

(function ($) {
    $().ready(function () {
        var iframe = $('#plone-cmsui-menu', window.parent.document);
        $('a.overlayLink').prepOverlay({
            subtype: 'ajax',
            filter: common_content_filter
            });

        iframe.height('100%');
        $(window.parent.document.body).css('overflow', 'hidden');
        //iframe.height($('#visual-portal-wrapper').height());

    });
}(jQuery));
