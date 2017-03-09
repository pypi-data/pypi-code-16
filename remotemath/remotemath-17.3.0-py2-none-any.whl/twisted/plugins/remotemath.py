from twisted.application.service import ServiceMaker

serviceMaker = ServiceMaker(
    "Remote math service",
    "remotemath.service",
    "Web service to multiply and negate",
    "remotemath",
)
