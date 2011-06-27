/*globals window, jQuery, $, document, console, common_content_filter*/

/* Code that runs inside the iframe menu
 */

CURRENT_OVERLAY_TRIGGER = null;
var menu_offset;
var menu_size = 'menu';

function expandMenu() {
    menu_offset = $(window.parent).scrollTop();
    $('body', window.parent.document).css('overflow', 'hidden');
    $(window.parent).scrollTop(menu_offset);
    $('#plone-cmsui-menu', window.parent.document).css('height', '100%');
    menu_size = 'full';
}
function contractMenu() {
    $('body', window.parent.document).css('overflow', 'auto');
    $(window.parent).scrollTop(menu_offset);
    $('#plone-cmsui-menu', window.parent.document).css('height', $('#toolbar').outerHeight());
    menu_size = 'menu';
}
function toggleMenu() {
    if (menu_size === 'menu') {
        expandMenu();
    } else {
        contractMenu();
    }
}

function showMessagesFromOverlay() {
    $('.overlay .portalMessage').each(function () {
        var type,
            portal_message = $(this),
            sticky = true;
        if (portal_message.hasClass('info')) {
            type = 'info';
            sticky = false;
        } else if (portal_message.hasClass('warning')) {
            type = 'warning';
        } else if (portal_message.hasClass('error')) {
            type = 'error';
        }
        window.parent.frames['plone-cmsui-notifications'].$.plone.notify({
            'title': portal_message.children('dt').html(),
            'message': portal_message.children('dd').html(),
            'type': type,
            'sticky': sticky
        });
    });
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
        $(document).trigger('onStartLoadOverlay', [this, href, data]);
        var $overlay = this.closest('.pb-ajax');
        this.load(href, data, function () {
            $overlay[0].handle_load_inside_overlay.apply(this, arguments);
            if (callback !== undefined) {
                callback.apply(this, arguments);
            }
            $(document).trigger('onEndLoadOverlay', [this, href, data]);
        });
        return this;
    };

    $().ready(function () {
        var iframe = $('#plone-cmsui-menu', window.parent.document);

        $('#toolbar').css({'opacity': 0});
        $(document).bind('onFormOverlayLoadSuccess', function () {
            showMessagesFromOverlay();
        });

        $('a.overlayLink').prepOverlay({
            subtype: 'ajax',
            filter: common_content_filter,
            // Add this to a link or button to make it close the overlay e.g.
            // on cancel without reloading the page
            closeselector: '.overlayCloseAction',
            formselector: 'form.overlayForm',
            config: {
                top: 130,
                onBeforeLoad: function (e) { 
                    // Close other overlays
                    expandMenu();
                    $(document).trigger('onBeforeOverlay', [this, e]);
                    return true; 
                },
                onLoad: function (e) {
                    loadUploader();
                    showMessagesFromOverlay();
                    $(document).trigger('onLoadOverlay', [this, e]);
                    return true; 
                }, 
                onClose: function (e) { 
                    CURRENT_OVERLAY_TRIGGER = null;
                    contractMenu();
                    $(document).trigger('onCloseOverlay', [this, e]);
                    return true; 
                }
            }
        });
        $(document).bind('onBeforeAjaxClickHandled', function(event, ele, api, clickevent){
            if(ele == CURRENT_OVERLAY_TRIGGER){
                return event.preventDefault();
            }else{
                if(CURRENT_OVERLAY_TRIGGER != null){
                    var overlays = $('div.overlay:visible');
                    overlays.fadeOut(function(){ $(this).remove(); });
                }
                CURRENT_OVERLAY_TRIGGER = ele;
            }
      });

        $("a.overlayLink").live('click', function(){
            $(document).trigger('onOverlayLinkClicked', [this]);
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
                    if ($(".overlay").length === 0) {
                        contractMenu();
                    }
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
            height, url, button;

        $('.portalMessage:visible').addClass('showNotify').hide();

        if (menu_state === 'small' || menu_state === 'large') {
            toolbar.addClass(menu_state);
            iframe.height(toolbar.outerHeight());
            parent_body.css('margin-top', toolbar.outerHeight());
            toolbar.animate({'opacity': 1}, 300, function () {
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
                        'z-index': 11000
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
            iframe.animate({'top': 0}, 1000);
            parent_body.animate({'margin-top': toolbar.outerHeight()}, 1000);
        }
        createCookie('__plone_height', $('#toolbar').outerHeight());

        $('#manage-page-open').click(function () {
            $(document).trigger('onManagePageOpening', [this]);
            var bottom_height = $('#toolbar-bottom').outerHeight();
            toolbar.addClass('large').removeClass('small');
            height = toolbar.outerHeight();
            $('#toolbar-bottom').css('top', -bottom_height);
            parent_body.stop().animate({'margin-top': height}, 500);
            $('#toolbar-bottom').stop().animate({'top': 0}, 500);
            iframe.stop().animate({'height': height}, 500);
            createCookie('__plone_menu', 'large');
            createCookie('__plone_height', height);
            $(document).trigger('onManagePageOpened', [this]);
            return false;
        });
        $('#manage-page-close').click(function () {
            $(document).trigger('onManagePageClosing', [this]);
            var bottom_height = $('#toolbar-bottom').outerHeight();
            height = toolbar.outerHeight() - bottom_height + 1;
            iframe.stop().animate({'height': height}, 500);
            parent_body.stop().animate({'margin-top': height}, 500, function () {
                toolbar.addClass('small').removeClass('large');
            });
            $('#toolbar-bottom').stop().animate({'top': -bottom_height}, 500);
            createCookie('__plone_menu', 'small');
            createCookie('__plone_height', height);
            $(document).trigger('onManagePageClosed', [this]);
            return false;
        });
    });

    // workaround this MSIE bug :
    // https://dev.plone.org/plone/ticket/10894
    if (jQuery.browser.msie) jQuery("#settings").remove();
    var Browser = {};
    // Browser.onUploadComplete = function() {
    //     window.location.reload();
    // }
    loadUploader = function() {
        var ulContainer = jQuery('.uploaderContainer');
        ulContainer.each(function(){
            var uploadUrl =  jQuery('.uploadUrl', this).val();
            var uploadData =  jQuery('.uploadData', this).val();
            var UlDiv = jQuery(this);
            jQuery.ajax({
                type: 'GET',
                url: uploadUrl,
                data: uploadData,
                dataType: 'html',
                contentType: 'text/html; charset=utf-8',
                success: function (html) {
                    UlDiv.html(html);
                }
            });
        });
    };
    jQuery(document).ready(loadUploader);


}(jQuery));

/**
 * Initialize tinymce
 */
$(document).bind('onLoadInsideOverlay', function() {
    $('textarea.mce_editable').each(function() {
        var config = new TinyMCEConfig($(this).attr('id'));
        config.init();
    });
});


/**
 *
 * JQuery Helpers for Plone Quick Upload
 *
 */

var PloneQuickUpload = {};

PloneQuickUpload.addUploadFields = function (uploader, domelement, file, id, fillTitles, fillDescriptions) {
    var blocFile, labelfiledescription, labelfiletitle;
    if (fillTitles || fillDescriptions) {
        blocFile = uploader._getItemByFileId(id);
        if (typeof id === 'string') {
            // If the string begins with any other value, the radix for
            // parseInt is 10 (decimal)
            id = parseInt(id.replace('qq-upload-handler-iframe', ''), 10);
        }
    }
    if (fillDescriptions)  {
        var labelfiledescription = jQuery('#uploadify_label_file_description').val();
        jQuery('.qq-upload-cancel', blocFile).after('\
                  <div class="uploadField">\
                      <label for="description_' + id + '">' + labelfiledescription + '</label> \
                      <textarea rows="2" \
                             class="file_description_field" \
                             id="description_' + id + '" \
                             name="description" \
                             value="" />\
                  </div>\
                   ')
    }
    if (fillTitles)  {
        var labelfiletitle = jQuery('#uploadify_label_file_title').val();
        jQuery('.qq-upload-cancel', blocFile).after('\
                  <div class="uploadField">\
                      <label for="title_' + id + '">' + labelfiletitle + '</label> \
                      <input type="text" \
                             class="file_title_field" \
                             id="title_' + id + '" \
                             name="title" \
                             value="' + file.fileName + '" />\
                  </div>\
                   ')
    }
    PloneQuickUpload.showButtons(uploader, domelement);
};

PloneQuickUpload.showButtons = function (uploader, domelement) {
    var handler = uploader._handler;
    if (handler._files.length) {
        jQuery('.uploadifybuttons', jQuery(domelement).parent()).show();
        return 'ok';
    }
    return false;
};

PloneQuickUpload.sendDataAndUpload = function (uploader, domelement, typeupload) {
    var handler = uploader._handler,
        files = handler._files,
        missing = 0,
        id, fileContainer;
    jQuery('.uploadifybuttons', jQuery(domelement).parent()).find('input').attr({disabled: 'disabled', opacity: 0.8});
    for (id = 0; id < files.length; id += 1) {
        if (files[id]) {
            fileContainer = jQuery('.qq-upload-list li', domelement)[id - missing],
                file_title = '',
                file_description = '';
            if (fillTitles) {
                file_title = jQuery('.file_title_field', fileContainer).val();
            }
            if (fillDescriptions) {
                file_description = jQuery('.file_description_field', fileContainer).val();
            }
            uploader._queueUpload(id, {'title': file_title, 'description': file_description, 'typeupload' : typeupload});
        }
        // if file is null for any reason jq block is no more here
        else {
            missing += 1;
        }
    }
    jQuery('.uploadifybuttons', jQuery(domelement).parent()).hide();
    jQuery('.uploadifybuttons', jQuery(domelement).parent()).find('input').removeAttr('disabled').attr('opacity', 1);
}
PloneQuickUpload.onAllUploadsComplete = function(){
    // Browser.onUploadComplete();
}
PloneQuickUpload.clearQueue = function(uploader, domelement) {
    var handler = uploader._handler;
    var files = handler._files;
    for ( var id = 0; id < files.length; id++ ) {
        if (files[id]) {
            handler.cancel(id);
        }
        jQuery('.qq-upload-list li', domelement).remove();
        handler._files = [];
        if (typeof handler._inputs !== 'undefined') {
            handler._inputs = {};
        }
    }
    jQuery('.uploadifybuttons', jQuery(domelement).parent()).hide();
};
PloneQuickUpload.onUploadComplete = function (uploader, domelement, id, fileName, responseJSON) {
    var uploadList = jQuery('.qq-upload-list', domelement);
    if (responseJSON.success) {
        window.setTimeout(function () {
            jQuery(uploader._getItemByFileId(id)).remove();
            // after the last upload, if no errors, reload the page
            var newlist = jQuery('li', uploadList);
            if (! newlist.length) {
                window.setTimeout(PloneQuickUpload.onAllUploadsComplete, 5);
            }
        }, 50);
    }

};
