/*globals window, jQuery*/

/* Set up the Structure overlay */

jQuery(function ($) {

    // set an initial history state
    var overlay_location = $('#structure a').attr('href');
    window.parent.history.replaceState({structure_href: overlay_location}, null, window.parent.location.href);

    // animate navigation to a new folder
    var slideTo = function(href, dir) {
        var $slider = $('.structure-slider');
        var width = $slider.outerWidth();

	$(window).trigger('onStructureStartSlideTo', [this, $slider, href, dir]);

        $('#structure-dialog').css({height: $slider.outerHeight()});
        $('<div class="structure-slider" style="width: 100%"><' + '/div>')
            .prependTo($('#structure-dialog'))
            .loadOverlay(href + ' .structure-slider>*')
            .css({position: 'absolute', left: (dir=='left'?width:-width), top: 0})
            .animate({'left': 0}, 200, function() {$('.structure-slider').css('position', 'static'); $('#structure-dialog').css('height', 'auto');});
        $slider.css('position', 'relative').animate({'left': (dir=='left')?-width:width}, 200, null, function(){
            $slider.remove();
	    $(window).trigger('onStructureEndSlideTo', [this, $slider, href, dir]);
        });
        overlay_location = href;
    }

    $(window).bind('onStructureEndSlideTo', function(){ $("table.orderable").ploneDnD(); });
    $(window).bind('onEndLoadOverlay', function(){ $("table.orderable").ploneDnD(); });
    $(window).bind('onLoadOverlay', function(){ $("table.orderable").ploneDnD(); });

    // trigger navigation into child folders
    $('#structure-dialog a.link-child').live('click', function(e) {
        e.preventDefault();
        var href = $(this).attr('href');
        slideTo(href, 'left');
        window.parent.history.pushState({structure_href: href}, null, window.parent.location.href);
    });

    // trigger navigation from breadcrumbs
    $('#structure-dialog a.link-parent').live('click', function(e) {
        e.preventDefault();
        var href = $(this).attr('href');
        slideTo(href, 'right');
        window.parent.history.pushState({structure_href: href}, null, window.parent.location.href);
    });

    // update current folder after back/forward history navigation
    window.parent.addEventListener('popstate', function(e) {
        if (e.state != null && e.state.structure_href !== undefined) {
            var href = e.state.structure_href;
            slideTo(href, (overlay_location.length > href.length ? 'right' : 'left'));
        }
    });

});
