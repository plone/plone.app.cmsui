/**
 * This plugin is used to display notifications
 *
 * @author Rob Gietema
 * @version 0.1
 * @licstart  The following is the entire license notice for the JavaScript
 *            code in this page.
 *
 * Copyright (C) 2011 Plone Foundation
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the Free
 * Software Foundation; either version 2 of the License.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along with
 * this program; if not, write to the Free Software Foundation, Inc., 51
 * Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 * @licend  The above is the entire license notice for the JavaScript code in
 *          this page.
 */
"use strict";

/*global jQuery: false, window: false */
/*jslint white: true, browser: true, onevar: true, undef: true, nomen: true,
eqeqeq: true, plusplus: true, bitwise: true, regexp: true, newcap: true,
immed: true, strict: true, maxlen: 80, maxerr: 9999 */

(function ($) {

    // Define plone namespace if it doesn't exist
    if (typeof($.plone) === "undefined") {
        $.plone = {};
    }

    /**
     * Initialize the notify module
     *
     * @id jQuery.plone.initNotify
     */
    $.plone.initNotify = function () {

        // Check if not already initialized
        if ($(".notification").length === 0) {

            // Append notification container to body element
            $("body").append(
                $(document.createElement("div"))
                    .addClass("notifications")
            );
        }
    };

    /**
     * Set the height of the iframe
     *
     * @id setIFrameHeight
     */
    function setIFrameHeight() {
        var last_notification = $(".notifications").children("div:last");
            
        // Set iframe height
        $('#plone-cmsui-notifications', window.parent.document)
            .css('height', last_notification.length > 0 ?
                           parseInt(last_notification.css("top"), 10) +
                           last_notification.height() + 10 : 0)
    }

    /**
     * Display a notification
     *
     * @id jQuery.plone.notify
     * @param {Object} options Object containing all the options of the action
     */
    $.plone.notify = function (options) {

        // Extend default settings
        options = $.extend({
            type: "info",
            title: "",
            message: "",
            fadeSpeed: "slow",
            duration: 3000
        }, options);

        // Check if title or message is empty
        if (options.title === "" || options.message === "") {
            return;
        }

        // Check if overlay is active
        if ($('.overlay', window.parent.frames['plone-cmsui-menu'].document).length !== 0) {
            $('#plone-cmsui-notifications', window.parent.document)
                .css('left', $(window.parent.frames['plone-cmsui-menu']).width() - 320);
        } else {
            $('#plone-cmsui-notifications', window.parent.document)
                .css('left', $(window.parent).width() - 320);
        }

        // Local variables
        var last_notification, offset_top, elm;

        // Get last notification
        last_notification = $(".notifications").children("div:last");

        // Calculate new offset top
        offset_top = last_notification.length > 0 ?
            parseInt(last_notification.css("top"), 10) +
            last_notification.height() + 10 : 0;

        // Add notification
        $(".notifications")

            // Add notification div
            .append($(document.createElement("div"))
                .addClass("notification")

                // Add notification header
                .append($(document.createElement("div"))
                    .addClass("notification-header")
                )

                // Add notification content
                .append($(document.createElement("div"))
                    .addClass("notification-content")

                    // Add type icon
                    .append($(document.createElement("div"))
                        .addClass("notification-type " +
                            "notification-type-" + options.type)
                    )

                    // Add close icon
                    .append($(document.createElement("div"))
                        .addClass("notification-close")

                        // On click fadeout and remove notification
                        .click(function () {
                            $(this).parents(".notification")
                                .data('close', true)
                                .fadeOut(options.fadeSpeed, function () {
                                    $(this).remove();
                                });
                        })
                    )

                    // Add notification text
                    .append($(document.createElement("div"))
                        .addClass("notification-text")
                        .append($(document.createElement("div"))
                            .addClass("notification-title")
                            .html(options.title)
                        )
                        .append($(document.createElement("div"))
                            .addClass("notification-message")
                            .html(options.message)
                        )
                    )
                )

                // Add notification footer
                .append($(document.createElement("div"))
                    .addClass("notification-footer")
                )

                // Hide notification so it can be fadein
                .hide()

                // Position notification
                .css("top", offset_top)

                // Fadein the notification
                .fadeIn(options.fadeSpeed, function () {
                    elm = $(this);

                    // Set timeout to hide notification
                    window.setTimeout(function () {

                        // If not mouseover fadeout and remove the message
                        if (elm.data("mouseover") === false) {
                            elm.fadeOut(options.fadeSpeed, function () {
                                elm.remove();
                            });
                        }
                        elm.data("timeout", true);
                    }, options.duration);

                    // Set initial state
                    elm.data("timeout", false);
                    elm.data('mouseover', false);
                    elm.data('close', false);
                })

                // Bind mouseover event
                .mouseover(function () {

                    // If not close pressed
                    if ($(this).data("close") === false) {

                        // Clear fadeout timeout and fade to full opacity
                        window.clearTimeout($(this).data('fade'));
                        $(this).stop();
                        $(this).fadeTo(options.fadeSpeed, 1);
                        $(this).data('mouseover', true);
                    }
                })

                // Bind mouseleave event
                .bind("mouseleave", function () {

                    // Get element
                    elm = $(this);

                    // If timeout has passed and close not pressed
                    if ((elm.data("timeout") === true) &&
                        (elm.data("close") === false)) {

                        // Fadeout and remove the notification
                        elm.fadeOut(options.fadeSpeed, function () {
                            elm.remove();
                        });
                    }

                    // Set mouseover state
                    $(this).data('mouseover', false);
                })
            );

        // Set iframe height
        setIFrameHeight();
    };

    // Init Deco on load
    $(window).load(function () {

        // Init notification
        $.plone.initNotify();

        // Show first notifications
        $('.showNotify', window.parent.frames['plone-cmsui-menu'].document).each(function () {
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

}(jQuery));
