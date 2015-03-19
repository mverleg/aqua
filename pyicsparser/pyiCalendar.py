# -*- coding:utf-8 -*-
"""iCalendar (RFC5545, RFC2445) parser/ validator/ generator/ events enumerator :  Parse, Generate and enumerate events (support of RRULE, EXRULE, RDATE, EXDATE)

About
-----

This module is an iCalendar parser for iCalendar file (ical or ics) defined by rfc5545 
(http://tools.ietf.org/html/rfc5545), which obsoleted rfc2445 
(http://www.ietf.org/rfc/rfc2445.txt), which had previously replaced vcal 1.0
(http://www.imc.org/pdi/vcal-10.txt).

The iCalendar file, once parsed, will be available as a typed structure. 
Events dates can be computed (including rrule, rdate exrule and exdates). 

iCalendar module and dateutils both provide some of the functionalities of this module but
do not provide it in an integrated way.

Usage
-----
* Enumerator of iCalendar file::

    mycal = icalendar.ics()\n
    mycal.local_load(icsfile)\n
    dates = mycal.get_event_instances(start,end)\n
    #dates will contain the json with all explicit dates of the events spec'ed by the iCalendar file\n

* Validator::

    mycal = icalendar.ics()\n
    perfect = mycal.isCalendarFileCompliant(icsfile) \n
    #When the file does not show any deviance from RFC5545, perfect will hold True \n
    #Console will display all non-conformance per lines\n

To come
-------
* 0.6.3: add load DATE and DATE-TIME 
    + document the code
    + add unittest support for parser, validator (RFC5545_xxx: those from RFC5545, SCM5545_xxx = additional test vectors)
    + add validator for generator + add call for validator from vevent 
    + make calls to validator less intrusive 
    + add checks on DATE-TIME from the timewindow vs event values
    + make flatten_rrule only take rrule and dtstart
    + make code for days lasting longer than 1 day
    + add code for get_instances or get_slots
    + add code for instances to have date-time if ics is in datetime
    + reset parameters when reloading
    + unit code on wild calendars : test the line for the errors
    +add code for event_instances (including support for overlapping), 
    get_instances(perday,permonth,peryear) event.instances.isbounded, event.instances.walk,
    +add code for valarm (note about: valarm description not to be counted as event description: cf SO_14892422.ics)
    +add code for multiple rrule, exrule, add code for event_instances['day']
    +add code for property parameters, property values, delimiters (linear, wlsp), ENCODING, character sets, language, binary values,XAPIA’s CSA RRULE,
    +x-components and x-properties parsing + for x-properties adding the type of data
* 0.6.4: add code for x-components and x-properties generation
* 0.6.5: add loader and generator for vtimezone,todo, alarm
* 0.7.x: add datetime and tzinfo + add email parser / generator capability (read MIME from email, send invite to GCal, Outlook, IPhone, BB)
* 0.8.x: add support for non-standard compliance: no tzoneinfo, escaped characters, ...
* 0.9.x: Extend support to new x-properties for iCalendar like events related to religious dates or celestial events

Next:
-----
* add CUA capability + CalDAV support

History
-------
* 0.6.1y - Jan 2013: added support for no dtstart and/or not dtend (compute one from another and raise exception if neither present) + add support for RDATE after UNTIL (and RDATE before DTSTART (to be ignored)
Created on Aug 4, 2011
* 0.6.1y1 - Feb 2013: added support for date-time, date-time-floating, date-time-TZID (though instances still only reports date) and no VTIMEZONE handling
* 0.6.1y3 - ValidateiCalendar will report and return True if iCalendar file is 100% compliant
*0.6.1y4 - fixed the validator not catching the max component count (see RFC5545_eventprop_count) 
            fixed the parser making difference between properties based on casing (lower / upper / mix)
@author: oberron
@change: to 0.4 - passes all unit test in ical_test v0.1
@change: 0.4 to 0.5 adds EXDATE support
@change: 0.5 to 0.6 adds support for no DTEND and DTEND computation from DURATION or DTSTART
@version: 0.6.1y
"""

from datetime import tzinfo, timedelta, datetime, date

from icalendar_SCM import RFC5545_SCM, ESCAPEDCHAR,RFC5545_Properties,RFC5545_FREQ,weekday_map,MaxInteger, CRLF,RFC5545_eventprop_count
from RFC5546_SCM import RFC5546_METHODS
import uuid

class newTZinfo(tzinfo):
    
    """ Overrides abstract class tzinfo from datetime to provide mean for TZID support from ical
    """
    name = ""
    def setID(self,ID):
        self.name = ID
    def getID(self):
        return self.name

    def utcoffset(self, dt):
        return timedelta(hours=0) + self.dst(dt)
    def dst(self, dt):
        return timedelta(hours=0)

class vevent:
    
    """ Parses a vevent (object from vcalendar as defined by the iCalendar standard (RFC5545)
    """
    lSCM = []
    dSCM = {}
    
    conformance = False
#    vevent_load = { "uid": self.string_load}
    def Validator(self,RFC_SCM,line_count=0,line="",level=0, alttxt = "", show = False):
        #FIXME: need to have one Validator for both event and calendar

#        print "line 111: dSCM, RFC_SCM",self.dSCM,RFC_SCM
        if not RFC_SCM=="3_0":
            self.lSCM.append(RFC_SCM)
            if line_count in self.dSCM:
                self.dSCM[line_count].append(RFC_SCM)
            else:
    #            print line_count
                self.dSCM[line_count]=[RFC_SCM]


        if show or self.conformance:
            if level ==0:
                if line_count==0 and line =="" and alttxt != "":
                    print "Warning: RFC5545 specifies \'%s\', %s"%(RFC5545_SCM[RFC_SCM],alttxt)
                else:
                    print "Warning: RFC5545 specifies \'%s\', following line is not compliant \n line: %s - %s"%(RFC5545_SCM[RFC_SCM],str(line_count),line)
            if level ==1:
                raise Exception("RFC5545 non compliance","RFC5545 specifies: \'%s\', following line is not compliant \n line: %s - %s"%(RFC5545_SCM[RFC_SCM],str(line_count),line))
            elif level ==-1:
                print alttxt
                
    def _icalindex_to_pythonindex(self,indexes):
        #FIXME: change this to load_integerlist and add check that we have "," as list separator (and no other values)
        ret_val = []
        for index in indexes:
            index = int(index)
#            if index > 0:
#                #ical sees the first as a 1 whereas python sees the 0 as the first index for positives
#                index = index -0
            if index>MaxInteger or index<-MaxInteger:
                self.Validator("3.3.8_1","Found: %i",index)
            ret_val.append(index)
        return ret_val
    def line_wrap(self,newline):
        if len(newline)<75:
            ret_val = newline
        else:
            #FIXME: about the utf-8 and mid-octet splitting
            NnewLine = int(len(newline)/73.0)
            ret_val = newline[0:74]+CRLF
            for i in range(1,NnewLine):
                ret_val+=" "+newline[i*73+1:(i+1)*73+1]+CRLF
            ret_val+=" "+newline[(NnewLine)*73+1:]      
        return ret_val
    def string_write(self,string):
        for esc in ESCAPEDCHAR:
            string = string.replace(ESCAPEDCHAR[esc],esc)
        return string
    def string_load(self,propval,param="",LineNumber = 0):
        #TODO add here escaped characters
        ret_val = propval
        for esc in ESCAPEDCHAR:
            ret_val= ret_val.replace(esc,ESCAPEDCHAR[esc])

        return ret_val
    def cal_address_write(self,cal_add,param=""):
        """ takes a mail-to URI and returns a mailto URI"""
        #FIXME: add here validator that URI is valid as per [RFC2368].
        return "mailto:"+cal_add
    def integer_write(self,integer,param=""):
        """ takes an integer and returns a string """
        #FIXME: need to add checks that it is an integer
        return str(integer)
    def integer_load(self,intval,params=[],LineNumber = 0):
        retval = 0
        try:
            retval = int(float(intval))
        except:
            self.Validator("3.3.8_1", LineNumber,  "The following value is not an integer:",intval )    
        if retval > 2147483647 or retval < -2147483648:
            self.Validator("3.3.8_1", LineNumber,  "The following value out of range for the standard:",intval )
        return retval
    def date_write(self,date2w,param=""):
        """ takes date or datetime and returns icalendar date or datetime"""
        dt = datetime(year=2013,month=1,day=26)
        
        if type(dt)==type(date2w):
            datestring = self.string_write(date2w.strftime("%Y%m%dT%H%M%S").upper())
        else :
            datestring = self.string_write(date2w.strftime("%Y%m%d").upper())
        return datestring
    def date_load(self,propval,params=[],LineNumber = 0):
        """ loads the date-time or date value + optional TZID into UTC date-time or date
        
        DTSTART, DTEND, DTSTAMP, UNTIL,..."""
        TZID="TZID not set - floatting"
        newdate = None
        
        for param in params:
            if param.find("TZID=")==0:
                TZID=param.split("=")[1]

        nTZinfo = newTZinfo()

#        retdate=datetime(1970,1,1) 
        yeardate = int(propval[0:4])
        
        if propval.find("-")>=0:
            self.Validator("3.3.12_1",line_count = LineNumber,line = propval)
        
        if yeardate<1582: #retdate<datetime(year=1582,month=10,day=15):
            self.Validator("3.3.5_1", line_count = LineNumber,line = propval,alttxt = "dates prior to 1582/oct/15 might be in julian calendar, prior validation should be undertaken - date moved to 1900 for enumerator")
            propval = "1900"+propval[5:]
        elif yeardate<1875:
            self.Validator("3.3.5_1", line_count = LineNumber,line = propval)
        elif yeardate<1970:
            self.Validator("3.3.5_1", line_count = LineNumber,line = propval,alttxt="1970 however is often a computer epoch limit prior validation should be undertaken before keeping such a past date")
        
        #BEFORE 0.6.1z
