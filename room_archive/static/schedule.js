
/*
	This matches all reservations that are loaded. Currently it's not a problem is this code is executed more 
	than once per event (except	for performance), but if it becomes problematic find a better way.
*/

$('body').live('pagecreate', function(event)
{
	/* Create the schedule content */
	$('.schedule_event').each(function (k, element)
	{
		var reservation = $(element);
		var start = parseInt(reservation.attr('data-start'));
		var end = parseInt(reservation.attr('data-end'));
		var height = parseInt(Math.max(time2pix(end) - time2pix(start), 22));
		reservation.css('top', time2pix(start) + 'px');
		reservation.css('height', height + 'px');
	});
	
	/* Swipe events */
	$('.schedule').swipeleft(function(event)
	{
		$.mobile.changePage($(this).find('.schedule_hidden_next').html());
	});
	$('.schedule').swiperight(function(event)
	{
		$.mobile.changePage($(this).find('.schedule_hidden_previous').html());
	});
});

function time2pix(time)
{
	/* Offset 40 px with 40px/hr = 2/3 px/min */
	return parseInt((time - 8 * 60 + 40) * 2 / 3);
}

