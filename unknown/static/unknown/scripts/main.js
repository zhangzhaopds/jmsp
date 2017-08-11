/*
Author: Dot Themes
*/
(function($) {
    "use strict";
	
    // SCREENSHOT MOBILE CAROUSEL
      $(".screenshots-carousel").owlCarousel({
          autoPlay: true, //Set AutoPlay to 3 seconds
          items : 5,
          itemsDesktop : [1199,3],
          itemsDesktopSmall : [979,3],
          itemsTablet : [768, 3],
          itemsMobile : [479,1]
      });
               
        // TESTIMONIAL CAROUSEL
      $(".testimonial-bottom").owlCarousel({
          navigation : false, // Show next and prev buttons
          slideSpeed : 300,
          paginationSpeed : 400,
          singleItem:true,
          autoPlay: true     
      });
        
        
        // Vimeo Video overlay
         $(".btn-vimeo").simpleOverlay({
            "insertBy": "embed",
            "attribute": "data-vimeo"
        });
        
        // Scroll Top
		$(window).on('scroll',function() {
		  if ($(this).scrollTop() > 100) {
				$('.scrollup').fadeIn();
			} else {
			  $('.scrollup').fadeOut();
			}
		});

		$('.scrollup').on('click', function(e) {
		  e.preventDefault();
			$('html, body').animate({scrollTop : 0}, 800);
		});
        
     // document function end

})(jQuery);