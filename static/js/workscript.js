

$(document).ready(function()
{
	/*
		Confirmations when deleting
	*/
	$('.delete_link').each(function(k, elem)
	{
		$(elem).click(function (elem, event)
		{
			if ( ! confirm('Weet je zeker dat je dit wilt verwijderen?'))
			{
			    event.preventDefault();
			}
		}.bind(null, elem));
	});
	
	/*
		Date- and timepickers
	*/
	var datePickerOpts = {
		dateFormat:'yy-mm-dd'
	};
	$('.datepicker').datepicker(datePickerOpts);
	
	/* http://timjames.me/jquery-ui-datetimepicker-plugin */
	var dateTimePickerOpts = {
		dateFormat:'yy-mm-dd',
		timeFormat:'hh:mm'
	};
	$('.datetimepicker').datetimepicker(dateTimePickerOpts);
	
	/* http://fgelinas.com/code/timepicker/ */
	$('.timepicker').timepicker();
	var timePickerOpts = {
        showLeadingZero: false,
        onHourShow: tpStartOnHourShowCallback,
        onMinuteShow: tpStartOnMinuteShowCallback
    };
    $('#timepicker_start').timepicker(timePickerOpts);
    $('#timepicker_end').timepicker(timePickerOpts);
    
    /*
	    Links inside list elements
    */
    $('.menu_list li a').each(function(k, elem)
    {
    	$(elem).attr('data-href', $(elem).attr('href'))
	    $(elem).removeAttr('href');
	    console.log($(elem));
    });
    $('.menu_list li a').each(function(k, elem)
    {
    	$(elem).parent('li').click(function (elem, event)
    	{
    		var url = $(elem).attr('data-href');
    		if ($(elem).attr('target') == '_blank')
    		{
				window.open(url);
    		}
    		else
    		{
    			window.location.href = url;
    		}
    		
    	}.bind(null, elem));
    });
});



/* Begin and end time restrictions */
/* #TODO this isn't working... when it is, move it to timepicker.js */
function tpStartOnHourShowCallback(hour) {
    var tpEndHour = $('#timepicker_end').timepicker('getHour');
    // all valid if no end time selected
    if ($('#timepicker_end').val() == '') { return true; }
    // Check if proposed hour is prior or equal to selected end time hour
    if (hour <= tpEndHour) { return true; }
    // if hour did not match, it can not be selected
    return false;
}

function tpStartOnMinuteShowCallback(hour, minute) {
    var tpEndHour = $('#timepicker_end').timepicker('getHour');
    var tpEndMinute = $('#timepicker_end').timepicker('getMinute');
    // all valid if no end time selected
    if ($('#timepicker_end').val() == '') { return true; }
    // Check if proposed hour is prior to selected end time hour
    if (hour < tpEndHour) { return true; }
    // Check if proposed hour is equal to selected end time hour and minutes is prior
    if ( (hour == tpEndHour) && (minute < tpEndMinute) ) { return true; }
    // if minute did not match, it can not be selected
    return false;
}

function tpEndOnHourShowCallback(hour) {
    var tpStartHour = $('#timepicker_start').timepicker('getHour');
    // all valid if no start time selected
    if ($('#timepicker_start').val() == '') { return true; }
    // Check if proposed hour is after or equal to selected start time hour
    if (hour >= tpStartHour) { return true; }
    // if hour did not match, it can not be selected
    return false;
}

function tpEndOnMinuteShowCallback(hour, minute) {
    var tpStartHour = $('#timepicker_start').timepicker('getHour');
    var tpStartMinute = $('#timepicker_start').timepicker('getMinute');
    // all valid if no start time selected
    if ($('#timepicker_start').val() == '') { return true; }
    // Check if proposed hour is after selected start time hour
    if (hour > tpStartHour) { return true; }
    // Check if proposed hour is equal to selected start time hour and minutes is after
    if ( (hour == tpStartHour) && (minute > tpStartMinute) ) { return true; }
    // if minute did not match, it can not be selected
    return false;
}