#            if len(propval)>8:
#                retdate = datetime.`(propval[:8],"%Y%m%d")
#            else:
#                retdate = datetime.strptime(propval,"%Y%m%d")
        #AFTER 0.6.1.z (included):
        if 'VALUE=DATE' in params:
            if len(propval)>8:
                self.Validator("3.3.4_1","expected date, found: %s"%(propval))
            else:
                newdate = datetime.strptime(propval,"%Y%m%d").date()
        else:
            if propval[len(propval)-1]=="Z":
                propval = propval[:-1]
                if not TZID=="TZID not set - floatting":
                    self.Validator("3.3.5_3", LineNumber, propval)
                TZID = "UTC"
            if len(propval)==15:
                retdate = datetime.strptime(propval[0:15],"%Y%m%dT%H%M%S")
                if not TZID=="TZID not set - floatting":
                    newdate = datetime(retdate.year,retdate.month,retdate.day,retdate.hour,retdate.minute,retdate.second,tzinfo=nTZinfo)
                    newdate.tzinfo.setID(TZID)
                else:
                    newdate = retdate
            elif len(propval)==8:
                #here is the case where we load UNTIL and it is a 'DATE' but we cannot check yet against the DTSTART value type
                newdate = datetime.strptime(propval[0:8],"%Y%m%d").date()
            else:
                self.Validator("3.3.5_2", LineNumber, line = propval)
        
        return newdate
    
    def period_load(self,propval,params=[],LineNumber=0):
        """ Loads period or list of period (via recursion)"""
        ret_per = None
        if propval.find(",")>0:
            #here we call recursively period_load 
            periods = propval.split(",")
            for period in periods:
                res = self.period_load(period,params,LineNumber)
                if not res == None:
                    #res == None if the propval was not valid (most likely will raise an error or warning
                    if ret_per == None:
                        ret_per = [res]
                    else:
                        ret_per.append(res)
        else:
            #here we get a simple period
            if len(propval.split("/"))>2 or len(propval.split("/"))<1 :
                self.Validator("3.3.9_1", LineNumber, propval)
            else:
                [start_datetime,end_datetime_or_positive_duration]=propval.split("/")
                start_datetime = self.date_load(start_datetime, params, LineNumber)
                if end_datetime_or_positive_duration[0]=="P":
                    end_datetime_or_positive_duration = self.duration_load(end_datetime_or_positive_duration, params, LineNumber=LineNumber)
                else:
                    end_datetime_or_positive_duration = self.date_load(end_datetime_or_positive_duration, params, LineNumber)
            ret_per = [start_datetime,end_datetime_or_positive_duration]
                    
        return ret_per
    def duration_write(self,duration):
        return duration
    def duration_load(self,duration,param="",conformance=False,LineNumber = 0):
        self.mycal4log = iCalendar()
        #FIXME: check that datetime.timdelta supports timeoffsets
        """
        FIXME: get below addressed and fixed when adding datetime
        The duration of a week or a day depends on its position in the
      calendar.  In the case of discontinuities in the time scale, such
      as the change from standard time to daylight time and back, the
      computation of the exact duration requires the subtraction or
      addition of the change of duration of the discontinuity.  Leap
      seconds MUST NOT be considered when computing an exact duration.
      When computing an exact duration, the greatest order time
      components MUST be added first, that is, the number of days MUST
      be added first, followed by the number of hours, number of
      minutes, and number of seconds.
        """
        duration_received = duration
        if duration[0]=="P":
            duration = duration[1:]
        tdelta = timedelta()
        years =0
        months =0
        sign =1
        if duration[0:1]=="-":
            duration = duration[1:]
            sign = -1
        if duration.find("T")>=0:
            [date,time]=duration.split("T")
#            date = date[1:]
        else:
            [date , time] = [duration,""]
        pos = date.find("W")
        if pos>0:
            tdelta += timedelta(weeks= sign*int(date[:pos]))
        pos = date.find("Y")
        if (pos)>0:
            years = sign*int(date[:pos])
            date = date[pos+1:]
            if conformance: 
                self.Validator("3.3.6_1",level=1,line_count = LineNumber,line = duration_received) #raise Exception("VEVENT VALIDATOR","encountered a Y parameter in a DURATION field which is prohibited by RFC5545")
            else:
                self.Validator("3.3.6_1",level=0,line_count = LineNumber,line = duration_received)
        pos = date.find("M")
        if pos>0:
            months = sign*int(date[:pos])
            date = date[pos+1:]
#            if conformance: raise Exception("VEVENT VALIDATOR","encountered a M parameter in a DURATION field which is prohibited by RFC5545")
            if conformance: 
                self.Validator("3.3.6_1",level=1,line_count = LineNumber,line = duration_received)
            else:
                self.Validator("3.3.6_1",level=0,line_count = LineNumber,line = duration_received)

        pos = date.find("D")
        if (pos)>0:
            tdelta += timedelta(days = sign*int(date[:pos]))
        pos = time.find("H")
        if (pos)>0:
            tdelta += timedelta(hours = sign*int(time[:pos]))
            time = time[pos+1:]
        pos = time.find("M")
        if (pos)>0:
            tdelta += timedelta(minutes = sign*int(time[:pos]))
            time = time[pos+1:]
        pos = time.find("S")
        if (pos)>0:
            tdelta += timedelta(seconds = sign*int(time[:pos]))
        return [years,months,tdelta]  
    def datelist_write(self,dtlist):
        return  dtlist
    def datelist_load(self,sDatelist,passedparam="",LineNumber = 0):
#        if sDatelist.find(",")>=0:
        sDatelist=sDatelist.split(",")
        lDatelist = []
        #FIXME: make below more robust to tackle all uses case for RDATE,EXDATE, ...
        if "VALUE=PERIOD" in passedparam:
            for value in sDatelist:
                lDatelist.append(self.period_load(value, params=passedparam, LineNumber=LineNumber))
        else:            
            for value in sDatelist:
                lDatelist.append(self.date_load(value,LineNumber = LineNumber, params=passedparam))
#        else:
#            raise Exception("ICALENDAR WARNING", RFC5545_SCM["3.1.1_1"] + "\nline information: %s - %s"%("NA",sDatelist))
        return lDatelist       
    def rrule_load(self,sRrule,param="",LineNumber = 0):
        """ load a string into a rrule object"""
        
        rules = {}
#        self._log("rrule is:",[line])
        rrule = sRrule.split(";")
        rule_count = 0
        for rule in rrule:
            rule_count +=1
#            self._log("120 rule out rules is:",[rule])
            if len(rule)>0:
                #FIXME: this is to cater for line ending with ; which is probably not valid
                [param, value] = rule.split("=")
                if param in rules:
                    self.Validator("3.3.10_1","%s rule part is defined twice in RRULE (Line: %i)"%(param,LineNumber))
                if (param == "FREQ"):
                    rules[param] = value
                    if rule_count >1:
                        #FREQ should be first rule part
                        self.Validator("3.3.10_2","see RRULE (Line: %i)"%(LineNumber))
                    if not value in RFC5545_FREQ :
                        self.Validator("3.3.10_5","see RRULE (Line: %i)"%(LineNumber))
                        
                elif (param == "UNTIL"):
                    #FIXME: see "3.3.10_6b"
                    rules[param] = self.date_load(value)
                elif (param == "COUNT"):
                    try:
                        count_instances = int(value)
                    except:
                        self.Validator("3.3.10_6","see RRULE (Line: %i)"%(LineNumber))
                    if count_instances <0:
                        self.Validator("3.3.10_6","see RRULE (Line: %i)"%(LineNumber))
                    else:
                        rules[param] = count_instances
                elif (param == "INTERVAL"):
                    #( ";" "INTERVAL" "=" 1*DIGIT )          /
                    rules[param] = int(value)
                elif (param == "BYSECOND"):
                    #( ";" "BYSECOND" "=" byseclist )        /
                    #byseclist  = seconds / ( seconds *("," seconds) )
                    #seconds    = 1DIGIT / 2DIGIT       ;0 to 59
                    byseclist = value.split(",")
                    rules[param]=[]
                    for seconds in byseclist:
                        if seconds>60:
                            self.Validator("3.3.10_7")
                        rules[param].append(int(seconds))
                elif (param == "BYMINUTE"):
                    if seconds>59:
                        self.Validator("3.3.10_8")
                    rules[param] = value
                elif (param == "BYHOUR"):
                    rules[param] = value
                elif (param == "BYDAY"):
                    #( ";" "BYDAY" "=" bywdaylist )          /
                    #bywdaylist = weekdaynum / ( weekdaynum *("," weekdaynum) )
                    #weekdaynum = [([plus] ordwk / minus ordwk)] weekday
                    #plus       = "+"
                    #  minus      = "-"
                    #  ordwk      = 1DIGIT / 2DIGIT       ;1 to 53
                    #  weekday    = "SU" / "MO" / "TU" / "WE" / "TH" / "FR" / "SA"
                    #;Corresponding to SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY,
                    #;FRIDAY, SATURDAY and SUNDAY days of the week.
                    #bywdaylist = split(value,",")
                    #for weekdaynum in bywdaylist:
                    rules[param] = {}
                    ldow = {}   #dictionnary with dow and list of index
                    #{'MO': [0], 'TU': [1], 'WE': [-1]} means every monday, first tuesday
                    # last wednesday, .. 
                    bywdaylist = value.split(",")
                    dow = ["MO","TU","WE","TH","FR","SA","SU"]
                    for weekdaynum in bywdaylist:
                        #get the position of the DOW
                        #weekdaynum of type: MO , 1MO, 2TU or -2WE
                        for d in dow:
                            if weekdaynum.find(d) >=0:
                                pos_dow = weekdaynum.find(d)
                        #extract position of dow to split its index from it.
                        if pos_dow == 0:
                            index = 0
                        else:
                            index = int(weekdaynum[0:pos_dow])
                        ddow = weekdaynum[pos_dow:]
                        if ddow in ldow:
                            ldow[ddow].append(index)
                        else:
                            ldow[ddow] = [index]
                    rules[param] = ldow
