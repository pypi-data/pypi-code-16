import logging
import sys
import yaml

def setupLogging(logging_level, logfile):
    root = logging.getLogger()
    root.setLevel(logging_level)

    logging.basicConfig(filename=logfile, level=logging_level)

    # ch = logging.StreamHandler(sys.stdout)
    # ch.setLevel(logging_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # root.setFormatter(formatter)
    # root.addHandler(ch)
    return root;

def loadConfiguration(externalizedFilename, defaults):
    try:
        with open(externalizedFilename, 'r') as ymlfile:
            configuration = yaml.load(ymlfile)

        logging.info('Configuration loaded.')
    except IOError as e:
        logging.warning(e)
        try:
            logging.info('Initialize new configuration ...')
            with open(externalizedFilename, 'w') as ymlfile:
                configuration = yaml.dump(defaults, ymlfile, default_flow_style=False)
            logging.info('Default configuration created.')
        except IOError:
            raise EnvironmentError('Configuration file mq could not created.')
    return configuration
