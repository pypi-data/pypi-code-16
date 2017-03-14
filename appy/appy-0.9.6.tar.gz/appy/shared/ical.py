'''Module for managing iCal files'''

# ------------------------------------------------------------------------------
class ICalConfig:
    '''How to map Appy object to iCal attributes'''
    fields = ('DTSTART', 'DTEND', 'UID', 'CREATED', 'DESCRIPTION',
              'LAST_MODIFIED', 'STATUS', 'SUMMARY')
    appyFields = {'DTSTART': 'date', 'DTEND': 'endDate', 'UID': 'id',
                  'CREATED': 'created', 'LAST_MODIFIED': 'modified',
                  'SUMMARY': 'title'}
    defaultValues = {'STATUS': 'CONFIRMED',
                     'DTEND': ':self.getEndDate(startDate)'}

    def __init__(self):
        for name in self.fields:
            setattr(self, name, self.appyFields.get(name))

# ------------------------------------------------------------------------------
class ICalExporter:
    '''Allows to to produce a .ics file (iCal)'''

    def __init__(self, name, config=None, dateFormat='%Y%m%dT%H%M00'):
        # The name of the file that will be created
        self.name = name
        self.config = config or ICalConfig()
        self.dateFormat = dateFormat
        # Open the result file
        self.f = file(name, 'w')

    def write(self, s):
        '''Writes content p_s into the result'''
        self.f.write('%s\n' % s)

    def start(self):
        '''Dumps the start of the file'''
        self.write('BEGIN:VCALENDAR\nPRODID:Appy\nVERSION:2.0\n' \
                   'CALSCALE:GREGORIAN\nMETHOD:PUBLISH')

    def end(self):
        '''Dumps the end of the file'''
        self.write('END:VCALENDAR')
        self.f.close()

    def getValue(self, value):
        '''Returns the iCal value given the Appy p_value'''
        if not isinstance(value, basestring): # It is a date
             res = value.strftime(self.dateFormat)
        else:
            res = value
            if res and ('\n' in res):
                # Truncate the value if a carriage return is found
                res = res[:res.index('\n')]
        return res

    def getEndDate(self, startDate):
        '''When no end date is found, create one, 1 hour later than
           p_startDate'''
        return self.getValue(startDate + (1.0/24))

    def event(self, obj):
        '''Dumps a calendar event in the file, from p_obj'''
        w = self.write
        w('BEGIN:VEVENT')
        config = self.config
        # We must remember the start date
        startDate = None
        for icalName in self.config.fields:
            # Get the corresponding Appy field
            appyName = getattr(config, icalName, None)
            # Try to get the value on p_obj
            value = None
            if appyName:
                value = getattr(obj, appyName)
                # Remember the start date
                if icalName == 'DTSTART':
                    startDate = value
            # If not found, try to get it from default values
            if (value == None) and (icalName in config.defaultValues):
                default = config.defaultValues[icalName]
                if default.startswith(':'):
                    # It is a Python expression
                    value = eval(default[1:])
                else:
                    value = default
            # Ensure the value is a string
            value = value or ''
            # Get the name of the iCal attribute
            name = icalName.replace('_', '-')
            # Get the value of the iCal attribute
            w('%s:%s' % (name, self.getValue(value)))
        w('END:VEVENT')
# ------------------------------------------------------------------------------
