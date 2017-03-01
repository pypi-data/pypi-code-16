# Copyright 2015 Formation Data Systems, Inc. All Rights Reserved.
#
import json
from fdscli.model.volume.recurrence_rule import Frequency, RecurrenceRule

class RecurrenceRuleConverter(object):
    '''Helper class for marshalling between RecurrenceRule and JSON formatted string.

    The term 'to marshal' means to convert some data from internal to external form
    (in an RPC buffer for instance). The term 'unmarshalling' refers to the reverse
    process. We presume that the server will use reflection to create a Java object
    given the JSON formatted string.
    '''

    @staticmethod
    def to_json( rule ):
        '''Converts ``model.volume.RecurrenceRule`` object into a JSON formatted string.

        We presume that the recipient (a server) uses a package like Gson and passes the type
        literal when deserializing the JSON formatted string.

        Parameters
        ----------
        :type rule: ``model.volume.RecurrenceRule`` object

        Returns
        -------
        :type string
        '''
        d = dict()

        if ( rule is None or rule.is_empty() == True ):
            return json.dumps( d )

        d["FREQ"] = str(rule.frequency)

        if ( rule.byday is not None ):
            d["BYDAY"] = rule.byday

        if ( rule.bymonth is not None ):
            d["BYMONTH"] = rule.bymonth

        if ( rule.byhour is not None ):
            d["BYHOUR"] = rule.byhour

        if ( rule.bymonthday is not None ):
            d["BYMONTHDAY"] = rule.bymonthday

        if ( rule.byyearday is not None ):
            d["BYYEARDAY"] = rule.byyearday

        if ( rule.byminute is not None ):
            d["BYMINUTE"] = rule.byminute 

        result = json.dumps( d )
        return result

    @staticmethod
    def build_rule_from_json( jString ):
        '''Produce a ``model.volume.RecurrenceRule`` object from deserialized server response

        Parameters
        ----------
        :type jString: dict or json-encoded string representing a JSON object

        Returns
        -------
        :type ``model.volume.RecurrenceRule``
        '''
        rule = RecurrenceRule()

        # If given argument not a dict, decode to a dict
        if not isinstance( jString, dict ):
            jString = json.loads( jString )

        if "FREQ" in jString:
            freq_str = jString.pop("FREQ");
            for s in Frequency:
                if s.name == str(freq_str.upper()):
                    rule.frequency = s.name
                    break;

        rule.byday = jString.pop( "BYDAY", None )
        rule.byhour = jString.pop( "BYHOUR", None )
        rule.bymonth = jString.pop( "BYMONTH", None )
        rule.byyearday = jString.pop( "BYYEARDAY", None )
        rule.bymonthday = jString.pop( "BYMONTHDAY", None )
        rule.byminute = jString.pop( "BYMINUTE", None )

        return rule

