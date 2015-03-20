# -*- coding:utf-8 -*-
'''
Created on Jan 2, 2013

@author: Oberron
'''

CRLF= "\r\n"

RFC5545_SCM = {
               "3_0": "SCM logs for loaded file",
               "3_1": "No iCalendar loaded",
               "3.1_1":"å¤3.1 mandates that content lines are delimited by a line break, which is a CRLF sequence",
               "3.1_2":"å¤3.1 mandates that all lines follow: 'contentline   = name *(\";\" param ) \":\" value CRLF'",
               "3.1_3":"å¤3.1 mandates line lengths to be less than 75 octets",
               "3.1_4":"å¤3.1 mandates line lengths to be less than 75 octets - current line too long and ignored",
               "3.1_5":"å¤3.1 mandates allowable characters",
               "3.3.4_1":"å¤3.3.4. Date is four-digit year, two-digit month, and two-digit day of the month.  There are no separator characters between the year, month, and day component text.",
               "3.1.1_1":"å¤3.1.1_1 COMMA ',' character as list Separators",
               "3.3.5_1":"å¤3.3.5 that DATE-TIME follows ISO8601-2004 which makes dates prior to 1875/may/20 bounded to prior agreement between sender and receiver",
               "3.3.5_2":"å¤3.3.5 that DATE-TIME is DATE (8 numbers as yyyymmdd), then 'T', then TIME (6 numbers HHMMSS), possibly followed by character 'Z'",
               "3.3.5_3":"å¤3.3.5 The \"TZID\" property parameter MUST NOT be applied to DATE-TIME properties whose time values are specified in UTC.",
               "3.3.6_1": "å¤3.3.6 that DURATION field doesn't support the \"Y\" and \"M\" designators from ISO8601",
               "3.3.8_1":"å¤3.3.8 The valid range for \"integer\" is -2147483648 to 2147483647.",
               "3.3.9_1":"å¤3.3.9 There are two forms of a period of time. First, a period of time is identified by its start and its end. Second, a period of time can also be defined by a start and a positiveduration of time.", 
               "3.3.10_1":"å¤3.3.10 Individual rule parts MUST only be specified once. ",
               "3.3.10_2":"å¤3.3.10 to ensure backward compatibility with applications that pre-date this revision of iCalendar the FREQ rule part MUST be the first rule part specified in a RECUR value.",
               "3.3.10_3":"å¤3.3.10 The FREQ rule part is REQUIRED",
               "3.3.10_4":"å¤3.3.10 The UNTIL or COUNT rule parts are OPTIONAL, but they MUST NOT occur in the same 'recur'.",
               "3.3.10_5":"å¤3.3.10 The FREQ values MUST be either SECONDLY / MINUTELY / HOURLY / DAILY / WEEKLY / MONTHLY / YEARLY",
               "3.3.10_6":"å¤3.3.10 The INTERVAL rule part contains a positive integer",
               "3.3.10_6b":"å¤3.3.10 The value of the UNTIL rule part MUST have the same value type as the \"DTSTART\" property (i.e. DATE or DATE-TIME) but also if DTSTART is floating or UTC or with TZID so should UNTIL be",
               "3.3.10_7":"å¤3.3.10 The BYSECOND Valid values are 0 to 60.",
               "3.3.10_8":"å¤3.3.10 The BYMINUTE Valid values are 0 to 59.",
               "3.3.10_9":"å¤3.3.10 The BYHOUR Valid values are 0 to 23.",
               "3.3.10_10":"å¤3.3.10 The BYSECOND, BYMINUTE and BYHOUR rule parts MUST NOT be specified when the associated \"DTSTART\" property has a DATE value type.",
               "3.3.10_11":"å¤3.3.10 Each BYDAY value can also be preceded by a positive (+n) or negative (-n) integer.  If present, this indicates the nth occurrence of a specific day within the MONTHLY or YEARLY \"RRULE\".",
               "3.3.10_12":"å¤3.3.10 The BYMONTHDAY rule part MUST NOT be specified when the FREQ rule part is set to WEEKLY.",
               "3.3.10_13":"å¤3.3.10 The BYYEARDAY rule part MUST NOT be specified when the FREQ rule part is set to DAILY, WEEKLY, or MONTHLY.",
               "3.3.10_14":"å¤3.3.10 The BYWEEKNO Valid values are 1 to 53 or -53 to -1.",
               "3.3.10_15":"å¤3.3.10 The BYWEEKNO rule part MUST NOT be used when the FREQ rule part is set to anything other than YEARLY.",
               "3.3.10_16":"å¤3.3.10 The BYMONTH Valid values are 1 to 12.",
               "3.3.10_17":"å¤3.3.10 The The WKST Valid values are MO, TU, WE, TH, FR, SA, and SU.",
               "3.3.10_17":"å¤3.3.10 The BYSETPOS rule part specifies a COMMA-separated list positive (+n) or negative (-n) integer.",
               "3.3.10_18":"å¤3.3.10 Recurrence rules may generate recurrence instances with an invalid date (e.g., February 30) or nonexistent local time (e.g., 1:30 AM on a day where the local time is moved forward by an hour at 1:00 AM).  Such recurrence instances MUST be ignored and MUST NOT be counted as part of the recurrence set.",
               "3.3.12_1":"å¤3.3.12 The form of time with UTC offset MUST NOT be used: 230000-0800        ;Invalid time format",
               
               "3.4_1":"å¤3.4 : The first line of the iCalendar object MUST contain the first of the pair of iCalendar object delimiter strings: BEGIN:VCALENDAR+CRLF",
               "3.4_2":"å¤3.4 : The last line of the iCalendar object MUST contain the last of the pair of iCalendar object delimiter strings: END:VCALENDAR+CRLF",
               
               "3.6_1":"å¤3.6 :PRODID property of iCalendar MUST be present",
               "3.6_2":"å¤3.6 :VERSION property of iCalendar MUST be present",
               "3.6_3":"å¤3.6 :at least on object of iCalendar MUST be present",
               "3.6.1_0":"å¤3.6.1 says DTSTART is optional, nonetheless a value should be computable",
               "3.6.1_1":"å¤3.6.1 specifies that \'The \"VEVENT\" calendar component cannot be nested within another calendar component.",
               "3.6.1_2":"å¤3.6.1 specifies DTSTAMP, UID, DTSTART, ... MUST NOT occur more than once",
               "3.6.1_3":"å¤3.6.1 UID is REQUIRED but cannot occur more than once",
               "3.6.1_4":"å¤3.6.1 Either 'dtend' or 'duration' MAY appear in a 'eventprop', but 'dtend' and 'duration' MUST NOT occur in the same 'eventprop'.",
               "3.6.1_5":"å¤3.6.1 if VEVENT has a DATE value type for the \"DTSTART\" and if such a \"VEVENT\" has a \"DTEND\" property, it MUST be specified as a DATE value also.",
               "3.8.2.2_1":"å¤3.8.2.2 on DTEND says 'its value MUST be later in time than the value of the \"DTSTART\" property.'",
               "3.8.2.4_1":"å¤3.8.2.4 mandates DTSTART when RRULE is set",
               '3.8.2.4_2':"å¤3.8.2.4 mandates DTSTART when METHOD is not set",
               "3.8.4.7_1": "å¤3.8.4.7 \"UID\" itself MUST be a globally unique identifier",
               "3.8.5.1_0": "å¤3.8.5.1 does not specify but implies that value type of EXDATE matches DTSTART value type",
               "3.8.5.2_0": "å¤3.8.5.2 does not specify but implies that value type of RDATE matches DTSTART value type",
               "3.8.5.3_1": "å¤3.8.5.3 RRULE SHOULD NOT be specified more than once. The recurrence set generated with multiple \"RRULE\" properties is undefined.", 
               "6_1":"Applications MUST generate iCalendar streams in the UTF-8 charset and MUST accept an iCalendar stream in the UTF-8 or US-ASCII charset.",
               "8.3.2_1": "å¤8.3.2 speficies valid properties"
               }

