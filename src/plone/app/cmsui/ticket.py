# This module was directly based on z3c.widget.flashupload.ticket.
# Unfortunately we needed more information, like the username that the ticket
# belongs to so that content can be created with the correct ownership.  And
# the username retrieval is quite Zope2-specific.

import random
from Acquisition import aq_inner
from zope.app.cache.ram import RAMCache
from zope.security.interfaces import Unauthorized
import AccessControl

ticketCache = RAMCache()

# from collective.quickupload import logger


def issueTicket(ident):
    """ issues a timelimit ticket
    >>> type(issueTicket(object()))== type('')
    True
    """
    ticket = str(random.random())
    sm = AccessControl.getSecurityManager()
    user = sm.getUser()
    if user is None:
        raise Unauthorized('No currently authenticated user')
    ticketCache.set(user.getId(), ident, key=dict(ticket=ticket))
    return ticket


def validateTicket(ident,ticket):
    """validates a ticket

    >>> validateTicket(object(),'abc')
    False
    >>> obj = object()
    >>> ticket = issueTicket(obj)
    >>> validateTicket(obj,ticket)
    True
    >>> validateTicket(object(),ticket)
    False
    >>> validateTicket(obj,'another')
    False
    """
    ticket =  ticketCache.query(ident,dict(ticket=ticket))
    return ticket is not None


def ticketOwner(ident, ticket):
    """Return username of the owner of the ticket.

    >>> ticketOwner(object(), 'abc') is None
    True
    >>> obj = object()
    >>> ticket = issueTicket(obj)
    >>> ticketOwner(obj,ticket)
    'Anonymous User'
    """

    return ticketCache.query(ident, dict(ticket=ticket))


def invalidateTicket(ident,ticket):

    """invalidates a ticket
    >>> ticket = issueTicket(1)
    >>> validateTicket(1,ticket)
    True
    >>> invalidateTicket(1,ticket)
    >>> validateTicket(1,ticket)
    False
    """
    ticketCache.invalidate(ident,dict(ticket=ticket))


class TicketView(object):

    """A view which returns a ticket for its context"""
    def __call__(self):
        # IE likes to cache this request, don't let it
        response = self.request.response
        response.setHeader('Cache-Control',
                           'no-cache, no-store, must-revalidate')
        response.setHeader('Pragma', 'no-ache')
        response.setHeader('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT')

        # logger.debug('Getting ready to issue new ticket')
        context = aq_inner(self.context)
        url = context.absolute_url()
        ticket = issueTicket(url)
        # logger.debug('Issued ticket "%s" for url: %s' % (str(ticket), url))

        return ticket