#                    self._log("175",[rules[param],param])
                elif (param == "BYMONTHDAY"):
                    # ( ";" "BYMONTHDAY" "=" bymodaylist )    /
                    # bymodaylist = monthdaynum / ( monthdaynum *("," monthdaynum) )
                    # monthdaynum = ([plus] ordmoday) / (minus ordmoday)
                    # ordmoday   = 1DIGIT / 2DIGIT       ;1 to 31
                    bymodaylist = value.split(",")
                    rules[param] = self._icalindex_to_pythonindex(bymodaylist)
                elif (param == "BYYEARDAY"):
                    byyeardaylist = value.split(",")
                    rules[param] = self._icalindex_to_pythonindex(byyeardaylist)
                elif (param == "BYWEEKNO"):
                    bywklist = value.split(",")
                    rules[param] = self._icalindex_to_pythonindex(bywklist)
                elif (param == "BYMONTH"):
                    #";" "BYMONTH" "=" bymolist )
                    #bymolist   = monthnum / ( monthnum *("," monthnum) )
                    #monthnum   = 1DIGIT / 2DIGIT       ;1 to 12
                    bymolist = value.split(",")
                    rules[param] = self._icalindex_to_pythonindex(bymolist)
                elif (param == "BYSETPOS"):
                    #( ";" "BYSETPOS" "=" bysplist )         /
                    # bysplist   = setposday / ( setposday *("," setposday) )
                    # setposday  = yeardaynum
                    bysplist = value.split(",")
                    rules[param] = self._icalindex_to_pythonindex(bysplist)
                elif (param == "WKST"):
                    rules[param] = value
                else:
                    rules[param] = value
                    
        if not "FREQ" in rules:
            self.Validator("3.3.10_3",LineNumber)
        if "UNTIL" in rules and "COUNT" in rules:
            self.Validator("3.3.10_4",LineNumber)
            
        return rules
    def rrule_write(self,sRRULE):
        return sRRULE
    def validate_event(self,event2validate):
        """ validates the event against RFC5545 rules"""
        addsummary = ""
        adduid = ""
        event = {}
        
        
        for prop in event2validate:
            if "val" in event2validate[prop]:
                event[prop]=event2validate[prop]["val"]
            else:
                event[prop]=event2validate[prop]

        if "SUMMARY" in event:
            addsummary = " event summary:"+event["SUMMARY"]
        if "UID" not in event:
            self.Validator("3.6.1_3",alttxt = addsummary) #raise Exception("VEVENT VALIDATOR","mandatory property UID not set"+addsummary)
            #FIXME: make sure this propagates
            event["UID"]={"val":"tempUID_AddedbyPyICSParser"+str(uuid.uuid1())}
        else:
            adduid = " event UID:"+event["UID"]
#        if "DTSTART" not in event:
#            #FIXME no DTSTART is valid, but should raise a warning
#            raise Exception("VEVENT VALIDATOR","mandatory property DTSTART not set"+adduid+addsummary)            
        if "DTEND" in event:
            if "DURATION" in event:
                self.Validator("3.6.1_4",alttxt = adduid+addsummary)
            if "DTSTART" in event:
                if event["DTSTART"] > event["DTEND"]:
                    self.Validator("3.8.2.2_1",alttxt="for enumerationn, DTEND is replaced with DTSTART, event impacted:"+adduid+addsummary)#raise Exception("VEVENT VALIDATOR","DTSTART > DTEND"+adduid+addsummary)
                    event["DTEND"] = event["DTSTART"]
        
        #check that all events have the same value type for all date/date-time
        if ("DTSTART" in event) and ("DTEND" in event):
            if not ( type(event["DTSTART"]) == type(event["DTEND"]) ): 
                self.Validator("3.6.1_5")
        if "RRULE" in event:
            if "UNTIL" in event["RRULE"] and "DTSTART" in event:
                if not ( type(event["DTSTART"]) == type(event["RRULE"]["UNTIL"]) ): 
                    self.Validator("3.3.10_6b")
        if "RDATE" in event and "DTSTART" in event:
            for rdate in event["RDATE"]:
                if not type(rdate) == type (event["DTSTART"]):
                    self.Validator("3.8.5.2_0", alttxt = "rdate value %s does not match DTSTART: %s"%(str(rdate),str(event["DTSTART"])))

        if "EXDATE" in event and "DTSTART" in event:
            for exdate in event["EXDATE"]:
                if not type(exdate) == type (event["DTSTART"]):
                    self.Validator("3.8.5.1_0", alttxt = "rdate value %s does not match DTSTART: %s"%(str(rdate),str(event["DTSTART"])))

        if "RRULE" in event and ("DTSTART" in event):
            if type(event["DTSTART"]) == type(date(2003,3,5)):
                if ("BYSECOND" in event["RRULE"]["FREQ"]) or ("BYMINUTE" in event["RRULE"]["FREQ"]) or ("BYHOUR" in event["RRULE"]["FREQ"]):
                    self.Validator("3.3.10_10")
        if "RRULE" in event:
            if "BYYEARDAY" in event["RRULE"]:
                if "YEARLY" in event["RRULE"]["FREQ"]:
                    for daypos in event["RRULE"]["BYYEARDAY"]:
                        if daypos>366 or daypos<-366:
                            self.Validator("3.3.10_11", "found BYYEARDAY value : %i while RRULE,FREQ=%s for EVENT with UID:%s"%(daypos,event["RRULE"]["FREQ"],adduid))
                if "MONTHLY" in event["RRULE"]["FREQ"]:
                    for daypos in event["RRULE"]["BYDAY"]:
                        if daypos>31 or daypos<-31:
                            self.Validator("3.3.10_11", "found BYDAY value : %i while RRULE,FREQ=%s for EVENT with UID:%s"%(daypos,event["RRULE"]["FREQ"],adduid))
            if "BYWEEKNO" in event["RRULE"]:
                for weekpos in event["RRULE"]["BYWEEKNO"]:
                    if weekpos>53 or weekpos<-53:
                        self.Validator("3.3.10_14", "found BYWEEKNO value : %i for EVENT with UID:%s"%(weekpos,adduid))
                if not "YEARLY" in event["RRULE"]["FREQ"]:
                    self.Validator("3.3.10_15", "found BYWEEKNO value for EVENT with FREQ: % and whose UID:%s"%(event["RRULE"]["FREQ"],adduid))
            if "BYMONTH" in event["RRULE"]:
                for monthpos in event["RRULE"]["BYMONTH"]:
                    if monthpos<0 and monthpos>12:
                        self.Validator("3.3.10_16", "found BYMONTH value: %i  for EVENT whose UID:%s"%(monthpos,adduid))
            if "WKST" in event["RRULE"]:
                if not event["RRULE"]["WKST"] in weekday_map :
                    self.Validator("3.3.10_17","found WKST = %s for EVENT whose UID:%s"%(event["RRULE"]["WKST"],adduid) )
                        
            if "BYMONTHDAY" in event["RRULE"] and "WEEKLY" in event["RRULE"]["FREQ"]:
                self.Validator("3.3.10_12", "both set for EVENT with UID:%s"%(adduid))
            if "BYYEARDAY" in event["RRULE"] and (("DAILY" in event["RRULE"]["FREQ"]) or ("WEEKLY" in event["RRULE"]["FREQ"]) or ("MONTHLY" in event["RRULE"]["FREQ"])):
                self.Validator("3.3.10_13", "both set for EVENT with UID:%s"%(adduid))
                    

class iCalendar:
    
    """ iCalendar (RFC5545, RFC2445) parser/validator/generator/events enumerator 
    
    Parse, Generate and enumerate events (support of RRULE, EXRULE, RDATE, EXDATE) usage:

    Enumerator:
        mycal = icalendar.ics()\n
        mycal.local_load(icalendarfile.ics)\n
        #icalendarfile.ics is the local path\n
        dates = mycal.get_event_instances(sDate,eDate)\n
        #start end end are strings in yyyymmdd format\n
        #dates will contain the json with all explicit dates of the events spec'ed by the iCalendar file\n

    Validator:
        mycal = icalendar.ics()\n
        mycal.local_load(icalendarfile.ics)\n
        #icalendarfile.ics is the local path\n
        mycal.parse_loaded(conformance=True)\n
        #When conformance is True it displays on console non critical error from icalendar file\n


    """
    version = "0.6.2a5"
    OccurencesWindowStartDate = ""
    """ Date from which occurences of iCalendar events should be returned by the enumerator"""
    OccurencesWindowEndDate = ""
    """ Date until which occurences of iCalendar events should be returned by the enumerator"""
    sVCALENDAR = [] #the VCALENDAR as a string
    dVCALENDAR = {} #the VCALENDAR as a typed object
    lVEVENT = [] #the current VEVENT being loaded from iCalendar file, array of strings each string is an unfolded
    conformance = False
    ical_loaded = 0
    events = []
    vevent = vevent()
    """ object holding all the vevent objects (with typed data) from the parsed iCalendar """
    debug_mode = False
    debug_level = 0
    LogFilePath = "./log.txt"
    lSCM=[]
    dSCM={}
    LogData = ""
    def inf(self):
        """ Returns generic info """
        info = "Follows:\n"
        info += "http://www.kanzaki.com/docs/ical/vevent.html \n"
        info += "http://www.kanzaki.com/docs/ical/rrule.html \n"
        info += "http://www.kanzaki.com/docs/ical/recur.html \n"
        info += "version: %s \n"%(self.version)
    def _reset(self):
        
        self.sVCALENDAR = []
        self.dVCALENDAR = {}
        self.lSCM = []
        self.dSCM = {}
        self.vevent = vevent()
        self.events = []
        self.ical_loaded = 0
        self.conformance = False
        self.lVEVENT = []
        
    def __init__(self):
        self.ical_loaded = 0
        self.debug_mode= 0
    def __del__(self):
        self.ical_datelist = []
        self.events_instances = []
    def debug(self,TrueFalse,LogPath="",debug_level=0):
        """ enables logging when executing (warning severe slow down)"""
        self.debug_mode = TrueFalse
        self._log("self debug is now",[TrueFalse])
        self.debug_level = debug_level
        self.LogFilePath = LogPath
        if len(LogPath)>0:
            try:
                log = open(self.LogFilePath,'w')
                log.write("Icalendar module version: %s, date/time running: %s"%(str(self.version),str(datetime.now())))
                log.close()
            except:
                raise Exception("File IO error","Could not open with write rights on log file:"+LogPath)
    def _log(self,title,listtodisplay,level=0):
        if self.debug_mode == True:
            if level >= self.debug_level:
                line = "**"+title+": \t"
                for el in listtodisplay:
                    if len(str(el))<1000:
                        line = line + "\t"+str(el)
                    else:
                        line = line + "\t"+str(el)[0:1000]
                line +="\n"
                if len(self.LogFilePath)>0:
                    log=open(self.LogFilePath,'a')
                    log.write(line)
                    log.close()
                else:
                    self.LogData += line
    def GenRRULEstr(self,rules):
        """ Generates RRULE string from rules dictionary
        
        Used by generator. 
        """
        
        RRULE="RRULE:"
        if "FREQ" in rules:
            RRULE+="FREQ="+rules["FREQ"]+";"
            if "INTERVAL" in rules:
                RRULE += "INTERVAL="+str(rules["INTERVAL"])+";"
            if "COUNT" in rules:
                RRULE += "COUNT="+str(rules["COUNT"])+";"
            bylist = ["BYWEEKNO","BYMONTH","BYMONTHDAY","BYDAY","BYYEARDAY","BYSETPOS"]
            for bys in bylist:
                if bys in rules:
                    numlist = rules[bys]
                    icallist = self._pythonindex_to_icalindex(numlist)
                    RRULE+=bys+"="+icallist+";"
        if "WKST" in rules:
            RRULE+="WKST="+rules["WKST"]+";"
        if "UNTIL" in rules:
            RRULE+= "UNTIL"+rules["UNTIL"]+";"
        if RRULE[-1]==";":
            RRULE = RRULE[:-1]
        return RRULE
    def Validator(self,RFC_SCM,line_count=0,line="",level=0, alttxt = "", show = False):
        """ when set for conformance logging (self.conformance == True) will display and log non-conformance """
        
