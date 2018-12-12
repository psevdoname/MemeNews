$(function() {
	$('.hide').fadeOut();
	$(window).scroll(function() {
		vat scroll = $(window.scrollTop();
		if (scroll >=0) {
			$('.hide').fadeOut();
		}
		else {
			$('.hide').fadeIn();
		}
	});
})
			