RFC5545_FREQ = {"SECONDLY" , "MINUTELY" , "HOURLY" , "DAILY",
                   "WEEKLY" , "MONTHLY" , "YEARLY"}

RFC5545_Components = {"VCALENDAR","VEVENT","VTODO","VJOURNAL","VFREEBUSY","VTIMEZONE",
                      "VALARM","STANDARD","DAYLIGHT"
                      }

RFC5545_eventprop_count = {
                  "1": ["DTSTAMP ", "UID" , "DTSTART" ],
                  "01": ["CLASS" , "CREATED" , "DESCRIPTION" , "GEO" ,
                  "LAST-MOD" , "LOCATION" , "ORGANIZER" , "PRIORITY" ,
                  "SEQ" , "STATUS" , "SUMMARY" , "TRASP" ,
                  "URL" , "RECURID" ,"DTEND" , "DURATION" ],
                  "0+" : ["RRULE", "ATTACH" , "ATTENDEE" , "CATEGORIES" , "COMMENT" ,
                  "CONTACT" , "EXDATE" , "RSTATUS" , "RELATED" ,
                  "RESSOURCES" , "RDATE" , "X-PROP" , "IANA-PROP"]
                  }

RFC5545_Properties = {'CALSCALE':"TEXT", #3.7.1.  Calendar Scale
                        'METHOD':"TEXT",
                        'PRODID':"TEXT",
                        'VERSION':"TEXT", #3.7.4.  Version
                        'ATTACH':"URI", #3.8.1.1.  Attachment
                        'CATEGORIES':"TEXT", #3.8.1.2.  Categories
                        'CLASS':"TEXT", #3.8.1.3.  Classification
                        'COMMENT':"TEXT", #3.8.1.4.  Comment
                        'DESCRIPTION':"TEXT", #3.8.1.5.  Description
                        'GEO':"FLOAT", #3.8.1.6.  Geographic Position
                        'LOCATION':"TEXT", #3.8.1.7.  Location
                        'PERCENT-COMPLETE':"INTEGER",
                        'PRIORITY':"INTEGER",
                        'RESOURCES':"TEXT",
                        'STATUS':"TEXT",
                        'SUMMARY':"TEXT",
                        'COMPLETED':"DATE-TIME",
                        'DTEND':"DATE-TIME",
                        'DUE':"DATE-TIME",
                        'DTSTART':"DATE-TIME",
                        'DURATION':"DURATION",
                        'FREEBUSY':"PERIOD",
                        'TRANSP':"TEXT",
                        'TZID':"TEXT",
                        'TZNAME':"TEXT",
                        'TZOFFSETFROM':"UTC-OFFSET",
                        'TZOFFSETTO':"TZOFFSETTO",
                        'TZURL':"URI",
                        'ATTENDEE':"CAL-ADDRESS", #FIXME: this seems not very clear #3.8.4.1.  Attendee
                        'CONTACT':"TEXT",
                        'ORGANIZER':"CAL-ADDRESS",
                        'RECURRENCE-ID':"DATE-TIME",
                        'RELATED-TO':"TEXT",
                        'URL':"URI",
                        'UID':"TEXT",
                        'EXDATE':"DATE-TIME-LIST",
                        'EXRULE':"RECUR",
                        'RDATE':"DATE-TIME-LIST",
                        'RRULE':"RECUR",
                        'ACTION':"TEXT",
                        'REPEAT':"INTEGER",
                        'TRIGGER':"DURATION",
                        'CREATED':"DATE-TIME",
                        'DTSTAMP':"DATE-TIME",
                        'LAST-MODIFIED':"DATE-TIME",
                        'SEQUENCE':"INTEGER",
                        'REQUEST-STATUS':"TEXT",
                        "BEGIN":"TEXT",
                        "END":"TEXT"
            }

ESCAPEDCHAR = {"\\\\" :"\\", "\\;":";",
                "\\,":"," , "\\N":"\n" , "\\n":"\n"}

weekday_map = {"MO":0,"TU":1,"WE":2,"TH":3,"FR":4,"SA":5,"SU":6}

MaxInteger = 2147483647