#        print "line 695: dSCM, RFC_SCM",self.dSCM,RFC_SCM
        if not RFC_SCM=="3_0":
            self.lSCM.append(RFC_SCM)
            if line_count in self.dSCM:
                self.dSCM[line_count].append(RFC_SCM)
            else:
    #            print line_count
                self.dSCM[line_count]=[RFC_SCM]
#        print "line 703:",self.dSCM

        if show or self.conformance:
            if level ==0:
                if line_count==0 and line =="" and alttxt != "":
                    print "Warning: RFC5545 specifies \'%s\', %s"%(RFC5545_SCM[RFC_SCM],alttxt)
                else:
                    print "Warning: RFC5545 specifies \'%s\', following line is not compliant \n line: %s - %s"%(RFC5545_SCM[RFC_SCM],str(line_count),line)
            if level ==1:
                raise Exception("RFC5545 non compliance","RFC5545 specifies: \'%s\', following line is not compliant \n line: %s - %s"%(RFC5545_SCM[RFC_SCM],str(line_count),line))
            elif level ==-1:
                print alttxt
    def local_load(self,sLocalFilePath,conformance=False):
        """loads iCalendar file from local path
        
        conformance will force / or not checking ics file for conformance (not supported yet)
        """
        self.sVCALENDAR = []
        self.dVCALENDAR = {}
        self.events = []
        self.events_instances = []
        self.lSCM = []
        self.dSCM = {}
        self.vevent.lSCM = []
        self.vevent.dSCM = {}
            
        self.conformance = conformance
        self.vevent.conformance = conformance
        self._log("\t\t entering local load:",[sLocalFilePath])
        self.Validator("3_0", alttxt="***********************************************************************************************\n*** \t\t Validating file: %s\t\t ***\n***\t\t with module version %s \t\t\t\t\t****\n***********************************************************************************************"%(sLocalFilePath,self.version),level = -1)

#        self.local_path = path
        #here check local path
        string = open(sLocalFilePath,'r').readlines()
        #FIXME: add here the CRLF check and remove the \n from strings_load
        #RFC5545_SCM["3.1_1"]
        self.strings_load(string,conformance)
    def string_load(self,string,conformance=False):
        string = string.replace("\r\n","\n")
        string = string.replace("\r","\n")
        strings = string.split("\n")
        self.strings_load(strings, conformance)

    def strings_load(self,strings,conformance=False):
        """Loads iCalendar from array of strings

        conformance will force / or not checking ics file for conformance (not supported yet)
        """
        self.sVCALENDAR = []
        self.dVCALENDAR = {}
        self.events = []
        self.events_instances = []
        self.lSCM = []
        self.vevent.lSCM =[]
        
        
        line_count = 0
        if not (strings[0].replace("\n","").replace("\r","") == "BEGIN:VCALENDAR"):
            self.Validator("3.4_1", line_count =0, line = strings[0])
        if (not (strings[-1].replace("\n","").replace("\r","") == "END:VCALENDAR")) or (not (strings[-1][-1]=="\n" or strings[-1][-1]=="\r")):
            self.Validator("3.4_2",line_count =len(strings),line = strings[-1])
        for line in strings:
            self._log("current sVCALENDAR, new line:", [self.sVCALENDAR,line], 0)
            line_count +=1
#            print "\t\t %s line:%s"%(line_count ,line)

            if len(line)>1:
                if line[-2:-1] == "\n\r":
                    pass
                else:
                    #FIXME: check why the local files are not conformant
    #                self.Validator("VCALENDAR VALIDATOR: WARNING",RFC5545_SCM['3.1_1']+ "%s : %s"%(line_count,line),0)
                    pass
                if line[0]==" " and len(self.sVCALENDAR)>0:
                    self._log("line wrapper before",[line,self.sVCALENDAR])
                    self.sVCALENDAR[-1]=self.sVCALENDAR[-1]+line[1:].replace("\n","").replace("\r","")
                    self._log("line wrapper after",[line,self.sVCALENDAR])
                elif line[0]==" ":
                    self.Validator("3.1_2",line = line,line_count = line_count, level =0)
                elif line.find(":")>0:
                    self._log("line legnth",[len(line)])
                    if  len(line)<76:
                        self.sVCALENDAR.append(line.replace("\n","").replace("\r",""))
    #                    self._log("sVCALENDAR added ?", [self.sVCALENDAR,line], 0)
                    elif len(line)>75:
                        self.Validator("3.1_3",line = line,line_count = line_count,level = 0)
                        self.sVCALENDAR.append(line.replace("\n","").replace("\r",""))
    #                    self._log("sVCALENDAR added ?", [self.sVCALENDAR,line], 0)
                    elif len(line)> 75 and len(line)<1000:
                        self.Validator("3.1_3",line = line,line_count = line_count,level = 0)
                        self.sVCALENDAR.append(line.replace("\n","").replace("\r",""))
                    else :
                        self.Validator("3.1_4",line = line,line_count = line_count,level = 1)
                else:
                    self.Validator('3.1_2',line = line,line_count = line_count,level =0)
            else:
                self.Validator('3.1_2',line = line,line_count = line_count,level =0)

        self.ical_loaded = 1
    def _validate(self):
        """ Will secure UID only present once at least in the file"""
        uidlist = []
        for event in self.events:
            if not "UID" in event:
                event["UID"]=str(uuid.uuid1())+"@pyICSPARSER"
            if event["UID"] not in uidlist:
                uidlist.append(event["UID"])
            else:
                self.Validator("3.8.4.7_1", alttxt = "this UID was found more than once in current file:"+event["UID"]["val"])

    def _mklist(self,start,end,step_size=1):
        #TODO:historical function created before knowing the range function, to be removed
#        result_list = []
#        while start <= end:
#            list.append(start)
#            start +=step_size
        result_list = range(start,end+1,step_size)
        return result_list

    def parse_loaded(self):
        """ parse loaded ical from file to array of typed data: self.events"""
        VCALENDAR_Components = {"VEVENT","VTIMEZONE","VTODO","VFREEBUSY","VJOURNAL"}
        Component_Name = ""
        Component_Stack =[]
        print "temp 835 - entering parse loaded"
        import sys,traceback
        for thread, frame in sys._current_frames().items():
            print('Thread 0x%x' % thread)
            traceback.print_stack(frame)

        self._log("\t\tentering loader",[])
        invevent = 0
        LineCountBE = 0 #Line count at which the Begin:VEVENT was found
        if self.ical_loaded == 0:
            self._log("error ",[RFC5545_SCM["3_1"]])
            self.Validator("3_1", level=1) #("VCALENDAR VALIDATOR","no vCALENDAR loaded")
#            self.ical_error = 1
#            return 0
        elif self.ical_loaded == 1:
            #TODO: add here increments over the calendars
            self._log("ical loaded", [self.ical_loaded,self.sVCALENDAR],0)
            line_count = 0
            for line in self.sVCALENDAR:
                self._log("line is ", [line], 0)
                line_count +=1
                #first load the given event
#                pos = line.find("BEGIN:")
                if (line.find("BEGIN:")==0):
                    self._log("new component?: LN / line / name",[line_count,line])
                    new_Component_Name= self._propval_line_split(line.replace("\n",""),line_count)[2] # ":".join(line.split(":")[1:]).replace("\n","")
                    if new_Component_Name in VCALENDAR_Components:
                        self._log("found new component: LN / line / name",[line_count,line,new_Component_Name])
                        Component_Stack.append(Component_Name)
                        Component_Name = new_Component_Name 
                        if (invevent == 0):
                            invevent = 1
                            self.lVEVENT =[]
                            LineCountBE = line_count
                        else:
                            self.Validator("3.6.1_1", line_count = line_count, line = line, level = 1) #raise Exception("VCALENDAR VALIDATOR","encountered BEGIN:%s before END:VEVENT @line: %s"%(Component_Name,str(line_count)))
#                            self.ical_error = 1
                    else:
                        #FIXME: if we have a IANA or X-COMP
                        pass
#                pos = line.find("END:")
                elif (line.find("END:")==0):
                    self._log("new end?: LN / line ",[line_count,line])
                    #if we have a event closing tag
                    closing_Component = self._propval_line_split(line.replace("\n",""),line_count)[2]#":".join(line.split(":")[1:]).replace("\n","") 
                    self._log("found end component: LN / line / name",[line_count,line,closing_Component ])
                    if closing_Component == Component_Name :
                        if invevent ==1:
                            #if we were already adding an event - stop adding
                            invevent = 0
#                            self.lVEVENT = self.lVEVENT+ [line.replace("\n","")]
                            self._log("event is", self.lVEVENT,2)
                            if Component_Name == "VEVENT":
                                self._addEvent(self.lVEVENT,LineCountBE)
                                Component_Name = Component_Stack.pop()
                            elif Component_Name == "VTIMEZONE":
                                #FIXME: add the function pointer here
                                pass
                    elif closing_Component in VCALENDAR_Components:
#                        self.ical_error = 1
                        self.Validator("3.6.1_1", line_count = line_count, line = line, level = 1,show=True) #raise Exception("VCALENDAR VALIDATOR","encountered END:%s instead of END:%s @line: %s"%(closing_Component,Component_Name,str(line_count)))
                    else:
                        #FIXME: add code here for handling IANA and X-COMP
