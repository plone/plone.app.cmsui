/*globals window, jQuery*/

/* Code that runs inside the iframe menu
 */

function expandMenu() {
    var offset = $(window.parent).scrollTop();
    $('body', window.parent.document).css('overflow', 'hidden');
    $(window.parent).scrollTop(offset);
    $('#plone-cmsui-menu', window.parent.document).css('height', '100%');
    return offset;
}
function contractMenu(offset) {
    $('body', window.parent.document).css('overflow', 'auto');
    $(window.parent).scrollTop(offset);
    $('#plone-cmsui-menu', window.parent.document).css('height', '139px');
}
 
(function ($) {
    $().ready(function () {
        var iframe = $('#plone-cmsui-menu', window.parent.document);
        var offset;

        $('a.overlayLink').prepOverlay({
            subtype: 'ajax',
            filter: common_content_filter,
            config: { 
                top: 150,
                onBeforeLoad: function (e) { 
                    offset = expandMenu();
                    return true; 
                },
                onClose: function (e) { 
                    contractMenu(offset);
                    return true; 
                } 
            } 
        });

        // iframe.height($('#visual-portal-wrapper').outerHeight());

    });
}(jQuery));
