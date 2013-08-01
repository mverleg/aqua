
/*
	Based on schedule.js
*/

$(document).ready(function()
{
	var availability_mode = $('.schedule').is('.availability_schedule');
	
	/* Schedule content */
	$('.schedule_timeslot').each(function (k, element)
	{
		/* Positioning */
		var timeslot = $(element);
		var start = parseInt(timeslot.attr('data-start'));
		var end = parseInt(timeslot.attr('data-end'));
		var height = parseInt(Math.max(time2pix(end) - time2pix(start), 22));
		timeslot.css('top', time2pix(start) + 'px');
		timeslot.css('height', height + 'px');
		
		/* Toggling */
		if (availability_mode)
		{
			$(element).click(function(element, event)
			{
				if ($(element).hasClass('schedule_timeslot_unavailable'))
				{
					$(element).addClass('schedule_timeslot_available');
					$(element).removeClass('schedule_timeslot_unavailable');
				}
				else
				{
					$(element).addClass('schedule_timeslot_unavailable');
					$(element).removeClass('schedule_timeslot_available');
				}
				$('#shift_submit').addClass('schedule_submit_bold');
				$('#shift_copy').hide();
				
			}.bind(null, element));
		}
		else
		{
			$(element).click(function(element, event)
			{
				if ($(element).hasClass('final_shift_mine') || $(element).hasClass('final_shift_fortrade') || $(element).hasClass('final_shift_empty') || $(element).hasClass('final_shift_admin')) 
				{
					window.location.href = $(element).attr('data-link');
				}
				
			}.bind(null, element));
		}
	});
	
	/* Warnings */
	$('#pagination').find('a').click(function (event){
		if ($('#shift_submit').hasClass('schedule_submit_bold'))
		{
			if ( ! confirm('Je beschikbaarheid voor deze week is nog niet opgeslagen en zal verloren gaan. Wil je toch doorgaan?'))
			{
			    event.preventDefault();
			}
		}
	});
	$('#shift_copy').click(function (event){
		if ( ! confirm('Weet je zeker dat je deze shifts wilt kopieren naar andere weken, zover ze overeenkomen? Alle andere weken worden overschreven!'))
		{
		    event.preventDefault();
		}
	});
	
	/* Submission */
	$('#shift_submit').find('a').click(function(event){
		var available_shifts = '';
		$('.schedule_timeslot_available').each(function(k, element)
		{
			available_shifts = available_shifts + $(element).attr('data-pk') + ';';
		});
		$('#shift_input').val(available_shifts.slice(0, -1));
		$('#shift_form').submit();
		event.preventDefault();
	});
});

function time2pix(time)
{
	/* Offset 40 px with 40px/hr = 2/3 px/min */
	return parseInt((time - 8 * 60 + 40) * 2 / 3);
}