#                        raise Exception("IANA or X-PROPERTY","Not supported yet")
                        pass
                else:
                    if (invevent ==1):
                        self.lVEVENT = self.lVEVENT + [line]
                    else:
                        #here adding the calendar  properties
                        [prop,param, val] = self._propval_line_split(line,line_count)
                        self.dVCALENDAR[prop]={"param":param,"val":val}
            
            if Component_Name == "":
                self.Validator("3.6_3")
        if "PRODID" not in self.dVCALENDAR:
            self.Validator("3.6_1",alttxt = "Parsed all calendar and was not found")
        if "VERSION" not in self.dVCALENDAR:
            self.Validator("3.6_2",alttxt = "Parsed all file and was not found")
        self._log("END Loader",[],0)
            
#        if self.conformance:
        self._validate()
        self.lSCM= self.lSCM + self.vevent.lSCM
        for line in self.dSCM:
            if line in self.vevent.dSCM:
                self.dSCM[line]+=self.vevent.dSCM[line]
        for line in self.vevent.dSCM:
            if line not in self.dSCM:
                self.dSCM[line]=self.vevent.dSCM[line]
                #        return 1
    def _addEvent(self,lVEVENT,EventFirstLine = 0):
        """
        loads self.event which is a string into 
        self.events which is an array of python types
        """
        self._log("\t\tentering event_load",[])
        self._log("list of vevents when entering",[self.events])
        dVevent = {}
        vevent_load = { "TEXT": self.vevent.string_load,
                   "DATE-TIME-LIST": self.vevent.datelist_load,
                   "DATE-TIME": self.vevent.date_load,
                   "DURATION":self.vevent.duration_load,
                   "INTEGER":self.vevent.integer_load,
                   "RECUR":self.vevent.rrule_load}
        line_count = EventFirstLine
        for line in lVEVENT:
            line_count +=1
            if line.find(":")>0:
                [prop,param,values]=self._propval_line_split(line,line_count)    #[line.split(":")[0],":".join(line.split(":")[1:])]
                prop = prop.upper()
                try:
                    #here parse the value as per its type into python type
                    res = vevent_load[RFC5545_Properties[prop]](values,param,LineNumber = line_count)
                except KeyError:
                    res = values
            else:
                self.Validator("3.1_2", line_count = line_count, line = line)#raise Exception("VEVENT VALIDATOR","mandatory property not set on line"+line)
            if prop in dVevent:
                #FIXME: need to support multiple RRULE lines
                if (prop in RFC5545_eventprop_count["1"]) or (prop.upper() in RFC5545_eventprop_count["01"]):
                    self.Validator("3.6.1_2", line_count = line_count, line = line)
                else:
                    #FIXME: need to add code for handling when properties set multiple times
                    if not res == None and not (prop == "RRULE"):
                        dVevent[prop]= [dVevent[prop],{"param":param,"val":res}]
                    else:
                        self.Validator("3.8.5.3_1", line_count, line)
            else:
                if not res == None:
                    dVevent[prop] = {"param":param,"val":res}
#                dVevent[prop] = res

        self.vevent.validate_event(dVevent)

        if "DTSTART" not in dVevent:
            if "UID" in dVevent:
                uid = dVevent["UID"]["val"]
            else:
                uid = "not available"

            if "RRULE" in dVevent: 
                self.Validator('3.8.2.4_1', alttxt="DTSTART missing for event with UID:"+uid, level = 0) #raise Exception("VEVENT VALIDATOR", RFC5545_SCM['3.8.2.4_1'])
            elif "METHOD" not in self.dVCALENDAR:
                self.Validator('3.8.2.4_2', alttxt="DTSTART missing for event with UID:"+uid)#raise Exception("VEVENT VALIDATOR", RFC5545_SCM['3.8.2.4_2'])
            elif 'DTEND' in dVevent:
                self.Validator("3.6.1_0", alttxt = "DTSTART will be computed from DTEND and DURATION from event with UID: "+uid,level=0)
            else:
                self.Validator("3.6.1_0", alttxt="not enough information for event with UID :"+uid)

            
        self.events.append(dVevent)
        self._log("*** VEVENT ADDED",[dVevent])
        self._log("list VEVENT so far: ",[self.events])
#        self.event = []
        return dVevent
    def _pythonindex_to_icalindex(self,indexes,isDOW=False):
        """ used by generator to make iCalendar lists """
        ret_val = ""
        for index in indexes:
            ret_val += str(index)+","
        if ret_val[-1]==",":
            ret_val=ret_val[:-1]
        return ret_val
    def _flatten(self,slot_dur=timedelta(days=1)):
#        print "entering flatten"
#        import sys,traceback
#        for thread, frame in sys._current_frames().items():
#            print('Thread 0x%x' % thread)
#            traceback.print_stack(frame)
        """ goes over self.events and compute list of their instances"""
        self._log("******************\t\t\t entering _flatten",[])
        self.events_instances = []
        
        UTC = newTZinfo()
        
        for event in self.events:
            tmp_event = event
            if not "DTSTART" in tmp_event:
                if not "DTEND" in tmp_event:
                    #we should never be here as this was checked at loading
                    raise Exception("VEVENT ERROR","Missing both DTSTART and DTEND, correct per RFC5545 but not enumerable")
                elif not "DURATION" in tmp_event:
                    tmp_event["DTSTART"]=tmp_event["DTEND"]["val"]
                else:
                    tmp_event["DTSTART"] = tmp_event["DTEND"]["val"]+tmp_event["DURATION"]["val"][2]
            else:
                tmp_event["DTSTART"]=tmp_event["DTSTART"]["val"]
                
            #convert DTSTART time to a floatting
            if type(tmp_event["DTSTART"]) == type(datetime(year = 2003, month=3,day =5, tzinfo=UTC)):
                utcoffset = tmp_event["DTSTART"].utcoffset()
                tmp_event["DTSTART"]=datetime(year= tmp_event["DTSTART"].year,
                                              month = tmp_event["DTSTART"].month,
                                              day = tmp_event["DTSTART"].day,
                                              hour = tmp_event["DTSTART"].hour,
                                              minute = tmp_event["DTSTART"].minute,
                                              second = tmp_event["DTSTART"].second)
                tmp_event["DTSTART"] = tmp_event["DTSTART"] +utcoffset

            """
            For cases where a "VEVENT" calendar component
            specifies a "DTSTART" property with a DATE value type but no
            "DTEND" nor "DURATION" property, the event's duration is taken to
            be one day.  For cases where a "VEVENT" calendar component
            specifies a "DTSTART" property with a DATE-TIME value type but no
            "DTEND" property, the event ends on the same calendar date and
            time of day specified by the "DTSTART" property.
            """
            if "DTEND" not in tmp_event:
                if "DURATION" not in tmp_event:
                    tmp_event["DTEND"] = tmp_event["DTSTART"]
                else:
                    tmp_event["DTEND"] = tmp_event["DTSTART"]+tmp_event["DURATION"]["val"][2]
                    #FIXME: add here the code for handling the DTEND+DURATION (years and months) - need to make
                    #the code either "instances accurate" or "date accurate"
                    #call: event["DTEND"] = add_year_months(event["DTEND"], event["DURATION"][1], event["DURATION"][0])
            else:
                tmp_event["DTEND"] = tmp_event["DTEND"]["val"]


            #convert DTEND time to a floatting
            if type(tmp_event["DTEND"]) == type(datetime(year = 2003, month=3,day =5, tzinfo=UTC)):
                utcoffset = tmp_event["DTEND"].utcoffset()
                tmp_event["DTEND"]=datetime(year= tmp_event["DTEND"].year,
                                              month = tmp_event["DTEND"].month,
                                              day = tmp_event["DTEND"].day,
                                              hour = tmp_event["DTEND"].hour,
                                              minute = tmp_event["DTEND"].minute,
                                              second = tmp_event["DTEND"].second)
                if not type(utcoffset)== type(None):
                    tmp_event["DTEND"] = tmp_event["DTEND"] +utcoffset
                    
            #convert UNTIL time to floatting
            if "RRULE" in tmp_event:
                if "UNTIL" in tmp_event["RRULE"]["val"]:
                    if type(tmp_event["RRULE"]["val"]["UNTIL"]) == type(datetime(year = 2003, month=3,day =5, tzinfo=UTC)):
                        utcoffset = tmp_event["RRULE"]["val"]["UNTIL"].utcoffset()
                        tmp_event["RRULE"]["val"]["UNTIL"]=datetime(year= tmp_event["RRULE"]["val"]["UNTIL"].year,
                                                      month = tmp_event["RRULE"]["val"]["UNTIL"].month,
                                                      day = tmp_event["RRULE"]["val"]["UNTIL"].day,
                                                      hour = tmp_event["RRULE"]["val"]["UNTIL"].hour,
                                                      minute = tmp_event["RRULE"]["val"]["UNTIL"].minute,
                                                      second = tmp_event["RRULE"]["val"]["UNTIL"].second)
                        if not type(utcoffset)== type(None):
                            tmp_event["RRULE"]["val"]["UNTIL"] = tmp_event["RRULE"]["val"]["UNTIL"] +utcoffset
            
            if "SUMMARY" in tmp_event:
                tmp_event["SUMMARY"]=tmp_event["SUMMARY"]["val"]
            else:
                tmp_event["SUMMARY"] = ""
            
            summary = tmp_event["SUMMARY"]
            
            self._log("event being _flatten is:",tmp_event)

            #FIXME: add here the multiple RRULE / EXRULE unfolding
            #event = #        [dtstart,dtend,rules, summary,uid,rdates,exdates] = event

            if "RRULE" in tmp_event:
                tmp_event["RRULE"]=tmp_event["RRULE"]["val"]
            else:
                tmp_event["RRULE"]=[]

            if type(tmp_event["DTSTART"])==type(date(2003,5,3)):
                WindowStart =self.OccurencesWindowStartDate.date()
                WindowEnd = self.OccurencesWindowEndDate.date()
            else:
                WindowStart =self.OccurencesWindowStartDate
                WindowEnd = self.OccurencesWindowEndDate
                
            """ **********************************************************
                THIS IS WHERE WE MAKE THE CALL TO ENUMERATE ALL INSTANCES
                **********************************************************
            """
            self._log("temp 1092",[self.events_instances])
            t_res = self._flatten_rrule(tmp_event,WindowStart,WindowEnd)

            self._log("*****************dates returned from _flatten_rrule",[t_res])
                
            """
                ***********************************************************
            """

            if "RDATE" in tmp_event:
                rdates = tmp_event ["RDATE"]["val"]
            else:
                rdates = []

            if "EXDATE" in tmp_event:
                exdates = tmp_event["EXDATE"]["val"]
                #convert EXDATES time to floatting
                if type(exdates[0])==type(datetime(2013,2,6,10,28,0,tzinfo=UTC)):
                    pass
                if len(rdates)>0:
                    rdates = [val for val in rdates if val not in exdates]
                    t_res = [val for val in t_res if val not in exdates]
            else:
                exdates = []
            
            """ FIXME:
            If the duration of the recurring component is specified with the
            "DTEND" or "DUE" property, then the same exact duration will apply
            to all the members of the generated recurrence set.  Else, if the
            duration of the recurring component is specified with the
            "DURATION" property, then the same nominal duration will apply to
            all the members of the generated recurrence set and the exact
            duration of each recurrence instance will depend on its specific
            start time.  For example, recurrence instances of a nominal
            duration of one day will have an exact duration of more or less
            than 24 hours on a day where a time zone shift occurs.  The
            duration of a specific recurrence may be modified in an exception
            component or simply by using an "RDATE" property of PERIOD value
            type.
            """
            """
            delta = timedelta(days = 1)
            t_date +=delta
                    
            while t_date < dtend:
                list_dates.append(t_date)
                t_date +=delta
                self._log("from dtstart to dtend",[dtstart,dtend,t_date,list_dates],0)

            """                
            res_slots_rdate = []
            if len(rdates)>0:
                #here make sure that duplication of rrule and rdate do not result in 2 instances !
                #also apply RFC5545 §5.2 recommendation: when occurence in rrule and rdate, the length/duration is
                #taken from rdate if rdate specifies a duration
                if type(rdates[0])==type([]):
                    start_rdates = [start for [start,end] in rdates ]
                    t_res = [start for start in t_res if start.replace(tzinfo=UTC) not in start_rdates]
                    for occur in rdates:
                        [start,end] =occur
                        nslot = self._get_number_slots(start,end,slot_dur)
                        for slotincrement in range(1,nslot):
                            res_slots_rdate.append(start+slot_dur*slotincrement)
                    res_slots_rdate+=start_rdates
                    res_slots_rdate = sorted(res_slots_rdate)

                else:
                    #FIXME: bug
                    #BUG: bug
                    #below will crash if RDATE has a bad value as the list will have a 'None'
                    t_res = t_res + [val for val in rdates if val not in t_res and val>=tmp_event["DTSTART"] and  val>=WindowStart and val<WindowEnd]
                self._log("319 days rdate", [rdates])
            if len(exdates)>0:
                #remove from lisst_dates any date in exdates
                #
                #FIXME: below needs to be made robust on combination of date / date-time naive / date-time aware on both t_res and exdates
                if not self._type_date(exdates[0])==self._type_date(t_res[0]):
                    t_res = [self._from_FloatingTime2TZ(val, UTC) for val in t_res if self._from_FloatingTime2TZ(val, UTC) not in exdates]
                else:
                    t_res = [val for val in t_res if val not in exdates]

            
            res_slots = []
            dtstart = tmp_event["DTSTART"]
            dtend = tmp_event["DTEND"]
            nslot = self._get_number_slots(dtstart,dtend,slot_dur)
            for occurence_start in t_res:
                for slotincrement in range(1,nslot):
                    res_slots.append(occurence_start+slot_dur*slotincrement)
            #FIXME: here add code for get_instances or get_slots
            t_res += res_slots
            t_res += res_slots_rdate
            t_res = sorted(t_res)

            
            self._log("temp 1186: self.events_instances:",[self.events_instances])
            for t_date in t_res:
                self._log("adding events description for",[[t_date,summary,tmp_event["UID"]["val"]]])
                if len(self.events_instances)==0:
                    #if events_instances is empty
                    self.events_instances=[[t_date,summary,tmp_event["UID"]["val"]]]
                else:
                    #if already instances in the list
                    self.events_instances.append([t_date,summary,tmp_event["UID"]["val"]])
        self._log("*****************self.events_instances returned from _flatten",[self.events_instances])
    def _flatten_rrule(self,event,WindowStart,WindowEnd):
        """ where the actual algorithm for unrolling the rrule lies  
        
        also compute day instances when dtend>dtstart"""
        #@param event:the event with python data type to be processed
        #@param start:the first date from which this event should be displayed (note the greater of calendar start and event start will be used
        #@param end: optionnal parameter to decide until when the event should be displayed (note the earlier from this and calendar end will be used   
        #@param dates: list of days i.e. [datetime, datetime,...] of days where this event will occur 
        #@param list_dates: list of days i.e. [datetime, datetime, ...] of days where this event will occur
        #TODO: add handling of bycal=GREG, LUN-CHIN, ORTH
        #TODO: add handling of byeasterday = +/- integer
