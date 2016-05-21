jQuery(document).ready(function($) {
	$(".headroom").headroom({
		"tolerance": 20,
		"offset": 50,
		"classes": {
			"initial": "animated",
			"pinned": "slideDown",
			"unpinned": "slideUp"
		}
	});

	$(".js-example-basic-multiple").select2();

	$('#search-input').keypress(function (e) {
		if (e.which == 13) {
			$('form#search-form').submit();
			return false;
		}
	});
});
	