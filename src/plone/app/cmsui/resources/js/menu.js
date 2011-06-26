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
    $('#plone-cmsui-menu', window.parent.document).css('height', $('#toolbar').outerHeight());
}

// http://www.quirksmode.org/js/cookies.html
function createCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime()+(days*24*60*60*1000));
        expires = "; expires="+date.toGMTString();
    }
    document.cookie = name+"="+value+expires+"; path=/";
}

function readCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    var c;
    for (i=0; i<ca.length; i++) {
        c = ca[i];
        while (c.charAt(0)===' ') { c = c.substring(1, c.length); }
        if (c.indexOf(nameEQ) === 0) { return c.substring(nameEQ.length, c.length); }
    }
    return null;
}

function eraseCookie(name) {
    createCookie(name, "", -1);
}

(function ($) {
    // jquery method to load an overlay
    $.fn.loadOverlay = function(href, data, callback) {
        var $overlay = this.closest('.pb-ajax');
        this.load(href, data, function() {
	    $("#listing-table").ploneDnD(); // need to initialize again...
            if (callback != undefined) {
                callback.apply(this, arguments);
            }
            $overlay[0].handle_load_inside_overlay.apply(this, arguments);
        });
        return this;
    }
    
    $().ready(function () {
        var iframe = $('#plone-cmsui-menu', window.parent.document);
        var offset;

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
                    offset = expandMenu();
                    return true; 
                },
                onLoad: function (e) {
                    loadUploader();
                    $("#listing-table").ploneDnD();
                    return true; 
                }, 
                onClose: function (e) { 
                    contractMenu(offset);
                    return true; 
                }
            } 
        });
        
        $("a.overlayLink").live('click', function(){
            var url = $(this).attr("href");
            $(this).closest('.pb-ajax').loadOverlay(url + ' ' + common_content_filter);
            return false;
        });
    });
    $(window).load(function () {
        var menu_state = readCookie('__plone_menu'),
            iframe = $('#plone-cmsui-menu', window.parent.document),
            parent_body = $('body', window.parent.document),
            toolbar = $('#toolbar'),
            height;

        $('.portalMessage:visible').addClass('showNotify').hide();

        if (menu_state === 'small' || menu_state === 'large') {
            toolbar.addClass(menu_state);
            iframe.height(toolbar.outerHeight());
            parent_body.css('margin-top', toolbar.outerHeight());
            toolbar.animate({'opacity': 1}, 300, function () {
                iframe.css('background', 'transparent');

                // Check if an overlay should be opened
                var url = window.parent.document.location.href.match(/#!\/menu\/(.*)$/);
                if (url) {
                    var button = $('#' + url[1] + ' > a');
                    if (button.length !== 0) {
                        button.click();
                    }
                }

                // Append iframe to the document
                parent_body.append(
                    $(window.parent.document.createElement("iframe"))
                        .attr({
                            'src': '@@cmsui-notifications',
                            'id': 'plone-cmsui-notifications'
                        })
                        .css({
                            'top': toolbar.outerHeight(),
                            'right': 0,
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
            var bottom_height = $('#toolbar-bottom').outerHeight();
            toolbar.addClass('large').removeClass('small');
            height = toolbar.outerHeight();            
            $('#toolbar-bottom').css('top', -bottom_height);
            parent_body.stop().animate({'margin-top': height}, 500);
            $('#toolbar-bottom').stop().animate({'top': 0}, 500);
            iframe.stop().animate({'height': height}, 500);
            createCookie('__plone_menu', 'large');
            createCookie('__plone_height', height);
            return false;
        });
        $('#manage-page-close').click(function () {
            var bottom_height = $('#toolbar-bottom').outerHeight();
            height = toolbar.outerHeight() - bottom_height + 1;
            iframe.stop().animate({'height': height}, 500);
            parent_body.stop().animate({'margin-top': height}, 500, function () {
                toolbar.addClass('small').removeClass('large');
            });
            $('#toolbar-bottom').stop().animate({'top': -bottom_height}, 500);
            createCookie('__plone_menu', 'small');
            createCookie('__plone_height', height);
            return false;
        });
    });
    
    // workaround this MSIE bug :
    // https://dev.plone.org/plone/ticket/10894
    if (jQuery.browser.msie) jQuery("#settings").remove();
    var Browser = {};
    Browser.onUploadComplete = function() {
        window.location.reload();
    }
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
                       success: function(html) { 
                          UlDiv.html(html);             
                       } });    
        }); 
    }
    jQuery(document).ready(loadUploader);    
    
    
}(jQuery));


/**
 *
 * JQuery Helpers for Plone Quick Upload
 *   
 */    

var PloneQuickUpload = {};
    
PloneQuickUpload.addUploadFields = function(uploader, domelement, file, id, fillTitles, fillDescriptions) {
    var blocFile;
    if (fillTitles || fillDescriptions)  {
        blocFile = uploader._getItemByFileId(id);
        if (typeof id == 'string') id = parseInt(id.replace('qq-upload-handler-iframe',''));
    }
    if (fillDescriptions)  {
        var labelfiledescription = jQuery('#uploadify_label_file_description').val();
        jQuery('.qq-upload-cancel', blocFile).after('\
                  <div class="uploadField">\
                      <label>' + labelfiledescription + '&nbsp;:&nbsp;</label> \
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
                      <label>' + labelfiletitle + '&nbsp;:&nbsp;</label> \
                      <input type="text" \
                             class="file_title_field" \
                             id="title_' + id + '" \
                             name="title" \
                             value="" />\
                  </div>\
                   ')
    }
    PloneQuickUpload.showButtons(uploader, domelement);
}

PloneQuickUpload.showButtons = function(uploader, domelement) {
    var handler = uploader._handler;
    if (handler._files.length) {
        jQuery('.uploadifybuttons', jQuery(domelement).parent()).show();
        return 'ok';
    }
    return false;
}

PloneQuickUpload.sendDataAndUpload = function(uploader, domelement, typeupload) {
    var handler = uploader._handler;
    var files = handler._files;
    var missing = 0;
    for ( var id = 0; id < files.length; id++ ) {
        if (files[id]) {
            var fileContainer = jQuery('.qq-upload-list li', domelement)[id-missing];
            var file_title = '';
            if (fillTitles)  {
                file_title = jQuery('.file_title_field', fileContainer).val();
            }
            var file_description = '';
            if (fillDescriptions)  {
                file_description = jQuery('.file_description_field', fileContainer).val();
            }
            uploader._queueUpload(id, {'title': file_title, 'description': file_description, 'typeupload' : typeupload});
        }
        // if file is null for any reason jq block is no more here
        else missing++;
    }
}    
PloneQuickUpload.onAllUploadsComplete = function(){
    Browser.onUploadComplete();
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
        if (typeof handler._inputs != 'undefined') handler._inputs = {};
    }    
}    
PloneQuickUpload.onUploadComplete = function(uploader, domelement, id, fileName, responseJSON) {
    var uploadList = jQuery('.qq-upload-list', domelement);
    if (responseJSON.success) {        
        window.setTimeout( function() {
            jQuery(uploader._getItemByFileId(id)).remove();
            // after the last upload, if no errors, reload the page
            var newlist = jQuery('li', uploadList);
            if (! newlist.length) window.setTimeout( PloneQuickUpload.onAllUploadsComplete, 5);       
        }, 50);
    }
    
}