#        [dtstart,dtend,rules, summary,uid,rdates,exdates] = event
        dtstart = event["DTSTART"]
        dtend = event["DTEND"]
        if "RRULE" in event:
            rules = event["RRULE"]
        else:
            rules = []
        if "SUMMARY" in event:
            summary = event["SUMMARY"]
        else:
            summary = ""
        
        self._log("flatten rule, dtstart is:",[dtstart],0)
        increment = "NONE"
        check_dow = False
        check_week = False
        check_doy = False
        check_setpos = False
        make_dow_list = False
        make_dom = False
        make_week = False
        dow ={'MO': [0],'TU': [0],"WE":[0],"TH":[0],"FR":[0],"SA":[0],"SU":[0]}
        setposlist = []
        list_dates = []
        dates = []
        dom_index = []
        tmp_dates = []
        count = 0
        MaxCount = 0
        days_step_size = 1
        weeks_step_size = 1 
        month_step_size = 1
        year_step_size = 1
        event_start = dtstart
        event_end = WindowEnd #FIXME: check why not DTEND?!?!? also do we need to keep test at the end ?!?!? line 1283
        #here we generate the list of dates for all loaded cals
        self._log("227 rules are:",[rules])
        
        years = [event_start.year]
        months = [event_start.month]
        weeks = [self._isoCW(event_start.year, event_start.month, event_start.day)]
        days = [event_start.day]
        wkst = "MO"
        step_size = 1

        first_dom = 1
        last_dom = 31
        
        month_start = 1
        month_end = 12

        t_date = dtstart

        if len(rules)<=0:
            #FIXME: need to change this if / else and remove it
            pass
        else:
            #switch between absolute computing and relative computing
            #if absolute: generate list
            #if relative
            #if len(years)>1:
            #    months = self._mklist(1, 12)
            #else:
            #    months = self._mklist(dtstart.month,dtend.month)
            #
            if "FREQ" in rules:
                if "INTERVAL" in rules:
                    step_size = int(rules["INTERVAL"])
                if rules["FREQ"] == "YEARLY":
                    increment = "YEAR"
                    year_step_size = step_size
                if rules["FREQ"] == "MONTHLY":
                    increment = "MONTH"
                    month_start = event_start.month
                    month_step_size = step_size
                if rules["FREQ"] == "WEEKLY":
                    make_week = True
                    make_dom = True
                    check_week = True
                    increment = "WEEK"
                    first_dom = event_start.day
                    month_start = event_start.month
                    weeks_step_size = step_size
                if rules["FREQ"] == "DAILY":
                    increment = "DAY"
                    first_dom = event_start.day
                    month_start = event_start.month
                    make_dom = True
                    self._log("277 make dom",[make_dom])
                    days_step_size = step_size
                if "COUNT" in rules:
                    MaxCount = rules["COUNT"]
                if "BYMONTH" in rules:
                    months = rules["BYMONTH"]
                if "BYWEEKNO" in rules:
                    weeks = rules["BYWEEKNO"]
                    check_week = True
                if "BYMONTHDAY" in rules:
                    dom_index = rules["BYMONTHDAY"]
                    make_dom = True
                if "BYDAY" in rules:
                    dow = rules["BYDAY"]
                    make_dow_list = True
                    check_dow = True
                    if increment == "YEAR" and ("BYMONTH" not in rules):
                        months = self._mklist(1, 12)
                if "BYYEARDAY" in rules:
                    doy = rules["BYYEARDAY"]
                    increment = "DAY"
                    make_dom = True
                    check_doy = True
                if "BYSETPOS" in rules:
                    check_setpos = True
                    make_dow_list = True
                    setposlist = rules["BYSETPOS"]
                if "WKST" in rules:
                    wkst = rules["WKST"]
            if "UNTIL" in rules:
                event_end = rules["UNTIL"]
            if make_dow_list == True:
                days = self._mklist(1, 31)
            #@param lday:  is the list of days matching dow before filtering by indexes
            
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |          |SECONDLY|MINUTELY|HOURLY |DAILY  |WEEKLY|MONTHLY|YEARLY|
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |BYMONTH   |Limit   |Limit   |Limit  |Limit  |Limit |Limit  |Expand|
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |BYWEEKNO  |N/A     |N/A     |N/A    |N/A    |N/A   |N/A    |Expand|
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |BYYEARDAY |Limit   |Limit   |Limit  |N/A    |N/A   |N/A    |Expand|
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |BYMONTHDAY|Limit   |Limit   |Limit  |Limit  |N/A   |Expand |Expand|
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |BYDAY     |Limit   |Limit   |Limit  |Limit  |Expand|Note 1 |Note 2|
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |BYHOUR    |Limit   |Limit   |Limit  |Expand |Expand|Expand |Expand|
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |BYMINUTE  |Limit   |Limit   |Expand |Expand |Expand|Expand |Expand|
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |BYSECOND  |Limit   |Expand  |Expand |Expand |Expand|Expand |Expand|
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |BYSETPOS  |Limit   |Limit   |Limit  |Limit  |Limit |Limit  |Limit |
#   +----------+--------+--------+-------+-------+------+-------+------+
#      Note 1:  Limit if BYMONTHDAY is present; otherwise, special expand
#               for MONTHLY.
#
#      Note 2:  Limit if BYYEARDAY or BYMONTHDAY is present; otherwise,
#               special expand for WEEKLY if BYWEEKNO present; otherwise,
#               special expand for MONTHLY if BYMONTH present; otherwise,
#               special expand for YEARLY.
            
            #******** END OF CONFIGURATION, NOW RUNNING
            
            lday = {}
            self._log("years months weeks days",[years,months,weeks,days,event_start,event_end])
            self._log("checks are: dow, week,doy,setpos",[check_dow,check_week,check_doy,check_setpos])
            if month_step_size > 12:
                years = self._mklist(event_start.year, event_end.year,month_step_size/12+1)
            else:
                years = self._mklist(event_start.year, event_end.year,year_step_size)
            self._log("years months weeks days",[years,months,weeks,days,event_start,event_end])

            for year in years:
                if (increment == "MONTH" or increment == "DAY" or increment == "WEEK") and not ("BYMONTH" in rules):
                    months = self._mklist(month_start, month_end, month_step_size)
                    self._log("months updated:",[months])
                if make_week == True:
                    #make here list of week numbers which are to be used
                    week0_num = self._isoCW(year,month_start,first_dom,wkst)
                    weeks = self._mklist(week0_num, 53, weeks_step_size)
                    self._log("weeks updated:",[weeks])
                    if not ("BYDAY" in rules):
                        #if BYDAY not specified add the DOW from DTSTART
                        dow = {}
                        t_dow = self._icalDOW(date(year, month_start, first_dom))
                        dow[t_dow] = [0]
                        self._log("379 make week list:\tyear,month_start,first_dom,wkst,weeks\n",[year,month_start,first_dom,wkst,weeks,dow],1)
                for month in months:
                    if make_dom == True:
                        last_dom = self._last_dom(year, month)
                        tmp_days = self._mklist(first_dom, last_dom,days_step_size)
                        days = []
                        if len(dom_index)>0:
                            #we enter here if dom_index has some content i.e. if the bymonthday was set in the rule
                            for index in dom_index:
                                if index>0:
                                    index = index -1
                                self._log("line 823 days, tmp_days, index",[days,tmp_days,index])
                                if index<len(tmp_days):
                                    #case where DOM is > length of month
                                    days.append(tmp_days[index])
                        else:
                            #else by default all day of month are considered
                            days = tmp_days
                    days0 = days[0]
                    cw = self._isoCW(year, month, days0, wkst)
                    lcw = cw
                    self._log("305 days month year",[days,month,year])
                    for day in days:
                        #HERE we start ploding through the days of the month and checking for all of them
                        #if they exist (feb 29th), then if they are in the good week number, then if they have the right DOW (monday, ...)
                        dateExist = True
                        good_date = True
                        try:
                            if type(datetime(year,month,days0))==type(dtstart):
                                t_date = datetime(year,month,days0,dtstart.hour,dtstart.minute,dtstart.second)
                            else:
                                t_date = date(year,month,days0)
                            delta = timedelta(days = day-days0)
                            t_date +=delta
                        except ValueError:
                            #this is in case days0 is not a valid date of month for the given year/month
                            dateExist = False 
                            #FIXME: check if could be better placed
                            self.Validator("3.3.10_18")                       
                        if (dateExist == True) and (t_date.month==month):
                            if check_week == True:
                                cw = self._isoCW(year,month,day,wkst)
                                self._log("cw , y m d,wkst",[cw,year,month,day,wkst])
                                if (cw not in weeks) and (cw>=lcw):
                                    #check if cw is a good week number
                                    #if cw is not in the list need to make sure we havn't gone round the week number back to 1 while still same year
                                    good_date = False
                                    self._log("381 good date is false because cw not in weeks (last cw)",[cw,weeks,lcw])
                                elif lcw>cw:
                                #    #here is the case where the week numbering is back to 1 but we are still at the end of year
                                    if 53 in weeks:
                                        good_date = True
                                    else:
                                        good_date = False
                                    self._log("460 corner case week number:good_date, cw, lcw,weeks",[good_date,cw, lcw, weeks])
                            #if check_dow==True:
                            tdate_dow = self._icalDOW(t_date)
                            if tdate_dow not in dow:
                                good_date = False
                                self._log("387 good date false because of dow",[t_date,tdate_dow,dow])
                            if check_doy==True:
                                if t_date.timetuple().tm_yday in doy:
                                    good_date = True
                                    self._log ("424 good date false because of doy",[t_date,check_doy,t_date.timetuple().tm_yday,doy])
                                else:
                                    good_date = False
                                    self._log ("424 good date false because of doy",[t_date,check_doy,t_date.timetuple().tm_yday,doy])
                            if good_date == True:
                                lcw = cw
                                #last good date is used for computing next starting date when rolling over
                                last_good_date = t_date
                                if tdate_dow in lday:
                                    lday[tdate_dow].append(t_date)
                                else:
                                    lday[tdate_dow] = [t_date]
                                self._log("396 append date:",[t_date,lday])
                        if increment == "DAY":
                            self._log("552 - about to enter _sublist filtering on DAY increment: last_good_date, days_step_size",[last_good_date, days_step_size])
                            list_dates = self._sublist(lday,dates,summary,dow,check_setpos,setposlist,list_dates)
                            dates = []
                            lday = {}
                            t_date = last_good_date +timedelta(days = days_step_size)
                            if t_date.month>month:
                                first_dom = t_date.day
                                self._log("380 - next first dom",[first_dom,month,year])
                            elif t_date.year>year:
                                first_dom = t_date.day
                                month_start = t_date.month    
                                self._log("441: roll-out year on daily freq first_dom, month_start",[first_dom, month_start, t_date.year])                            
                    if increment == "WEEK":
                        first_dom = 1
                    if increment == "MONTH":
                        #enter here to empty the lday list and fill the list_dates
                        self._log("about to enter _sublist filtering on MONTH increment:\t lday,dates,dow,check_setpos_setposlit,list_dates\n",[lday,dates,summary,dow,check_setpos,setposlist,list_dates])
                        list_dates = self._sublist(lday,dates,summary,dow,check_setpos,setposlist,list_dates)
                        month_start = (months[-1]+month_step_size) % 12
                        dates = []
                        lday = {}
                if increment == "YEAR" or increment == "WEEK":
                    self._log("about to enter _sublist filtering on YEAR increment:\t lday,dates,dow,check_setpos_setposlit,list_dates\n",[lday,dates,summary,dow,check_setpos,setposlist,list_dates])
                    list_dates = self._sublist(lday,dates,summary,dow,check_setpos,setposlist,list_dates)
                    dates = []
                    lday = {}
                    if increment == "WEEK":
                        self._log("584: next first dom last_good_date, weeks_step_size",[last_good_date ,weeks_step_size])
                        #0.72b fixed
                        #before:
                        t_date = last_good_date +timedelta(weeks = weeks_step_size)
                        #after:
                        #need to compute last day of week - first day of week days ofset
                        
                        maxDOW = 0
                        minDOW = 7
                        for dw in dow:
                            dwi = weekday_map[dw]
                            if dwi<minDOW:
                                minDOW = dwi
                            if dwi>maxDOW:
                                maxDOW = dwi
                        daysgap = 7-(maxDOW-minDOW)
                        t_date = last_good_date +timedelta(weeks = weeks_step_size-1)+timedelta(days = daysgap)
                        #end 0.72b->0.72c fix
                        if t_date.year>year:
                            first_dom = t_date.day
                            month_start = t_date.month
                            self._log("584: next first dom",[first_dom,month_start,t_date.year])
                #month_start = 1
        self._log("list of dates before the validation: list_dates and tmp_dates \n",[list_dates,tmp_dates])
        self._log("interval dates: event_start,event_end,self.OccurencesWindowStartDate,self.OccurencesWindowEndDate \n",[event_start,event_end,self.OccurencesWindowStartDate,self.OccurencesWindowEndDate])
        
        if dtstart not in list_dates:
            list_dates.append(dtstart)
            self._log("DTSTART added to list", [dtstart,list_dates])

        list_dates = sorted(list_dates)

        for t_date in list_dates:
            #FIXME: need to account here for event with start<WindowStart but start+duration>WindowStart
            #FIXME: need to account also for dual case with WindowEnd
            if t_date>=event_start and  t_date>=WindowStart and t_date<WindowEnd and t_date<=event_end:
                self._log("Maxcount",[MaxCount, t_date])
                if MaxCount >0:
                    #if we count the number of recurrencies then only add dates as long as below max number
                    count = count+1
                    if count<= MaxCount:
                        self._log("count, MaxCount",[count,MaxCount, t_date])
                        tmp_dates.append(t_date)
                else:
                    #if we are not counting the number of reccurencies then just keep it
                    tmp_dates.append(t_date)
        list_dates = tmp_dates
        
        return list_dates
    def add_year_months(self,date,years,months,InstanceAccurate = True):
        """"will add nMonths to the date, if not 100% accurate it will either compromise the date (like 31 jan +1 mo = 28 fev InstanceAccurate
        2012/2/29 + 1 year = "Na" for DateAccurate
        """
        months = months % 12
        years = years + months / 12
        
        year = date.year
        month = date.month
        new_date = None
        try:
            new_date= date(year+years,month+months)
        except:
            pass
        
        return new_date
    def _propval_line_split(self,LineContent,LineNumber =0):
        """ takes a line and splits in property, parameters and value
        
        will also secure that the property is a valid property
        """
        self._log("line loader", [LineContent], 0)
        if LineContent.find(":")>0:
            [propnparam,value]=[LineContent.split(":")[0], ":".join(LineContent.split(":")[1:])]
            if propnparam.find(";")>0:
                [prop,param]=[propnparam.split(";")[0],propnparam.split(";")[1:]]
            else:
                [prop,param]=[propnparam,[]]
        else:
            if LineNumber ==0:
                LineNumber = ""
            else:
                LineNumber = str(LineNumber)           
            self.Validator("3.1_2", line_count = LineNumber, line = LineContent, level = 0)#raise Exception("VCALENDAR WARNING","Expected a semi-column ':' %s : %s"%(LineNumber,LineContent))
        self._log("line loaded", [prop,param,value], 0)
        if prop not in RFC5545_Properties:
            if not prop.find("X-") == 0:
                self.Validator("8.3.2_1", line_count = LineNumber, line = LineContent, level = 0)
        return [prop,param,value]
    def _last_dom(self,year,month):
        day = datetime(year,month,1)
        for i in range(1,32):
            delta = timedelta(days = i)
            new = day + delta
            if new.month != day.month:
                return i
    def _icalDOW(self,date):
        "returns DOW ical way from date (MO, TU, ..."
        return date.strftime("%a")[-3:-1].upper()
    def _isoCW(self,year, month,day,wkst="MO",iso=True):
        """returns the iso week number of the passed date, 0 if invalid date
        
        CW is week number of year/month/day
        CW is set to iso week number (ISO8601
        wkst is currenlty used start of week
        index is index of day within week (first value irrelevant, just needs to remain consistant)
        if day.index > wkst.index 
         if day is after wkst but before monday (monday as we use iso8601 calendar)
         and day is before monday
         then CW -=1
        
        examples:
        2008,dec,29, with wkst="MO" the weeknumber is 1 (day is monday and 4 days ,
        
        Dec29    |    Dec30    |    Dec31    |    Jan1    |    Jan2    |    Jan3    |    Jan4
        Mo            Tuesday        wednesday    Thursday    Friday        Saturday    Sunday
        ISOWK=1        ISOWK=1        ISOWK=1    ISOWK=1        ISOWK=1    ISOWK=1        ISOWK=1
        >=    Y        Y


       [2009,1,5,"MO",2,0],
       [2012,1,18,"TH",3,3]]
        
        """
        
        #2005-01-01 is 2004-W53-6
        CW = 0
        dow = ["TU","WE","TH","FR","SA","SU","MO"]
        try:
            CW= datetime(year,month,day).isocalendar()[1]
            #if dow is between wkst and monday then CW-=1 else keep CW, "MO" was put end of list so if wkst = MO then no change
            if (dow.index(self._icalDOW(date(year,month,day)))-dow.index(wkst)>=0) and (dow.index(wkst)<dow.index("MO")) and (dow.index(self._icalDOW(date(year,month,day))) < dow.index("MO")):
                    CW -= 1
        except ValueError:
            #this is in case days0 is not a valid date of month for the given year/month
            CW = 0
        return CW
    def _get_number_slots(self,dtstart,dtend,slot_duration):
        """ will return the number of slots (defined by slot duration) between dtstart (inclusive) and dtend (not inclusive)
        
        handles timezones and leap seconds
        """
        delta = dtend-dtstart
        delta_days = delta.days
        #FIXME: here converts number of days in seconds
        delta_seconds = delta_days *86400
        delta_seconds = delta_seconds+delta.seconds
        slot_dur_seconds = slot_duration.days*86400 + slot_duration.seconds
        nb_slots = delta_seconds/slot_dur_seconds
        return nb_slots
    def _to_FloatingTime(self,dt):
        """ takes a datetime object with tzinfo and returns a naive datetime with time converted to UTC """
        
        #FIXME: need to uncomment below
