##############################
# Classes de Telecomunicação #
##############################


class SubscriberType(object):
    COMERCIAL = 1
    PUBLIC_POWER = 2
    RESIDENTIAL = 3
    PUBLIC_PHONE = 4
    SEMI_PUBLIC_PHONE = 5
    HUGE_CLIENT = 6


class UtilizationType(object):
    TELEPHONY = 1
    DATA_COMMUNICATION = 2
    CABLE_TV = 3
    INTERNET_ACCESS = 4
    MULTIMIDIA = 5
    OTHERS = 6


##


class Model(object):
    eletric_energy = 6
    communication = 22
    telecommunication = 23


class Situation(object):
    CANCELLED = "S"
    NOT_CANCELLED = "N"
