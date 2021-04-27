$(document).ready( function(){

	$('#sign-btn').on('click', function(e) {

		$(e.currentTarget).closest('ul').hide();

		$('form#sign').fadeIn('fast');
	});

});