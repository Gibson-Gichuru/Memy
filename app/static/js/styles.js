$(document).ready( function(){

	var $charCount, maxCharCount;

	$charCount = $('#post-modal .char-counter');
	maxCharCount = parseInt($charCount.data('max'), 10);

	$('#post-modal textarea').on('keyup', function(e) {

		var postLength = $(e.currentTarget).val().length;

		$charCount.html(maxCharCount - postLength);

	});
});

