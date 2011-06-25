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
		    $("#listing-table").ploneDnD();
                    return true; 
                },
                onClose: function (e) { 
                    contractMenu(offset);
                    return true; 
                }
            } 
        });

        // iframe.height($('#visual-portal-wrapper').outerHeight());
        // ------ Structure dialog navigation -------
        
        var overlay_location = $('#structure a').attr('href');
        window.parent.history.replaceState({structure_href: overlay_location}, null, window.parent.location.href);

        var slideTo = function(href, dir) {
            var $slider = $('.structure-slider');
            var width = $slider.outerWidth();

            $('#structure-dialog').css({height: $slider.outerHeight()});
            $('<div class="structure-slider" style="width: 100%"><' + '/div>')
                .prependTo($('#structure-dialog'))
                .load(href + ' .structure-slider>*')
                .css({position: 'absolute', left: (dir=='left'?width:-width), top: 0})
                .animate({'left': 0}, 200, function() {$('.structure-slider').css('position', 'static'); $('#structure-dialog').css('height', 'auto');});
	    $slider.css('position', 'relative').animate({'left': (dir=='left')?-width:width}, 200, null, function(){
		$slider.remove();
		$("#listing-table").ploneDnD();
	    });
            overlay_location = href;
        }

        $('#structure-dialog a.link-child').live('click', function(e) {
            e.preventDefault();
            var href = $(this).attr('href');
            slideTo(href, 'left');
            window.parent.history.pushState({structure_href: href}, null, window.parent.location.href);
        });

        $('#structure-dialog a.link-parent').live('click', function(e) {
            e.preventDefault();
            var href = $(this).attr('href');
            slideTo(href, 'right');
            window.parent.history.pushState({structure_href: href}, null, window.parent.location.href);
        });

        window.parent.addEventListener('popstate', function(e) {
            if (e.state != null && e.state.structure_href !== undefined) {
                var href = e.state.structure_href;
                slideTo(href, (overlay_location.length > href.length ? 'right' : 'left'));
            }
        });

    });
}(jQuery));
