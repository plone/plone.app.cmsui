from Acquisition import aq_inner

from datetime import datetime
from dateutil.relativedelta import relativedelta

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
        
        sel_from = request.form.get('sel_from',None)
        sel_to = request.form.get('sel_to',None)
        if sel_from and sel_to:
            self.sel_from = int(sel_from)
            self.sel_to = int(sel_to)
        elif sel_to:
            self.sel_from = 'previous'
            self.sel_to = int(sel_to)
        else:
            self.sel_from = 'previous'
            self.sel_to   = 'latest'
    
    def __call__(self):
        context = self.context
        #TODO: Is this how to do it?
        if not(_checkPermission(AccessPreviousVersions, self.context)):
            raise Unauthorized
        
        # Get editing history
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
        history_list = []
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
                comment=meta['comment'] or _("Edit"),
                klass='',
            )
            if self.sel_from == h['version_id']:
              h['klass'] = 'sel_from'
              self.sel_from_version = h
            if self.sel_to == h['version_id']:
              h['klass'] = 'sel_to'
              self.sel_to_version = h
            history_list.append(h)
        
        # Add workflow history to version history
        workflow = getToolByName(self.context, 'portal_workflow')
        for r in workflow.getInfoFor(self.context, 'review_history'):
            title = workflow.getTitleForTransitionOnType(r['action'], self.context.portal_type)
            if title is None: continue # No title means 'Create', and there'll be a edit_history entry for this.
            history_list.append(dict(entry_type='workflow',
                transition=title,
                principal=r.get('actor', _(u'label_anonymous_user', default=u'Anonymous User')),
                timestamp=datetime.fromtimestamp(float(r['time'])),
                comment=r['comments'] or _("Transition"),
                klass='',
            ))
        
        # Insert a date marker for every unique month
        date_markers = dict()
        for e in history_list:
            date_string = e['timestamp'].strftime('%B %Y')
            if date_markers.has_key(date_string): continue
            date_markers[date_string] = dict(
                entry_type='date-marker',
                # Timestamp one month ahead so it's on top of all the entries it refers to
                timestamp=datetime(e['timestamp'].year,e['timestamp'].month,1)+relativedelta(months=+1),
                date=e['timestamp'].strftime('%B %Y'),
            )
        history_list += date_markers.values()
        
        # Sort list into reverse order
        self.history_list = history_list = sorted(history_list, key=lambda k: datetime.now() - k['timestamp'])
        
        return super(HistoryPanel, self).__call__()
    
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
