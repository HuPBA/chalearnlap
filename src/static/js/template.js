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

	$("#dialog").dialog({
	    modal: true,
	    autoOpen: false
	});
	$("a.delete-event").click(function(e) {
	    e.preventDefault();
	    var id = $(this).attr('id');
	    var addr = $(this).attr('value');
	    $("#dialog").dialog('option', 'buttons', {
	        "Delete": function() {
	            $.post({
	                url: addr,
	                data : {csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value},
	                success: function(data) {
				        if (data) {
				        	window.location.href = data;
				            // data.redirect contains the string URL to redirect to
				            // window.location.href = data;
				        }
				    }
	            });
	            $(this).dialog("close");
	        },
	        "Cancel": function() {
	            $(this).dialog("close");
	        }
	    });
	    $("#dialog").dialog("open");
	    return false;
	});

	$('#table-order').DataTable();
});