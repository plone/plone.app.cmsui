/*
    Code that runs inside the iframe menu

    XXX: Way too many globals created; needs a namespace
    Globals exported:
        CURRENT_OVERLAY_TRIGGER
        PloneQuickUpload
        TinyMCEConfig
        contractMenu
        createCookie
        eraseCookie
        expandMenu
        forceContractMenu
        menu_offset
        menu_size,
        readCookie
        toggleMenu

*/

 /*jslint white:false, onevar:true, undef:true, nomen:false, eqeqeq:true,
   plusplus:true, bitwise:true, regexp:false, newcap:true, immed:true,
   strict:false, browser:true */
/*global jQuery:false, $:false, document:false, window:false, location:false,
  common_content_filter:false, TinyMCEConfig:false */


var CURRENT_OVERLAY_TRIGGER = null;
var menu_offset;
var menu_size = 'menu';

function expandMenu() {
    menu_offset = $(window.parent).scrollTop();
    $('body', window.parent.document).css('overflow', 'hidden');
    $(window.parent).scrollTop(menu_offset);
    $('#plone-cmsui-menu', window.parent.document).css('height', '100%');
    menu_size = 'full';
}
function forceContractMenu() {
    $('body', window.parent.document).css('overflow', 'auto');
    $(window.parent).scrollTop(menu_offset);
    $('#plone-cmsui-menu', window.parent.document).css('height', $('#toolbar').outerHeight());
    menu_size = 'menu';
}
function contractMenu() {
    if ($('.overlay').length === 0 && $('.dropdownItems:visible').length === 0) {
        forceContractMenu();
    }
}
function toggleMenu() {
    if (menu_size === 'menu') {
        expandMenu();
    } else {
        contractMenu();
    }
}

// http://www.quirksmode.org/js/cookies.html
function createCookie(name, value, days) {
    var expires = '', date;
    if (days) {
        date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = '; expires=' + date.toGMTString();
    }
    document.cookie = name + '=' + value + expires + '; path=/';
}

function readCookie(name) {
    var nameEQ = name + '=',
        ca = document.cookie.split(';'),
        c, i;
    for (i = 0; i < ca.length; i += 1) {
        c = ca[i];
        while (c.charAt(0) === ' ') {
            c = c.substring(1, c.length);
        }
        if (c.indexOf(nameEQ) === 0) {
            return c.substring(nameEQ.length, c.length);
        }
    }
    return null;
}

function eraseCookie(name) {
    createCookie(name, '', -1);
}

