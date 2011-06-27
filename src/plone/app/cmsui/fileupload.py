import mimetypes
import random
import urllib
from Acquisition import aq_inner
from AccessControl import SecurityManagement
from ZPublisher.HTTPRequest import HTTPRequest

from interfaces import IQuickUploadFileFactory
from zope.component import getUtility

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.app.container.interfaces import INameChooser
from plone.i18n.normalizer.interfaces import IIDNormalizer

# from collective.quickupload import siteMessageFactory as _
# from collective.quickupload import logger

import json

def decodeQueryString(QueryString):
  """decode *QueryString* into a dictionary, as ZPublisher would do"""
  r= HTTPRequest(None,
         {'QUERY_STRING' : QueryString,
          'SERVER_URL' : '',
          },
         None,1)
  r.processInputs()
  return r.form 

def getDataFromAllRequests(request, dataitem) :
    """
    Sometimes data is send using POST METHOD and QUERYSTRING
    """
    data = request.form.get(dataitem, None)
    if data is None:
        # try to get data from QueryString
        data = decodeQueryString(request.get('QUERY_STRING','')).get(dataitem)
    return data    


class QuickUploadView(BrowserView):
    """ The Quick Upload View
    """

    def __init__(self, context, request):
        super(QuickUploadView, self).__init__(context, request)
        self.uploader_id = self._uploader_id()

    def _uploader_id(self) :
        return 'uploader%s' %str(random.random()).replace('.','')
    
    def script_content(self) :
        context = aq_inner(self.context)
        return context.restrictedTraverse('@@quick_upload_init')(for_id = self.uploader_id)


XHR_UPLOAD_JS = """       
    var fillTitles = %(ul_fill_titles)s;
    var fillDescriptions = %(ul_fill_descriptions)s;
    var auto = %(ul_auto_upload)s;
    addUploadFields_%(ul_id)s = function(file, id) {
        var uploader = xhr_%(ul_id)s;
        PloneQuickUpload.addUploadFields(uploader, uploader._element, file, id, fillTitles, fillDescriptions);
    }
    sendDataAndUpload_%(ul_id)s = function() {
        var uploader = xhr_%(ul_id)s;
        PloneQuickUpload.sendDataAndUpload(uploader, uploader._element, '%(typeupload)s');
    }    
    clearQueue_%(ul_id)s = function() {
        var uploader = xhr_%(ul_id)s;
        PloneQuickUpload.clearQueue(uploader, uploader._element);    
    }    
    onUploadComplete_%(ul_id)s = function(id, fileName, responseJSON) {       
        var uploader = xhr_%(ul_id)s;
        PloneQuickUpload.onUploadComplete(uploader, uploader._element, id, fileName, responseJSON);
    }
    createUploader_%(ul_id)s= function(){    
        xhr_%(ul_id)s = new qq.FileUploader({
            element: jQuery('#%(ul_id)s')[0],
            action: '%(context_url)s/@@quick_upload_file',
            autoUpload: auto,
            onAfterSelect: addUploadFields_%(ul_id)s,
            onComplete: onUploadComplete_%(ul_id)s,
            allowedExtensions: %(ul_file_extensions_list)s,
            sizeLimit: %(ul_xhr_size_limit)s,
            simUploadLimit: %(ul_sim_upload_limit)s,
            template: '<div class="qq-uploader">' +
                      '<div class="qq-upload-drop-area"><span>%(ul_draganddrop_text)s</span></div>' +
                      '<div class="qq-upload-button"><label for="file-upload">%(ul_button_text)s</label></div>' +
                      '<ul class="qq-upload-list"></ul>' + 
                      '</div>',
            fileTemplate: '<li>' +
                    '<a class="qq-upload-cancel" href="#">&nbsp;</a>' +
                    '<div class="qq-upload-infos"><span class="qq-upload-file"></span>' +
                    '<span class="qq-upload-spinner"></span>' +
                    '<span class="qq-upload-failed-text">%(ul_msg_failed)s</span></div>' +
                    '<div class="qq-upload-size"></div>' +
                '</li>',                      
            messages: {
                serverError: "%(ul_error_server)s",
                serverErrorAlwaysExist: "%(ul_error_always_exists)s {file}",
                serverErrorZODBConflict: "%(ul_error_zodb_conflict)s {file}, %(ul_error_try_again)s",
                serverErrorNoPermission: "%(ul_error_no_permission)s",
                typeError: "%(ul_error_bad_ext)s {file}. %(ul_error_onlyallowed)s {extensions}.",
                sizeError: "%(ul_error_file_large)s {file}, %(ul_error_maxsize_is)s {sizeLimit}.",
                emptyError: "%(ul_error_empty_file)s {file}, %(ul_error_try_again_wo)s"            
            }            
        });           
    }
    jQuery(document).ready(createUploader_%(ul_id)s); 
"""


