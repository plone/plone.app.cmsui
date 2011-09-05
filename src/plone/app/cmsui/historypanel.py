from Acquisition import aq_inner

from datetime import datetime

from plone.app.cmsui.interfaces import _

from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.Permissions import AccessPreviousVersions
from zope.publisher.browser import BrowserView

from zope.i18n import translate

from zExceptions import Unauthorized

class HistoryPanel(BrowserView):
    def __init__(self, context, request):
        super(HistoryPanel, self).__init__(context, request)
        
        # Work out if a version was selected, if 2 were selected always
        # comparing newest first
        sel_versions = request.form.get('diff',None)
        if isinstance(sel_versions,list) and sel_versions[0] > sel_versions[1]:
            self.sel_from = int(sel_versions[1])
            self.sel_to   = int(sel_versions[0])
        elif isinstance(sel_versions,list):
            self.sel_from = int(sel_versions[0])
            self.sel_to   = int(sel_versions[1])
        elif isinstance(sel_versions,str):
            self.sel_from = 'previous'
            self.sel_to   = int(sel_versions)
        else:
            self.sel_from = 'previous'
            self.sel_to   = 'latest'
    
    def __call__(self):
        context = self.context
        #TODO: Is this how to do it?
        if not(_checkPermission(AccessPreviousVersions, self.context)):
            raise Unauthorized
        
        # Get editing history
        self.version_history = []
        self.repo_tool=getToolByName(self.context, "portal_repository")
        if self.repo_tool is None or not self.repo_tool.isVersionable(context):
            # Item isn't versionable
            self.sel_to = self.sel_from = 0
            return super(HistoryPanel, self).__call__()
        edit_history=self.repo_tool.getHistoryMetadata(context);
        if not(hasattr(edit_history,'getLength')):
            # No history metadata
            self.sel_to = self.sel_from = 0
            return super(HistoryPanel, self).__call__()
        
        # Go through revision history backwards
        for i in xrange(edit_history.getLength(countPurged=False)-1, -1, -1):
            data = edit_history.retrieve(i, countPurged=False)
            meta = data["metadata"]["sys_metadata"]
            
            # Get next version, updating which is latest and previous if need be
            version_id = edit_history.getVersionId(i, countPurged=False)
            if self.sel_to == 'latest':
                self.sel_to = version_id
            elif self.sel_from == 'previous' and version_id < self.sel_to:
                self.sel_from = version_id
            
            # Add block describing this revision
            h = dict(entry_type='edit',
                version_id=version_id,
                principal=meta['principal'],
                timestamp=datetime.fromtimestamp(meta['timestamp']),
                comment=meta['comment'],
                klass='',
            )
            if self.sel_from == h['version_id']: h['klass'] = 'sel_from'
            if self.sel_to == h['version_id']:
              h['klass'] = 'sel_to'
              self.sel_to_version = h
            self.version_history.append(h)
        
        return super(HistoryPanel, self).__call__()
    
    def history_list(self):
        version_history = self.version_history
        
        # Add workflow history to version history
        workflow = getToolByName(self.context, 'portal_workflow')
        for r in workflow.getInfoFor(self.context, 'review_history'):
            version_history.append(dict(entry_type='workflow',
                transition=workflow.getTitleForTransitionOnType(r['action'], self.context.portal_type),
                principal=r.get('actor', _(u'label_anonymous_user', default=u'Anonymous User')),
                timestamp=datetime.fromtimestamp(float(r['time'])),
                comment=r['comments'],
                klass='',
            ))
        return sorted(version_history, key=lambda k: datetime.now() - k['timestamp'])

    def history_changes(self):
        if not(isinstance(self.sel_from,int) and isinstance(self.sel_to,int)):
            return []
        dt=getToolByName(self.context, "portal_diff")
        changeset=dt.createChangeSet(
                self._getVersion(self.sel_from),
                self._getVersion(self.sel_to),
                id1=self._versionTitle(self.sel_to), #TODO
                id2=self._versionTitle(getattr(self,'sel_from',None))
        )
        return [change for change in changeset.getDiffs()
                      if not change.same]

    def _versionTitle(self, version):
        return translate(
            _(u"version ${version}",
              mapping=dict(version=version)),
            context=self.request
        )

    def _getVersion(self, version):
        context=aq_inner(self.context)
        if version >= 0:
            return self.repo_tool.retrieve(context, int(version)).object
        else:
            return context