(function ($) {
    var Browser = {},
        loadUploader;

    // jquery method to load an overlay
    $.fn.loadOverlay = function(href, data, callback) {
        $(document).trigger('startLoadOverlay', [this, href, data]);
        var self = $(this),
            $overlay = this.closest('.pb-ajax');

        if(self.length === 0){
            $overlay = $('div.overlay-ajax:visible div.pb-ajax');
            self = $overlay;
        }
        self.load(href, data, function () {
            $overlay[0].handle_load_inside_overlay.apply(this, arguments);
            if (callback !== undefined) {
                callback.apply(this, arguments);
            }
            $(document).trigger('endLoadOverlay', [this, href, data]);
        });
        return this;
    };

    $().ready(function () {
        // var iframe = $('#plone-cmsui-menu', window.parent.document);

        $('#toolbar').css({'opacity': 0});
        $(document).bind('formOverlayLoadSuccess', function () {
            $.plone.showNotifyFromElements($(".overlay"));
        });

        $('a.overlayLink,.configlets a').prepOverlay({
            subtype: 'ajax',
            filter: common_content_filter,
            // Add this to a link or button to make it close the overlay e.g.
            // on cancel without reloading the page
            closeselector: '.overlayCloseAction',
            formselector: 'form.overlayForm,form.edit-form,#document-base-edit',
            noform: 'reload', // XXX : this will probably need to get smarter
            config: {
                closeOnClick: false,
                top: 130,
                mask: {
                    color: '#000000',
                    opacity: 0.5
                },
                onBeforeLoad: function (e) {
                    $('.dropdownItems').slideUp();
                    this.getOverlay().addClass($(CURRENT_OVERLAY_TRIGGER).closest('li').attr('id') + '-overlay');
                    $(document).trigger('beforeOverlay', [this, e]);
                    if (this.getOverlay().find('#form-widgets-ILayoutAware-content').length > 0) {
                        $.deco.init();
                        return false;
                    } else {
                        expandMenu();
                        return true;
                    }
                },
                onLoad: function (e) {
                    loadUploader();
                    $.plone.showNotifyFromElements($(".overlay"));
                    $(document).trigger('loadOverlay', [this, e]);
                    return true;
                },
                onClose: function (e) {
                    CURRENT_OVERLAY_TRIGGER = null;
                    $(document).trigger('closeOverlay', [this, e]);
                    forceContractMenu();
                    return true;
                }
            }
        });
        $(document).bind('beforeAjaxClickHandled', function(event, ele, api, clickevent){
            if(ele === CURRENT_OVERLAY_TRIGGER){
                return event.preventDefault();
            }else{
                if(CURRENT_OVERLAY_TRIGGER !== null){
                    var overlays = $('div.overlay:visible');
                    overlays.fadeOut(function(){ $(this).remove(); });
                }
                CURRENT_OVERLAY_TRIGGER = ele;

            }
        });

        $("a.overlayLink,.configlets a").live('click', function(){
            $(document).trigger('overlayLinkClicked', [this]);
            var url = $(this).attr("href");
            $(this).closest('#overlay-content').loadOverlay(url + ' ' + common_content_filter);
            return false;
        });
        $('.dropdownLink').bind('click', function (e) {
            if (menu_size === 'menu') {
                // iframe is collapsed
                expandMenu();
                $(this).nextAll('.dropdownItems').slideToggle();
            }
            else {
                $(this).nextAll('.dropdownItems').slideToggle(function () {
                    contractMenu();
                });
            }
            e.preventDefault();
        });
    });

    $(window).load(function () {
        var menu_state = readCookie('__plone_menu'),
            iframe = $('#plone-cmsui-menu', window.parent.document),
            parent_body = $('body', window.parent.document),
            toolbar = $('#toolbar'),
            height,
            url,
            button;

        $('.portalMessage:visible').addClass('showNotify').hide();

        if (menu_state === 'small' || menu_state === 'large') {
            toolbar.addClass(menu_state);
            iframe.height(toolbar.outerHeight());
            parent_body.css('margin-top', toolbar.outerHeight());
            toolbar.animate({'opacity': 1}, 250, function () {
                iframe.css('background', 'transparent');

                // Check if an overlay should be opened
                url = window.parent.document.location.href.match(/#!\/menu\/(.*)$/);
                if (url) {
                    button = $('#' + url[1] + ' > a');
                    if (button.length !== 0) {
                        button.click();
                    }
                }

                // Append iframe to the document
                parent_body.append(
                    $(window.parent.document.createElement('iframe'))
                    .attr({
                        'src': '@@cmsui-notifications',
                        'id': 'plone-cmsui-notifications',
                        'name': 'plone-cmsui-notifications'
                    })
                    .css({
                        'top': toolbar.outerHeight(),
                        'margin': 0,
                        'padding': 0,
                        'border': 0,
                        'outline': 0,
                        'background': 'transparent',
                        'position': 'fixed',
                        '_position': 'absolute',
                        '_top': 'expression(eval((document.body.scrollTop)?document.body.scrollTop:document.documentElement.scrollTop))',
                        'width': '320px',
                        'height': '0px',
                        'z-index': 100000
                    })
                );
            });
        } else {
            createCookie('__plone_menu', 'small');
            toolbar
                .addClass('small')
                .css('opacity', 1);
            height = toolbar.outerHeight();
            iframe.css({
                'top': -height,
                'height': height
            });
            iframe.animate({'top': 0}, 500);
            parent_body.animate({'margin-top': toolbar.outerHeight()}, 500);
        }
        createCookie('__plone_height', $('#toolbar').outerHeight());

        $('#manage-page-open').click(function () {
            $(document).trigger('managePageOpening', [this]);
            var bottom_height = $('#toolbar-bottom').outerHeight();
            toolbar.addClass('large').removeClass('small');
            height = toolbar.outerHeight();
            $('#toolbar-bottom').css('top', -bottom_height);
            parent_body.stop().animate({'margin-top': height}, 250);
            $('#toolbar-bottom').stop().animate({'top': 0}, 250);
            iframe.stop().animate({'height': height}, 250);
            createCookie('__plone_menu', 'large');
            createCookie('__plone_height', height);
            $(document).trigger('managePageOpened', [this]);
            return false;
        });
        $('#manage-page-close').click(function () {
            $(document).trigger('managePageClosing', [this]);
            var bottom_height = $('#toolbar-bottom').outerHeight();
            height = toolbar.outerHeight() - bottom_height + 1;
            iframe.stop().animate({'height': height}, 250);
            parent_body.stop().animate({'margin-top': height}, 250, function () {
                toolbar.addClass('small').removeClass('large');
            });
            $('#toolbar-bottom').stop().animate({'top': -bottom_height}, 250);
            createCookie('__plone_menu', 'small');
            createCookie('__plone_height', height);
            $(document).trigger('managePageClosed', [this]);
            return false;
        });
    });

    // workaround this MSIE bug :
    // https://dev.plone.org/plone/ticket/10894
    if (jQuery.browser.msie) {jQuery("#settings").remove();}
    Browser = {};
    // Browser.onUploadComplete = function() {
    //     window.location.reload();
    // }

}(jQuery));

/**
 * Initialize tinymce
 */
$(document).bind('loadInsideOverlay', function() {
    $('textarea.mce_editable').each(function() {
        var config = new TinyMCEConfig($(this).attr('id'));
        config.init();
    });
});