class QuickUploadInit(BrowserView):
    """ Initialize uploadify js
    """

    def _utranslate(self, msg):
        # XXX fixme : the _ (SiteMessageFactory) doesn't work
        context = aq_inner(self.context)
        return context.translate(msg, domain="collective.quickupload")

    def upload_settings(self):
        context = aq_inner(self.context)
        request = self.request
        session = request.get('SESSION', {})
        portal_url = getToolByName(context, 'portal_url')()    
        
        settings = dict(
            portal_url             = portal_url,
            typeupload             = '',
            context_url            = context.absolute_url(),
            physical_path          = "/".join(context.getPhysicalPath()),
            ul_id                  = self.uploader_id,
            ul_fill_titles         = 'true',
            ul_fill_descriptions   = 'false',
            ul_auto_upload         = 'false',
            ul_size_limit          = '1',
            ul_xhr_size_limit      = '0',
            ul_sim_upload_limit    = '1',
            ul_file_extensions     = '*.*',
            ul_file_extensions_list = '[]',
            ul_file_description    = self._utranslate(u'Choose files to upload'),
            ul_button_text         = self._utranslate(u'Choose one or more files to upload:'),
            ul_draganddrop_text    = self._utranslate(u'Drag and drop files to upload'),
            ul_msg_all_sucess      = self._utranslate(u'All files uploaded with success.'),
            ul_msg_some_sucess     = self._utranslate(u' files uploaded with success, '),
            ul_msg_some_errors     = self._utranslate(u" uploads return an error."),
            ul_msg_failed          = self._utranslate(u"Failed"),
            ul_error_try_again_wo  = self._utranslate(u"please select files again without it."),
            ul_error_try_again     = self._utranslate(u"please try again."),
            ul_error_empty_file    = self._utranslate(u"This file is empty :"),
            ul_error_file_large    = self._utranslate(u"This file is too large :"),
            ul_error_maxsize_is    = self._utranslate(u"maximum file size is :"),
            ul_error_bad_ext       = self._utranslate(u"This file has invalid extension :"),
            ul_error_onlyallowed   = self._utranslate(u"Only allowed :"),
            ul_error_no_permission = self._utranslate(u"You don't have permission to add this content in this place."),
            ul_error_always_exists = self._utranslate(u"This file already exists with the same name on server :"),
            ul_error_zodb_conflict = self._utranslate(u"A data base conflict error happened when uploading this file :"),
            ul_error_server        = self._utranslate(u"Server error, please contact support and/or try again."),
        )        
        
        return settings

    def __call__(self, for_id="uploader"):
        self.uploader_id = for_id
        settings = self.upload_settings()
        return XHR_UPLOAD_JS % settings   


class QuickUploadFile(BrowserView):
    """ Upload a file
    """  
    
    def __call__(self):
        """
        """        
        context = aq_inner(self.context)
        request = self.request
        response = request.RESPONSE      
        
        response.setHeader('Expires', 'Sat, 1 Jan 2000 00:00:00 GMT')
        response.setHeader('Cache-control', 'no-cache') 
        # the good content type woul be text/json or text/plain but IE 
        # do not support it
        response.setHeader('Content-Type', 'text/html; charset=utf-8')               

        if request.HTTP_X_REQUESTED_WITH :
            # using ajax upload
            file_name = urllib.unquote(request.HTTP_X_FILE_NAME)       
            upload_with = "XHR"
            try :
                file = request.BODYFILE
                file_data = file.read()
                file.seek(0)
            except AttributeError :
                # in case of cancel during xhr upload
                # logger.info("Upload of %s has been aborted" %file_name)
                # not really useful here since the upload block
                # is removed by "cancel" action, but
                # could be useful if someone change the js behavior
                return  json.dumps({u'error': u'emptyError'})
            except :
                # logger.info("Error when trying to read the file %s in request"  %file_name)
                return json.dumps({u'error': u'serverError'})
        else :
            # using classic form post method (MSIE<=8)
            file_data = request.get("qqfile", None)
            filename = getattr(file_data,'filename', '')
            file_name = filename.split("\\")[-1]  
            upload_with = "CLASSIC FORM POST"
            # we must test the file size in this case (no client test)

        # TODO Just change the id, instead of blocking the upload.
        if not self._check_file_id(file_name) :
            # logger.info("The file id for %s always exist, upload rejected" % file_name)
            return json.dumps({u'error': u'serverErrorAlwaysExist'})

        content_type = mimetypes.guess_type(file_name)[0]
        # sometimes plone mimetypes registry could be more powerful
        if not content_type :
            mtr = getToolByName(context, 'mimetypes_registry')
            oct = mtr.globFilename(file_name)
            if oct is not None :
                content_type = str(oct)
        
        portal_type = getDataFromAllRequests(request, 'typeupload') or ''
        title =  getDataFromAllRequests(request, 'title') or ''
        description =  getDataFromAllRequests(request, 'description') or ''
        
        if not portal_type :
            ctr = getToolByName(context, 'content_type_registry')
            portal_type = ctr.findTypeName(file_name.lower(), content_type, '') or 'File'
        
        if file_data:
            factory = IQuickUploadFileFactory(context)
            # logger.info("uploading file with %s : filename=%s, title=%s, description=%s, content_type=%s, portal_type=%s" % \
            # (upload_with, file_name, title, description, content_type, portal_type))                             
            
            try :
                f = factory(file_name, title, description, content_type, file_data, portal_type)
            except :
                return json.dumps({u'error': u'serverError'})
            
            if f['success'] is not None :
                o = f['success']
                # logger.info("file url: %s" % o.absolute_url()) 
                msg = {u'success': True}
            else :
                msg = {u'error': f['error']}
        else :
            msg = {u'error': u'emptyError'}
            
        return json.dumps(msg)          
    
    def _check_file_id(self, id):
        context = aq_inner(self.context)
        charset = context.getCharset()
        id = id.decode(charset)
        normalizer = getUtility(IIDNormalizer)
        chooser = INameChooser(context)
        newid = chooser.chooseName(normalizer.normalize(id), context)
        # consolidation because it's different upon Plone versions
        newid = newid.replace('_','-').replace(' ','-').lower()
        if newid in context.objectIds() :
            return 0
        return 1

class QuickUploadCheckFile(BrowserView):
    """
    check if file exists
    """
     
    def __call__(self):
        """
        """
        
        context = aq_inner(self.context)
        request = self.request
        
        always_exist = {}
        formdict = request.form
        ids = context.objectIds()
        
        for k,v in formdict.items():
            if k!='folder' :
                if v in ids :
                    always_exist[k] = v
        
        return str(always_exist)

