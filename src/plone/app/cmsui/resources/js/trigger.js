/* Code to trigger loading the iframe menu when a page is loaded
 */
 
// TODO: We probably shouldn't rely on jQuery here, and this all needs
//       cleanup. See http://projects.plone.org/browse/NEWUI-86

(function ($) {

    $().ready(function() {
        
        var cmsui, overlay, menu;

        // The cmsui global object
        if (window.cmsui === undefined) {
            window.cmsui = {};
        }
        cmsui = window.cmsui;

        // Some basic node utilities
        function updateAttrs(elem, attrs) {
            var attr;
            for(attr in attrs) {
                if(attrs.hasOwnProperty(attr)) {
                    elem.setAttribute(attr, attrs[attr]);
                }
            }
        }

        function text(s) {
            return document.createTextNode(s);
        }

        function element(tag, attrs, children) {
            var i, length, elem = document.createElement(tag);
            updateAttrs(elem, attrs);
            for(i=0, length=children.length; i < length; i += 1) {
                elem.appendChild(children[i]);
            }
            return elem;
        }

        function div(attrs, children) {
            return element('div', attrs, children);
        }

        function span(attrs, children) {
            return element('span', attrs, children);
        }

        function iframe(attrs) {
            var elem = element('iframe', attrs, []);
            if (elem.allowTransparency !== undefined) {
                elem.allowTransparency = true;
            }
            return elem;
        }

        // Menu elements
        menu = cmsui.menu = {};
        menu.iframe = iframe({
            id: 'cmsui-menu',
            name: 'cmsui-menu',
            src: $("#cmsui-menu-link").attr("href"),
            scrolling: 'no'
        });
        menu.wrapper = div({'class': 'cmsui-reset', id: 'cmsui-menu-wrapper'}, [
            menu.iframe
        ]);
        
        menu.resize = function () {
            var size = cmsui.menu.window.document.getElementById('visual-portal-wrapper').scrollHeight;
            $(cmsui.menu.iframe).css("height", size + 10);
        };
        menu.iframe.onload = menu.resize;
        
        document.body.insertBefore(menu.wrapper, document.body.childNodes[0]);
        menu.window = menu.iframe.contentWindow;

        // Overlay elements
        overlay = cmsui.overlay = {};
        overlay.closeButton = div({'id': 'cmsui-overlay-close'}, [
            span({}, [
                text("Close")
            ])
        ]);
        overlay.iframe = iframe({
            id: 'cmsui-overlay',
            name: 'cmsui-overlay',
            src: 'about:blank'
        });
        overlay.wrapper = div({id: 'cmsui-overlay-wrapper'}, [
            overlay.closeButton,
            overlay.iframe,
        ]);
        overlay.mask = div({'class': 'cmsui-reset', id: 'cmsui-overlay-mask', style:'display: none;'}, [
            overlay.wrapper
        ]);
        document.body.insertBefore(overlay.mask, document.body.childNodes[0]);
        overlay.window = overlay.iframe.contentWindow;

        // Overlay close event
        overlay._close_listeners = [];
        overlay._notifyClosed = function() {
            var i, length, handler,
                listeners = overlay._close_listeners;
            for(i=0, length=listeners.length; i < length; i += 1) {
                handler = listeners[i][0];
                data = listeners[i][1];
                if (data === undefined) {
                    handler();
                } else {
                    handler(data);
                }
            }
        };

        overlay.close = function (data, handler) {
            if(data !== undefined) {
                if (handler === undefined) {
                    // handler is first argument
                    overlay._close_listeners.push([data, undefined]);
                } else {
                    overlay._close_listeners.push([handler, data]);
                }
            } else {
                overlay._close()
            }
        };

        overlay._close = function () {
            // Trigger the onbeforeunlaod event
            overlay.window.location.href = "about:blank";
            overlay.window.onunload = function () {
                overlay.mask.style.display = "none";
                overlay._notifyClosed();
            };
        };
        overlay.closeButton.onclick = overlay._close;

        // Overlay open
        overlay.open = function (url, success) {
            overlay.window.location.href = url;
            overlay.mask.style.display = "block";
            overlay.mask.style.height = document.body.clientHeight + 'px'; //XXX This would be better as position fixed.
            overlay.window.onunload = success; // hmmm. How to detect cancel from unload protection?
        };

        // overlay resize
        // overlay.resize = function () {
        //     var element = cmsui.overlay.window.document.getElementById('visual-portal-wrapper');
        //     if(element != null) {
        //         var height = element.scrollHeight;
        //         cmsui.overlay.iframe.height = height;
        //     }
        // };
        // overlay.iframe.onload = overlay.resize;

        // remove fallback link
        $("#cmsui-menu-link").remove();
        
    });

}(jQuery));
