LOGGING = {
    "LOG_LEVEL": "DEBUG",
    "SETUP_LOGGERS": [
        "NucleusApp"
    ],
    "REPORTS_STORAGE": None,
    "HANDLERS": [
        {
            "HANDLER": "logging.StreamHandler",
            "FORMATTER": '%(asctime)s (%(filename)s:%(lineno)d %(threadName)s) %(levelname)s - %(name)s: "%(message)s"'
        }
    ]
}
