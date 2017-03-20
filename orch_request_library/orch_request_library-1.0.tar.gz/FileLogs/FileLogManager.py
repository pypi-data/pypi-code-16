import logging.config
import re
import os
import json
from inspect import stack, getmodule
from django.conf import settings


class FileLogManager:
    def setup_logging(
            default_path='FileLogs\logfilesettings.json',
            default_level=logging.DEBUG,
            env_key='LOG_CFG'
    ):
        """Setup logging configuration"""

        APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(APP_PATH, default_path)

        #check LOG_ROOT setting exists in settings.py
        if hasattr(settings, 'LOG_ROOT'):
            log_folder = settings.LOG_ROOT


        #if not, set the default location
        else:
            log_folder = os.path.join(APP_PATH, "logs")
            #create a log folder if it doesn't exits

            if not os.path.exists(log_folder):
                os.makedirs(log_folder)


        if os.path.exists(path):
            with open(path, 'rt') as f:
                config = json.load(f)

            #update the config json with the few file location
            file_location = os.path.join(log_folder, config["handlers"]["app_log_handler"]["filename"])
            config["handlers"]["app_log_handler"]["filename"] = file_location

            #load the udpated logging config
            logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=default_level)


    @classmethod
    def write_log_to_file(cls, log_level, log_message, module_name):
        FileLogManager.setup_logging()

        #check whether module_name is provided, if not extract module name from the stack
        if (module_name == ""):
            source = stack()[1]
            module_details = getmodule(source[0])

            #module details format
            # < module 'MODULE_NAME' from '{FILE_PATH}' >
            #using regex to extract the module name
            module_match = re.search("<module '(.+?)' from", str(module_details))



            if module_match:
                module_name = module_match.group(1)

        logger = logging.getLogger(module_name)
        if(log_level=="INFO"):
            logger.info(log_message)
        else:
            logger.debug(log_message)