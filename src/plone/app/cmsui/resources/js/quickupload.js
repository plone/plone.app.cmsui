/**
 *
 * JQuery Helpers for Plone Quick Upload
 *
 */

(function ($) {
    initQuickUpload = function(){
        $('.uploaderContainer').each(function(){
            var ulDiv = $(this);
            var uploadUrl = ulDiv.children('.uploadUrl').val();
            var uploadData = ulDiv.children('.uploadData').val();
            // If the uploaderContainer is already set up, leave it alone
            if(typeof uploadUrl === "undefined") return;
            jQuery.ajax({
                type: 'GET',
                url: uploadUrl,
                data: uploadData,
                dataType: 'html',
                contentType: 'text/html; charset=utf-8',
                success: function (html) {
                    ulDiv.html(html);
                }
            });
        });
    };
    $(document).ajaxComplete(initQuickUpload);
    $(document).ready(initQuickUpload);
}(jQuery));

var PloneQuickUpload = {};

PloneQuickUpload.addUploadFields = function (uploader, domelement, file, id, fillTitles, fillDescriptions) {
    var blocFile,
        labelfiledescription,
        labelfiletitle;

    if (fillTitles || fillDescriptions) {
        blocFile = uploader._getItemByFileId(id);
        if (typeof id === 'string') {
            // If the string begins with any other value, the radix for
            // parseInt is 10 (decimal)
            id = parseInt(id.replace('qq-upload-handler-iframe', ''), 10);
        }
    }
    if (fillDescriptions)  {
        labelfiledescription = jQuery('#uploadify_label_file_description').val();

        jQuery('.qq-upload-cancel', blocFile).after(
            '<div class="uploadField">' +
            '  <label for="description_' + id + '">' + labelfiledescription + '</label>' +
            '    <textarea rows="2"' +
            '        class="file_description_field"' +
            '        id="description_' + id + '"' +
            '        name="description"' +
            '        value="" />' +
            '</div>');
    }
    if (fillTitles)  {
        labelfiletitle = jQuery('#uploadify_label_file_title').val();

        jQuery('.qq-upload-cancel', blocFile).after(
            '<div class="uploadField">' +
            '  <label for="title_' + id + '">' + labelfiletitle + '</label>' +
            '  <input type="text"' +
            '         class="file_title_field"' +
            '         id="title_' + id + '"' +
            '         name="title"' +
            '         value="' + file.fileName + '" />' +
            '</div>');
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
        id,
        fileContainer,
        fillTitles,
        fillDescriptions,
        file_title,
        file_description;

    jQuery('.uploadifybuttons', jQuery(domelement).parent())
        .find('input')
        .attr({disabled: 'disabled', opacity: 0.8});

    for (id = 0; id < files.length; id += 1) {
        if (files[id]) {
            fileContainer = jQuery('.qq-upload-list li', domelement)[id - missing];
            file_title = '';
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
};

PloneQuickUpload.onAllUploadsComplete = function(uploader){
    overlay = $(uploader._element).closest("div.pb-ajax");
    if(overlay.length) {
        $("div.pb-ajax").loadOverlay(uploader._options.container_url);
    } else {
        // Not in an overlay, reload the page
        window.location.reload(true);
    }
    $.plone.notify({
        'title': 'Info',
        'message': uploader._filesUploaded + ' files have been uploaded.'
    });
};

PloneQuickUpload.clearQueue = function(uploader, domelement) {
    var handler = uploader._handler,
        files = handler._files,
        id;

    for (id = 0; id < files.length; id+=1) {
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
                PloneQuickUpload.onAllUploadsComplete(uploader);
            }
        }, 50);
    }

};
