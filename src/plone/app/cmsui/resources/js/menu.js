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
            iframe.animate({'opacity': 1}, 300, function () {
                $('.portalMessage:visible').each(function () {
                    var type,
                        portal_message = $(this);
                    if (portal_message.hasClass('info')) {
                        type = 'info';
                    } else if (portal_message.hasClass('warning')) {
                        type = 'warning';
                    } else if (portal_message.hasClass('error')) {
                        type = 'error';
                    }
                    $.plone.notify({
                        'title': portal_message.children('dt').html(),
                        'message': portal_message.children('dd').html(),
                        'type': type
                    });
                });
            });
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
}(jQuery));
