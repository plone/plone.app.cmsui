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

function openLinksInOverlay() {
    $("a.overlayLink").live('click', function(){
        var url = $(this).attr("href");
        $(".pb-ajax").load(url + ' ' + common_content_filter);
        return false;
    });
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
    for (var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)===' ') { c = c.substring(1, c.length); }
        if (c.indexOf(nameEQ) === 0) { return c.substring(nameEQ.length, c.length); }
    }
    return null;
}

function eraseCookie(name) {
    createCookie(name, "", -1);
}

(function ($) {
    $().ready(function () {
        var iframe = $('#plone-cmsui-menu', window.parent.document);
        var offset;

        $('a.overlayLink').prepOverlay({
            subtype: 'ajax',
            filter: common_content_filter,
            // Add this to a link or button to make it close the overlay e.g.
            // on cancel without reloading the page
            closeselector: '.overlayCloseAction',
            config: { 
                top: 130,
                onBeforeLoad: function (e) { 
                    offset = expandMenu();
                    return true; 
                },
                onLoad: function (e) {
                    openLinksInOverlay();
                    loadUploader();
                    return true; 
                }, 
                onClose: function (e) { 
                    contractMenu(offset);
                    return true; 
                }
            }
        });

    });
    $(window).load(function () {
        var menu_state = readCookie('__plone_menu'),
            iframe = $('#plone-cmsui-menu', window.parent.document),
            parent_body = $('body', window.parent.document),
            toolbar = $('#toolbar'),
            height;
        if (menu_state === 'small' || menu_state === 'large') {
            toolbar.addClass(menu_state);
            iframe.height(toolbar.outerHeight());
            parent_body.css('margin-top', toolbar.outerHeight());
            iframe.animate({'opacity': 1}, 300);
        } else {
            createCookie('__plone_menu', 'small');
            toolbar.addClass('small');
            height = toolbar.outerHeight();            
            iframe.css({
                'opacity': 1,
                'top': -height,
                'height': height
                })
            iframe.animate({'top': 0}, 1000);
            parent_body.animate({'margin-top': toolbar.outerHeight()}, 1000);
        }
        createCookie('__plone_height', $('#toolbar').outerHeight());

        $.plone.initNotify();

        $('#manage-page-open').click(function () {
            var bottom_height = $('#toolbar-bottom').outerHeight();
            toolbar.addClass('large').removeClass('small');
            height = toolbar.outerHeight();            
            $('#toolbar-bottom').css('top', -bottom_height);
            parent_body.animate({'margin-top': height}, 500);
            $('#toolbar-bottom').animate({'top': 0}, 500);
            iframe.animate({'height': height}, 500);
            createCookie('__plone_menu', 'large');
            createCookie('__plone_height', height);
            return false;
        });
        $('#manage-page-close').click(function () {
            var bottom_height = $('#toolbar-bottom').outerHeight();
            height = toolbar.outerHeight() - bottom_height + 1;
            iframe.animate({'height': height}, 500);
            parent_body.animate({'margin-top': height}, 500, function () {
                toolbar.addClass('small').removeClass('large');
            });
            $('#toolbar-bottom').animate({'top': -bottom_height}, 500);
            createCookie('__plone_menu', 'small');
            createCookie('__plone_height', height);
            return false;
        });

        $('#folder-contents a').click(function () {
            $.plone.notify({
                'title': 'test',
                'message': 'some message'
            });
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