#        timedelta = dt.tzinfo.DST()
        
        dtFloat = datetime(year = dt.year, 
                        month = dt.month,
                        day = dt.day,
                        hour = dt.hour,
                        minute = dt.minute,
                        second = dt.second
                        )
        
        return dtFloat
    def _from_FloatingTime2TZ(self,dt,TZ):
        """ takes a TZ naive-datetime (floating) and converts to TZ-aware datetime """
        #FIXME: need to uncomment below
#        timedelta = dt.tzinfo.DST()

        
        dtTZ = datetime(year = dt.year, 
                        month = dt.month,
                        day = dt.day,
                        hour = dt.hour,
                        minute = dt.minute,
                        second = dt.second,
                        tzinfo = TZ)
        
        return dtTZ
       
    def _type_date(self,dt):
        typeDT = "DATETIME-TZ"
        if type(dt)==type(datetime(2013,2,6).date()):
            typeDT= "DATE"
        if type(dt) == type(datetime(2013,2,6)):
            try:
                if dt>datetime(2013,2,6):
                    typeDT= "DATETIME-FLOAT"
                elif dt<=datetime(2013,2,6):
                    typeDT= "DATETIME-FLOAT"
                else:
                    pass                    
            except:
                typeDT = "DATETIME-TZ"
        return typeDT
    def _sublist(self,lday,dates,summary,dow,check_setpos,setposlist,list_dates):
        """ used in flatten rrule to accelerate by only looking at some dates within a list"""
        self._log("347 list_Dates",[list_dates])
        self._log("348 lday",[lday])
        self._log("349 setposlist",[setposlist])
        self._log("350 dow",[dow])
        #same as above for the year
        for dowi in lday:
            if 0 in dow[dowi]:
                for date in lday[dowi]:
                    dates.append(date)
            else:
                for dow_index in dow[dowi]:
                    if dow_index>0:
                        dow_index -=1
                    if len(dates)==0:
                        dates = [lday[dowi][dow_index]]
                    else:
                        dates.append(lday[dowi][dow_index])
        self._log("356 dates before check_setpos",[dates])
        dates = sorted(dates)
        if check_setpos == True:
            dates_pos = []
            self._log("363 dates sorted", [dates])
            for setpos in setposlist:
                if setpos>0:
                    setpos = setpos-1
                dates_pos.append(dates[setpos])
            dates = dates_pos
        if len(list_dates)==0:
            list_dates = dates
        else:
            for date in dates:
                list_dates.append(date)
        self._log("413: list_dates at end of _sublist",[list_dates])
        return list_dates
    def get_event_instances(self,start=datetime.today().strftime("%Y%m%d"),end=datetime.today().strftime("%Y%m%d"),count=-1):
        """Returns an array of events with dates, uid, and summary
        
        The function returns the array of events within a given date window (defined by start and end),
        should only a certain number of events be needed either from a start date or to an end date the
        missing date should be set to Null
        """
        self.OccurencesWindowStartDate = datetime.strptime(start,"%Y%m%d")
        self.OccurencesWindowEndDate = datetime.strptime(end,"%Y%m%d")+timedelta(days =1)
        self.parse_loaded()
        self._flatten()
        import operator
        try:
            self.events_instances = sorted(self.events_instances,key = lambda dateeve: operator.itemgetter(0).date() if type(operator.itemgetter(0)) == type(datetime.now()) else operator.itemgetter(0) )
        except:
            print self.events_instances
