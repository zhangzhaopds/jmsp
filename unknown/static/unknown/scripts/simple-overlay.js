/*
 * jQuery simple overlay plugin
 * Author: Bjoern Diekert <me@bdiekert.com>
 * License: The Unlicense / unlicense.org
 * */

(function ($) {
  "use strict";

  /* Plugin Start */
  $.fn.simpleOverlay = function (options, callback) {

    /* Default settings */
    var settings = $.extend({
      "namespace": "simple-overlay",
      "insertBy": "load",
      "attribute": "href",
      "speed": 400
    }, options);

    /* HTML markup */
    var markup = "<div id='" + settings.namespace + "' class='" + settings.namespace + "'><div class='" + settings.namespace + "__wrapper'></div> <div class='" + settings.namespace + "__close'></div></div>";

    /* Close overlay */
    var closeOverlay = function () {
      var $overlay = $("#" + settings.namespace);

      $overlay.fadeOut(settings.speed, removeOverlay);

      /* Remove body no scroll */
      var $body = $("body");
      $body.css("overflow", "auto");
      $body.width("auto");

      /* Callback */
      callback();
    };

    /* Remove overlay */
    var removeOverlay = function () {
      var $overlay = $("#" + settings.namespace);

      $overlay.remove();
    };

    /* Open overlay */
    var openOverlay = function () {

      /* Prevent overlay from opening up when an overlay is still open */
      if ($('#' + settings.namespace).length === 1) {
        return false;
      }

      /* Append markup, find overlay, hide overlay */
      $('body').append(markup);
      var $overlay = $("#" + settings.namespace);
      $overlay.hide();

      /* */
      var overlayAttr = $(this).attr(settings.attribute);

      /* Insert by load */
      if (settings.insertBy === "load") {
        $overlay.find("." + settings.namespace + "__wrapper").load(overlayAttr);
      }

      /* Insert by embed */
      if (settings.insertBy === "embed") {
        $overlay.find("." + settings.namespace + "__wrapper").html(overlayAttr);
      }

      /* Close function */
      $overlay.find("." + settings.namespace + "__close").click(closeOverlay);

      /* Add body no scroll */
      var $body = $("body");
      var oldWidth = $body.innerWidth();
      $body.css("overflow", "hidden");
      $body.width(oldWidth);

      /* Fadein Overlay */
      $overlay.fadeIn(settings.speed);

      return false;
    };

    /* Return function */
    return this.each(function () {

      /* Bind click */
      $(this).click(openOverlay);

    });
  };
}(jQuery));