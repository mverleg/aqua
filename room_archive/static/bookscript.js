
$('body').live('pagecreate', function(event)
{
	$('#pick_time_start').change(function (event)
	{
		var time_parts = $('#pick_time_start').val().split(/[:;\., ]/);
		//alert(parseInt(time_parts[0]) + 1);
		$('#pick_time_start').val((parseInt(time_parts[0]) + 1) + ':' + time_parts[1]);
		$('#pick_time_end').val((parseInt(time_parts[0]) + 1) + ':' + time_parts[1]);
	});
});


$(document).keyup(function(event)
{
	if (event.which == 90 && event.ctrlKey)
	{
		window.location = "/zaalwacht/";
	}
});


/*
	reset type=date inputs to text
	http://jquerymobile.com/demos/1.0a4.1/experiments/ui-datepicker/
*/
$( document ).bind( "mobileinit", function()
{
	$.mobile.page.prototype.options.degradeInputs.date = true;
});