#            print self.events_instances[0][0]
#            print type(self.events_instances[0][0])
#            print datetime(2015,1,1,11,11)
#            print datetime(2015,1,1,11,11).date()
#            print datetime(2015,1,1,11,11).date().date()
#            print self.events_instances[0][0].date()
            raise
        return self.events_instances

    def Gen_iCalendar(self,append = False,method=""):
        """ takes the self.dVCALENDAR and generates an icalendar string """
        
#        if not append:
#            self._reset()

        vevent_write = {
                        "TEXT": self.vevent.string_write,
                        "DATE-TIME": self.vevent.date_write,
                        "INTEGER":self.vevent.integer_write,
                        "DURATION":self.vevent.duration_write,
                        "CAL-ADDRESS":self.vevent.cal_address_write,
                        "RECUR":self.vevent.rrule_write
                        }
        
        sCalendar = "BEGIN:VCALENDAR"+CRLF
        if not "VERSION" in self.dVCALENDAR:
            self.dVCALENDAR["VERSION"]="2.0"
        if not "PRODID" in self.dVCALENDAR:
            self.dVCALENDAR["PRODID"]="pyICSParser@1-annum.com"
        if (not "METHOD" in self.dVCALENDAR) and method in RFC5546_METHODS:
            self.dVCALENDAR["METHOD"]=method

        for Prop in self.dVCALENDAR:
            #here add calendar properties
            param = ""
            if "param" in self.dVCALENDAR[Prop]:
                for p in self.dVCALENDAR[Prop]["param"]:
                    param +=p+";"
            else:
                param = ""
            if not "val" in self.dVCALENDAR[Prop]:
                propvalue = self.dVCALENDAR[Prop]
            else:
                propvalue = self.dVCALENDAR[Prop]["val"]
            sCalendar+=Prop+param+":"+propvalue+CRLF
        
        for event in self.events:
            if "UID" not in event:
                event["UID"]="FIXMEUID"
            if "DTSTAMP" not in event:
                event["DTSTAMP"]={"param":"","val":datetime.now()}
            sCalendar += "BEGIN:VEVENT"+CRLF
            for Prop in event:
                if not "val" in event[Prop]:
                    propvalue = event[Prop]
                else:   
                    propvalue = event[Prop]["val"]
#                newline = Prop+":"+vevent_write[Prop](propvalue)+CRLF
                #RFC5545_Properties[Prop] will give the relevant type
                #vevent_write["TEXT"] will call self.vevent.string_write(_
                if Prop in RFC5545_Properties:
                    newline = Prop+":"+vevent_write[RFC5545_Properties[Prop]](propvalue)+CRLF
                elif Prop.find("X-")==0:
                    #write code here for adding X-properties
                    pass
                else:
                    print "trying to add invalid property: %s"%(Prop)
                sCalendar+= self.vevent.line_wrap(newline)
                newline =""
            sCalendar += "END:VEVENT"+CRLF
            
        sCalendar += "END:VCALENDAR"+CRLF
        return sCalendar
    def updateEvent(self,uid,updatelist):
        """ will update self.events[uid] with the new value for the properties in updatelist"""
        
        for event in self.events:
            if event["UID"]["val"]==uid:
                for newval in updatelist:
                    event[newval]=updatelist[newval]
                if "SEQUENCE" in event:
                    event["SEQUENCE"]["val"]=event["SEQUENCE"]["val"]+1
    def isCalendarFileCompliant(self,iCalendarFile,_ReportNonConformance = True):
        """ will load and parse the iCalendar File and display errors """
        self.conformance = _ReportNonConformance
        self.vevent.conformance = _ReportNonConformance
        self.local_load(iCalendarFile,conformance = _ReportNonConformance)
        retval = False
        self.parse_loaded()
        if len(self.lSCM)==0 and len(self.vevent.lSCM)==0:
#            print "Congratulations your iCalendar file is 100% compliant to RFC5545"
            retval = True
        else:
            pass
#            self.dSCM = sorted(self.dSCM)
        return retval
    def isCalendarStringCompliant(self,iCalendarFile,_ReportNonConformance = True):
        """ will load and parse the iCalendar File and display errors """
        
        #FIXME: need to get code below adjusted
        self.conformance = _ReportNonConformance
        self.vevent.conformance = _ReportNonConformance
        self.string_load(iCalendarFile,conformance = _ReportNonConformance)
        retval = False
        self.parse_loaded()
        if len(self.lSCM)==0 and len(self.vevent.lSCM)==0:
#            print "Congratulations your iCalendar file is 100% compliant to RFC5545"
            retval = True
        else:
            pass
#            self.dSCM = sorted(self.dSCM)

        return retval